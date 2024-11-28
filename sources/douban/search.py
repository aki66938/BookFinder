"""豆瓣图书搜索模块"""
from typing import Dict, List, Optional
import json
from urllib.parse import quote
from bs4 import BeautifulSoup
import re

from config import HEADERS, REQUEST_TIMEOUT
from sources.utils import retry_on_failure, make_request, clean_text, extract_year
from sources.image import process_cover_image

# URL配置
DOUBAN_BASE_URL = 'https://book.douban.com'
DOUBAN_SEARCH_URL = f'{DOUBAN_BASE_URL}/j/subject_suggest'

@retry_on_failure(max_retries=3)
def search_books(book_name: str) -> List[Dict[str, str]]:
    """
    搜索豆瓣图书
    
    Args:
        book_name: 要搜索的书名

    Returns:
        包含搜索结果的列表，每个元素是一个字典，包含书籍信息
    """
    try:
        # 构造搜索URL
        params = {
            'q': book_name
        }
        response = make_request(DOUBAN_SEARCH_URL, HEADERS, params=params)
        
        if not response:
            return []
            
        data = response.json()
        results = []
        
        for item in data:
            if item.get('type') == 'b':  # 豆瓣API中图书类型为 'b'
                book = {
                    'url': item.get('url', ''),
                    'title': item.get('title', ''),
                    'author': item.get('author_name', ''),
                    'year': item.get('year', ''),
                    'cover_url': item.get('pic', ''),
                    'press': item.get('publisher_name', '')
                }
                results.append(book)
        
        return results
        
    except Exception as e:
        print(f"搜索过程出错: {str(e)}")
        return []

def get_book_details(url: str) -> Optional[Dict[str, str]]:
    """
    获取图书详细信息
    
    Args:
        url: 图书详情页URL

    Returns:
        包含图书详细信息的字典
    """
    try:
        response = make_request(url, HEADERS)
        if not response:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取基本信息
        info = {}
        info['url'] = url
        
        # 提取标题
        title = soup.select_one('#wrapper > h1 > span')
        if title:
            info['title'] = clean_text(title.text)
            
        # 提取作者
        author = soup.select_one('#info .pl:contains("作者") + a')
        if author:
            info['author'] = clean_text(author.text)
            
        # 提取出版社信息
        info_text = soup.select_one('#info').text if soup.select_one('#info') else ''
        publisher_match = re.search(r'出版社:\s*([^\n]+)', info_text)
        if publisher_match:
            info['press'] = clean_text(publisher_match.group(1))
            
        # 提取出版年份
        year_match = re.search(r'出版年:\s*([^\n]+)', info_text)
        if year_match:
            info['year'] = extract_year(year_match.group(1))
            
        # 提取ISBN
        isbn_match = re.search(r'ISBN:\s*([^\n]+)', info_text)
        if isbn_match:
            info['isbn'] = clean_text(isbn_match.group(1))
            
        # 提取内容简介
        intro = soup.select_one('#link-report .intro')
        if intro:
            info['description'] = clean_text(intro.text)
            
        # 提取作者简介
        author_intro_elem = soup.select_one('div#content div.indent div.intro')
        if author_intro_elem and author_intro_elem.find_previous('h2', string=re.compile(r'作者简介')):
            info['author_intro'] = clean_text(author_intro_elem.get_text())
        else:
            # 尝试其他可能的作者简介位置
            all_intros = soup.select('div.indent div.intro')
            for intro in all_intros:
                prev_h2 = intro.find_previous('h2')
                if prev_h2 and '作者' in prev_h2.get_text():
                    info['author_intro'] = clean_text(intro.get_text())
                    break
        
        # 提取封面图片
        cover = soup.select_one('#mainpic img')
        if cover and cover.get('src'):
            info['cover_url'] = cover['src']
            
        return info
        
    except Exception as e:
        print(f"获取图书详情失败: {str(e)}")
        return None
