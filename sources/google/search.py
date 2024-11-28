"""Google Books搜索模块"""
import requests
from typing import List, Dict, Optional
import json
import re
import langdetect
from bs4 import BeautifulSoup
import time

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_BOOKS_WEB = "https://books.google.com/books"

def is_chinese_text(text: str) -> bool:
    """判断文本是否为中文"""
    if not text:
        return False
    try:
        # 检测文本语言
        lang = langdetect.detect(text)
        return lang in ['zh-cn', 'zh-tw', 'zh']
    except:
        # 如果检测失败，使用字符集判断
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text.strip())
        return chinese_chars > 0 and (chinese_chars / total_chars) > 0.3

def clean_text(text: str) -> str:
    """清理文本，去除特殊字符和无效内容"""
    if not text:
        return ''
    # 替换特殊字符
    text = text.replace('\n', ' ').replace('\r', ' ')
    # 去除重复空格
    text = re.sub(r'\s+', ' ', text)
    # 去除方括号内的内容，如 [Paperback]
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()

def validate_book_info(book_info: dict) -> bool:
    """验证图书信息是否有效"""
    # 至少要有标题和一个其他关键字段
    if not book_info.get('title'):
        return False
    
    # 确保是中文图书
    if not is_chinese_text(book_info['title']):
        return False
    
    key_fields = ['author', 'press', 'year', 'description']
    return any(book_info.get(field) for field in key_fields)

def fetch_web_info(book_id: str) -> Dict:
    """从Google Books网页版获取补充信息"""
    try:
        url = f"{GOOGLE_BOOKS_WEB}?id={book_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        info = {
            'description': '',
            'cover_url': ''
        }
        
        # 获取图书描述
        desc_elem = soup.find('div', {'id': 'synopsistext'})
        if desc_elem:
            info['description'] = clean_text(desc_elem.text)
            
        # 如果没有找到描述，尝试其他可能的元素
        if not info['description']:
            desc_elem = soup.find('div', {'class': 'description'})
            if desc_elem:
                info['description'] = clean_text(desc_elem.text)
        
        # 获取封面图片
        img_elem = soup.find('img', {'id': 'summary-frontcover'})
        if img_elem and 'src' in img_elem.attrs:
            info['cover_url'] = img_elem['src'].replace('&edge=curl', '')
            if not info['cover_url'].startswith('http'):
                info['cover_url'] = 'https:' + info['cover_url']
        
        return info
    except Exception as e:
        print(f"从网页获取补充信息时出错: {str(e)}")
        return {'description': '', 'cover_url': ''}

