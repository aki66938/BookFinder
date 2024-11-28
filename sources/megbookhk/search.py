"""香港美国书店图书搜索模块"""
from typing import Dict, List, Optional
import json
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import re
import os

from config import REQUEST_TIMEOUT
from sources.utils import retry_on_failure, make_request, clean_text, extract_year
from sources.image import process_cover_image

# URL配置
MEGBOOKHK_BASE_URL = 'http://www.megbook.hk'
MEGBOOKHK_SEARCH_URL = 'http://search.megbook.hk/mall/search.jsp'

# 更新请求头
MEGBOOK_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "http://www.megbook.hk/",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache"
}

def extract_book_info(cell) -> Optional[Dict[str, str]]:
    """从单元格中提取图书信息"""
    # 查找所有文本内容
    text = clean_text(cell.get_text())
    if not text:
        return None
        
    # 查找链接
    link = cell.find('a')
    if not link:
        return None
        
    href = link.get('href', '')
    if not href or not href.startswith('http://www.megbook.hk/mall/detail.jsp'):
        return None
        
    # 提取标题 - 移除多余前缀
    title = clean_text(link.get_text())
    if not title:
        title = clean_text(cell.get_text().split('『')[0])
    
    # 清理标题
    title = title.replace('編輯推薦：', '').replace('『簡體書』', '').strip()
    
    # 提取其他信息
    info_text = clean_text(cell.get_text())
    author = ''
    press = ''
    year = ''
    
    if '作者：' in info_text:
        author = info_text.split('作者：')[1].split('出版：')[0].strip()
    if '出版：' in info_text:
        press = info_text.split('出版：')[1].split('日期：')[0].strip()
    if '日期：' in info_text:
        year = extract_year(info_text.split('日期：')[1].split('『')[0].strip())
        
    # 查找封面图片
    img = cell.find('img')
    cover_url = ''
    if img and 'src' in img.attrs:
        cover_url = urljoin(MEGBOOKHK_SEARCH_URL, img.get('src', ''))
        
    # 只返回看起来像图书的结果
    if title and (author or press):
        return {
            'url': href,  # 使用原始的香港美国书店链接
            'title': title,
            'author': author,
            'press': press,
            'year': year,
            'cover_url': cover_url
        }
    return None

@retry_on_failure(max_retries=3)
def search_books(book_name: str) -> List[Dict[str, str]]:
    """
    搜索香港美国书店图书
    
    Args:
        book_name: 要搜索的书名

    Returns:
        包含搜索结果的列表，每个元素是一个字典，包含书籍信息
    """
    try:
        # 构造搜索URL和参数
        params = {
            'range': '',
            'keywords': book_name,
            'searchType': '2',
            'Submit': '搜寻..'
        }
        
        response = make_request(MEGBOOKHK_SEARCH_URL, MEGBOOK_HEADERS, params=params)
        if not response:
            return []
            
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # 查找所有表格
        all_tables = soup.find_all('table')
        
        # 遍历每个表格
        for table in all_tables:
            # 查找所有单元格
            cells = table.find_all('td')
            for cell in cells:
                # 提取图书信息
                book_info = extract_book_info(cell)
                if book_info:
                    # 检查是否为重复结果
                    if not any(b['url'] == book_info['url'] for b in results):
                        results.append(book_info)
        
        # 过滤掉没有标题或作者的结果
        filtered_results = [
            book for book in results 
            if book.get('title') and book.get('author') and 
            not book['title'].startswith('詳情') 
        ]
        
        return filtered_results[:10]  # 限制返回前10条结果
        
    except Exception as e:
        return []

@retry_on_failure(max_retries=3)
def get_book_details(url: str) -> Optional[Dict[str, str]]:
    """
    获取图书详细信息
    
    Args:
        url: 图书详情页URL

    Returns:
        包含图书详细信息的字典
    """
    try:
        response = make_request(url, MEGBOOK_HEADERS)
        if not response:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        info = {}
        info['url'] = url
        
        # 提取并清理标题 - 使用多种方式
        title = None
        
        # 方法1：从URL参数中提取proID
        pro_id = url.split('proID=')[-1]
        
        # 方法2：尝试从表格中提取
        tables = soup.find_all('table')
        for table in tables:
            # 查找包含书名的单元格
            cells = table.find_all('td')
            for cell in cells:
                text = clean_text(cell.get_text())
                
                # 如果找到包含书名的单元格
                if '『簡體書』' in text:
                    title = text.split('『簡體書』')[1].split('書城自編碼')[0].strip()
                    break
                elif '書名：' in text:
                    title = text.split('書名：')[1].split('\n')[0].strip()
                    break
                elif pro_id in text and '：' in text:
                    # 尝试提取冒号后的内容作为标题
                    parts = text.split('：')
                    if len(parts) > 1:
                        title = parts[1].split('\n')[0].strip()
                        break
            
            if title:
                break
        
        if title:
            # 清理标题
            title = title.replace('編輯推薦', '').replace('『簡體書』', '').strip()
            info['title'] = title
        else:
            # 如果还是没有找到标题，使用搜索结果中的标题
            desc_cells = soup.find_all('td', {'class': 'desc'}) or soup.find_all('td', {'bgcolor': '#FFFFFF'})
            for cell in desc_cells:
                text = clean_text(cell.get_text())
                if text and '『簡體書』' in text:
                    title = text.split('『簡體書』')[1].split('書城自編碼')[0].strip()
                    if title:
                        info['title'] = title
                        break
        
        # 提取基本信息
        info_text = clean_text(soup.get_text())
        
        # 使用更精确的提取方法
        patterns = {
            'author': [
                r'作者[：:]\s*([^出版\n]+?)(?=出版|$)',
                r'作者[：:]\s*([^\n]+?)(?=\s|$)',
                r'作者[：:]\s*([^國際書號]+)國際書號'
            ],
            'press': [
                r'出版社[：:]\s*([^出版日期\n]+?)(?=出版日期|$)',
                r'出版社[：:]\s*([^\n]+?)(?=\s|$)'
            ],
            'year': [
                r'出版日期[：:]\s*(\d{4})[年-]?(\d{1,2})?',
                r'出版日期[：:]\s*(\d{4})'
            ],
            'isbn': [
                r'ISBN[：:]\s*(\d{13}|\d{10})',
                r'國際書號[（(]ISBN[）)][：:]\s*(\d{13}|\d{10})',
                r'國際書號[：:]\s*(\d{13}|\d{10})'
            ],
            'pages': [
                r'頁數[：:]\s*(\d+)',
                r'頁數/字數[：:]\s*(\d+)'
            ],
            'price': [
                r'售價[：:]\s*(HK\$\s*[\d.]+)',
                r'定價[：:]\s*(HK\$\s*[\d.]+)'
            ]
        }
        
        # 尝试所有模式
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, info_text)
                if match:
                    if key == 'year' and len(match.groups()) > 1 and match.group(2):
                        info[key] = f"{match.group(1)}-{match.group(2)}"
                    else:
                        info[key] = match.group(1).strip()
                    break
        
        # 提取内容简介
        desc_patterns = [
            r'【内容简介】\s*(.*?)(?=【|書城介紹|$)',
            r'內容簡介[：:](.*?)(?=作者簡介|關於作者|書城介紹|$)',
            r'内容简介[：:](.*?)(?=作者简介|关于作者|書城介紹|$)',
            r'簡介[：:](.*?)(?=作者簡介|關於作者|書城介紹|$)'
        ]
        
        for pattern in desc_patterns:
            desc_match = re.search(pattern, info_text, re.DOTALL)
            if desc_match:
                description = clean_text(desc_match.group(1))
                if len(description) > 20:
                    # 清理掉网站相关内容
                    description = re.sub(r'書城介紹.*$', '', description, flags=re.DOTALL)
                    description = re.sub(r'Copyright.*$', '', description, flags=re.DOTALL)
                    description = description.strip()
                    if len(description) > 20:
                        info['description'] = description
                        break
        
        # 提取作者简介
        author_patterns = [
            r'【作者简介】\s*(.*?)(?=【|書城介紹|$)',
            r'作者簡介[：:](.*?)(?=內容簡介|書城介紹|$)',
            r'作者简介[：:](.*?)(?=内容简介|書城介紹|$)',
            r'關於作者[：:](.*?)(?=內容簡介|書城介紹|$)',
            r'关于作者[：:](.*?)(?=内容简介|書城介紹|$)'
        ]
        
        for pattern in author_patterns:
            author_match = re.search(pattern, info_text, re.DOTALL)
            if author_match:
                author_intro = clean_text(author_match.group(1))
                if len(author_intro) > 20:
                    # 清理掉网站相关内容
                    author_intro = re.sub(r'書城介紹.*$', '', author_intro, flags=re.DOTALL)
                    author_intro = re.sub(r'Copyright.*$', '', author_intro, flags=re.DOTALL)
                    author_intro = author_intro.strip()
                    if len(author_intro) > 20:
                        info['author_intro'] = author_intro
                        break
        
        # 提取封面图片
        cover_selectors = [
            'img[src*="cover"]',
            'img[src*="book"]',
            'img[alt*="封面"]',
            'img[src*="prod"]'
        ]
        
        for selector in cover_selectors:
            cover_elem = soup.select_one(selector)
            if cover_elem and 'src' in cover_elem.attrs:
                cover_url = cover_elem['src']
                if not cover_url.startswith('http'):
                    cover_url = urljoin(url, cover_url)
                info['cover_url'] = cover_url
                break
        
        # 确保至少有基本信息
        if not info.get('title'):
            return None
            
        return info
        
    except Exception as e:
        return None