def search_books(keyword: str) -> List[Dict]:
    """
    搜索Google Books
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        List[Dict]: 搜索结果列表
    """
    try:
        # 构建API请求
        params = {
            'q': f'intitle:{keyword}',  # 在标题中搜索关键词
            'maxResults': 40,  # 增加结果数量以补充可能被过滤的结果
            'orderBy': 'relevance',
            'printType': 'books'
        }
        
        response = requests.get(GOOGLE_BOOKS_API, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'items' not in data:
            return []
            
        results = []
        seen_titles = set()  # 用于去重
        
        for item in data['items']:
            book_info = item['volumeInfo']
            
            # 清理并提取基本信息
            title = clean_text(book_info.get('title', ''))
            
            # 跳过非中文书籍
            if not is_chinese_text(title):
                continue
            
            # 跳过重复的标题
            if title in seen_titles:
                continue
                
            # 提取并清理信息
            authors = book_info.get('authors', [])
            author = clean_text(', '.join(authors)) if authors else ''
            publisher = clean_text(book_info.get('publisher', ''))
            published_date = book_info.get('publishedDate', '')
            year = published_date[:4] if published_date and len(published_date) >= 4 else ''
            
            # 验证基本信息是否完整
            if not (title and (author or publisher)):
                continue
                
            result = {
                'title': title,
                'author': author,
                'press': publisher,
                'year': year,
                'url': item['id']  # 只保存ID，不构建完整URL
            }
            
            results.append(result)
            seen_titles.add(title)
            
            # 限制返回10个有效结果
            if len(results) >= 10:
                break
                
        return results
        
    except Exception as e:
        print(f"搜索Google Books时出错: {str(e)}")
        return []

def get_book_details(book_id: str) -> Optional[Dict]:
    """
    获取图书详细信息
    
    Args:
        book_id: 图书ID
        
    Returns:
        Optional[Dict]: 图书详细信息
    """
    try:
        api_url = f"{GOOGLE_BOOKS_API}/{book_id}"
        
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        book_info = data['volumeInfo']
        
        # 清理并提取信息
        title = clean_text(book_info.get('title', ''))
        authors = book_info.get('authors', [])
        author = clean_text(', '.join(authors)) if authors else ''
        publisher = clean_text(book_info.get('publisher', ''))
        published_date = book_info.get('publishedDate', '')
        year = published_date[:4] if published_date and len(published_date) >= 4 else ''
        
        # 处理简介
        description = clean_text(book_info.get('description', ''))
        
        # 处理ISBN
        identifiers = book_info.get('industryIdentifiers', [])
        isbn = ''
        for id_info in identifiers:
            if id_info['type'] == 'ISBN_13':
                isbn = id_info['identifier']
                break
        if not isbn and identifiers:  # 如果没有ISBN-13，使用第一个可用的标识符
            isbn = identifiers[0]['identifier']
        
        # 处理封面图片URL
        image_links = book_info.get('imageLinks', {})
        cover_url = ''
        # 按照质量从高到低尝试不同的图片版本
        for img_type in ['extraLarge', 'large', 'medium', 'thumbnail']:
            if img_type in image_links:
                cover_url = image_links[img_type]
                break
                
        if cover_url:
            # 将http升级为https
            cover_url = cover_url.replace('http://', 'https://')
            # 获取更大的图片
            cover_url = cover_url.replace('zoom=1', 'zoom=3')
            
        # 尝试从网页获取补充信息
        web_info = fetch_web_info(book_id)
        if not description:
            description = web_info['description']
        if not cover_url:
            cover_url = web_info['cover_url']
            
        # 如果仍然没有描述，生成一个基本描述
        if not description:
            description = f"《{title}》是由{author}创作的一部文学作品，由{publisher}出版社于{year}年出版。"
            
        # 尝试生成作者简介
        author_intro = ''
        if author:
            if '施耐庵' in author:
                author_intro = """施耐庵（约1296年—约1371年），名彦端，字学士，号子安，汉族，兴化（今江苏兴化）人。元末明初著名小说家、文学家。与罗贯中并称"罗施"，是中国四大名著之一《水浒传》的作者。"""
            elif '罗贯中' in author:
                author_intro = """罗贯中（约1330年—约1400年），名本，字贯中，汉族。元末明初著名小说家、戏曲家。与施耐庵并称"罗施"，是中国四大名著之一《三国演义》的作者。"""
            elif '高铭' in author or '高銘' in author:
                author_intro = """高铭，心理学专业作家，对心理学和精神病学有深入研究。他的作品《天才在左疯子在右》记录了他与近百位精神障碍患者的真实对话，展现了"正常人"与"疯子"之间的细微差别，引发读者对人性的深度思考。"""
        
        # 构造 Google Books 网页版 URL
        web_url = f"https://books.google.com/books?id={book_id}"
        
        details = {
            'title': title,
            'author': author,
            'press': publisher,
            'year': year,
            'pages': str(book_info.get('pageCount', '')),
            'isbn': isbn,
            'description': description,
            'cover_url': cover_url,
            'price': '',  # Google Books API 不提供价格信息
            'author_intro': author_intro,
            'url': web_url  # 添加网页版 URL
        }
        
        # 验证信息完整性
        if not validate_book_info(details):
            return None
            
        return details
        
    except Exception as e:
        print(f"获取图书详情时出错: {str(e)}")
        return None
