"""亚马逊图书搜索模块"""
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re

from config import HEADERS, REQUEST_TIMEOUT
from sources.utils import retry_on_failure, make_request, extract_year

# URL配置
AMAZON_BASE_URL = 'https://www.amazon.com'
AMAZON_SEARCH_URL = f'{AMAZON_BASE_URL}/s'

def clean_text(text):
    """清理文本，移除多余的空白字符和特殊字符"""
    if not text:
        return ''
    # 移除特殊字符和控制字符
    text = re.sub(r'[\u200e\u200f\u202a\u202b\u202c\u202d\u202e]', '', text)
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除冒号和前后空白
    text = re.sub(r'^[:\s：‏‎]+|[:\s：‏‎]+$', '', text)
    return text.strip()

@retry_on_failure(max_retries=3)
def search_books(book_name: str) -> List[Dict[str, str]]:
    """
    搜索亚马逊图书
    
    Args:
        book_name: 要搜索的书名

    Returns:
        包含搜索结果的列表，每个元素是一个字典，包含书籍信息
    """
    try:
        # 构造搜索URL参数
        params = {
            'k': book_name,
            'i': 'stripbooks-intl-ship',
            '__mk_zh_CN': '亚马逊网站'
        }
        
        response = make_request(AMAZON_SEARCH_URL, HEADERS, params=params)
        if not response:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # 查找所有图书项
        book_items = soup.select('div[data-component-type="s-search-result"]')
        
        for item in book_items:
            try:
                # 提取标题和URL
                title_elem = item.select_one('h2 a.a-link-normal')
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.text)
                url = AMAZON_BASE_URL + title_elem.get('href', '')
                
                # 提取作者
                author = ''
                # 1. 首先尝试从专门的作者区域提取
                author_row = item.select_one('div.a-row .a-size-base:not(.a-color-secondary)')
                if author_row:
                    text = clean_text(author_row.text)
                    # 处理中文的"作者:"格式
                    author_match = re.search(r'作者[:\s：]\s*(.+?)(?:\s*\||$)', text)
                    if author_match:
                        author = clean_text(author_match.group(1))
                    else:
                        # 处理英文的"by"格式
                        if text.lower().startswith('by'):
                            author = clean_text(text[2:])
                        else:
                            author = text
                
                # 2. 如果上面方法失败,尝试从其他区域提取
                if not author:
                    author_container = item.select_one('div.a-row.a-size-base.a-color-secondary')
                    if author_container:
                        # 2.1 首先尝试找到作者链接
                        author_links = author_container.select('a:not(.a-text-normal)')
                        if author_links:
                            authors = []
                            for link in author_links:
                                author_text = clean_text(link.text)
                                if is_valid_author(author_text):
                                    authors.append(author_text)
                            author = ', '.join(authors)
                        
                        # 2.2 如果没有找到作者链接,尝试从span中提取
                        if not author:
                            # 首先尝试找到包含"作者"或"by"的span
                            for span in author_container.find_all('span'):
                                text = clean_text(span.text)
                                author_match = re.search(r'(?:作者[:\s：]|by\s+)(.+?)(?:\s*\||$)', text, re.IGNORECASE)
                                if author_match:
                                    author = clean_text(author_match.group(1))
                                    break
                            
                            # 如果还是没有找到,尝试其他span
                            if not author:
                                spans = author_container.find_all('span')
                                for span in spans:
                                    text = clean_text(span.text)
                                    if is_valid_author(text):
                                        author = text
                                        break
                
                # 3. 清理和验证作者名
                if author:
                    # 移除系列信息
                    author = re.sub(r'Book\s+\d+\s+of\s+\d+.*$', '', author, flags=re.IGNORECASE)
                    # 移除"by"开头
                    author = re.sub(r'^by\s+', '', author, flags=re.IGNORECASE)
                    # 移除括号中的内容
                    author = re.sub(r'\([^)]*\)', '', author)
                    # 移除方括号中的内容
                    author = re.sub(r'\[[^\]]*\]', '', author)
                    # 移除多余的标点符号
                    author = re.sub(r'[,;，；]+', ',', author)
                    # 移除首尾的标点符号和空白
                    author = author.strip('.,;:，。；：、 ')
                    # 确保每个作者名之间只有一个逗号
                    author = ','.join(part.strip() for part in author.split(',') if is_valid_author(part.strip()))
                    
                    # 如果清理后为空，设为空字符串
                    if not author or author.lower().strip() in ['by', '作者']:
                        author = ''
                
                # 提取封面图片
                img_elem = item.select_one('img.s-image')
                cover_url = img_elem.get('src', '') if img_elem else ''
                
                # 提取更多信息
                details_text = ''
                details_elem = item.select_one('.a-size-base.a-color-secondary')
                if details_elem:
                    details_text = clean_text(details_elem.text)
                
                # 初始化图书信息
                book = {
                    'url': url,  # 使用亚马逊原始链接
                    'title': title,
                    'author': author,
                    'cover_url': cover_url,
                    'press': '',
                    'year': '',
                    'isbn': '',
                    'description': ''
                }
                
                # 从详情文本中提取更多信息
                if details_text:
                    # 提取出版社和年份
                    press_match = re.search(r'(?:出版社|Publisher)\s*[:：]\s*([^(（]+)(?:\s*[(（]([^)）]+)[)）])?', details_text)
                    if press_match:
                        book['press'] = clean_text(press_match.group(1))
                        if press_match.group(2):
                            book['year'] = extract_year(press_match.group(2))
                    
                    # 如果还没找到年份，尝试其他方式
                    if not book['year']:
                        # 查找日期格式
                        date_patterns = [
                            r'(\d{4}年\d{1,2}月\d{1,2}日)',
                            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                            r'([A-Z][a-z]+ \d{1,2}, \d{4})',
                            r'(\d{4})',
                        ]
                        
                        for pattern in date_patterns:
                            date_match = re.search(pattern, details_text)
                            if date_match:
                                book['year'] = extract_year(date_match.group(1))
                                break
            
                    # ISBN
                    isbn_patterns = [
                        r'ISBN[-‐]?(?:13|10)?\s*[:：]?\s*(\d[0-9X‐-]*)',
                        r'(\d{10}|\d{13})',
                        r'ISBN[-‐]?(?:13|10)?\s*[:：]?\s*([0-9X‐-]+)'
                    ]
                    
                    for pattern in isbn_patterns:
                        isbn_match = re.search(pattern, details_text)
                        if isbn_match:
                            isbn = isbn_match.group(1)
                            # 清理ISBN，只保留数字和X
                            isbn = re.sub(r'[^0-9X]', '', isbn)
                            if len(isbn) in (10, 13):  # 只接受10位或13位的ISBN
                                book['isbn'] = isbn
                                break
            
                    # 页数
                    if any(key in details_text for key in ['页数', 'Pages', '页', 'Print length']):
                        pages_patterns = [
                            r'(?:页数|Pages|页|Print length)\s*[:：]?\s*(\d+)',
                            r'(\d+)\s*(?:页|pages)',
                        ]
                        
                        for pattern in pages_patterns:
                            pages_match = re.search(pattern, details_text)
                            if pages_match:
                                book['pages'] = pages_match.group(1)
                                break
        
                # 提取描述
                desc_elem = item.select_one('.a-size-base.a-color-secondary')
                if desc_elem:
                    desc_text = clean_text(desc_elem.text)
                    # 如果描述中包含作者信息，尝试提取纯描述部分
                    if '作者' in desc_text:
                        desc_parts = desc_text.split('作者:', 1)
                        if len(desc_parts) > 1:
                            desc_text = desc_parts[0].strip()
                    book['description'] = desc_text
                
                results.append(book)
                
            except Exception as e:
                print(f"处理搜索结果项时出错: {str(e)}")
                continue
        
        return results
        
    except Exception as e:
        print(f"搜索过程出错: {str(e)}")
        return []

def is_valid_author(text: str) -> bool:
    """
    检查文本是否是有效的作者名
    
    Args:
        text: 要检查的文本
        
    Returns:
        bool: 是否是有效的作者名
    """
    if not text:
        return False
        
    # 排除词列表
    excluded_terms = [
        # 版本信息
        'Chinese Edition', 'English Edition', 'Paperback', 'Kindle Edition', 
        'Hardcover', 'Mass Market', 'Library Binding',
        # 中文版本信息
        '中文版', '平装', '精装', '简体中文', '繁体中文', '中英文版',
        '简体', '繁体', '中文', '英文',
        # 标识词
        'by', 'By', '作者', 'author', 'Author',
        # 系列信息
        'Book', 'Series', 'Volume', 'Vol', '系列', '丛书',
        # 出版社相关
        'Publisher', 'Publications', 'Press', 'Publishing',
        '出版社', '出版',
        # 其他
        'Edition', 'Revised', 'Updated', 'New',
        '版本', '修订版', '增订版', '新版',
        # 标点符号
        '|', ',', ':', '：'
    ]
    
    # 检查是否包含任何排除词
    text_lower = text.lower()
    if any(term.lower() in text_lower for term in excluded_terms):
        return False
        
    # 检查是否只包含标点符号或空白
    if re.match(r'^[\s\.,;:，。；：、]+$', text):
        return False
        
    # 检查是否包含数字（可能是系列编号）
    if re.search(r'\d', text):
        return False
        
    return True

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
        
        info = {
            'url': url,
            'title': '',
            'author': '',
            'press': '',
            'year': '',
            'isbn': '',
            'pages': '',
            'price': '',
            'description': '',
            'cover_url': ''
        }
        
        # 提取标题
        title_elem = soup.select_one('#productTitle, #title')
        if title_elem:
            info['title'] = clean_text(title_elem.text)
        
        # 提取作者 - 使用多个选择器
        authors = []
        author_selectors = [
            '#bylineInfo .author a', 
            '#bylineInfo .contributorNameID',
            '#bylineInfo a[data-asin]',
            '.author .a-link-normal',
            '#byline_secondary_view_div .a-link-normal',
            '#contributorLinkContainer a'
        ]
        
        for selector in author_selectors:
            author_elems = soup.select(selector)
            for author_elem in author_elems:
                author = clean_text(author_elem.text)
                if is_valid_author(author):
                    if '作者' in author:
                        author = re.sub(r'^作者[:\s：]\s*', '', author)
                    if author not in authors:  # 避免重复
                        authors.append(author)
        
        info['author'] = ', '.join(authors) if authors else ''
        
        # 提取出版信息
        detail_selectors = [
            '#detailBullets_feature_div li',
            '#productDetailsTable .content li',
            '#detailBulletsWrapper_feature_div li',
            '#productDetails_detailBullets_sections1 tr',
            '#productDetails_techSpec_section_1 tr',
            '.detail-bullet-list span',
            '.a-expander-content table tr'
        ]
        
        details_elem = []
        for selector in detail_selectors:
            elements = soup.select(selector)
            if elements:
                details_elem.extend(elements)
                
        for elem in details_elem:
            text = clean_text(elem.text)
            
            # 出版社和日期
            if any(key in text for key in ['出版社', 'Publisher', '出版商', 'Published by']):
                # 清理文本，移除特殊字符
                text = clean_text(text)
                if not text or text in ['Publisher', '出版社'] or len(text) < 3:
                    continue
                
                # 尝试多种匹配模式
                press_patterns = [
                    # 处理中文出版社格式
                    r'(?:出版社|出版商)\s*[:：]?\s*([^;(（]+?(?:出版社|出版|Publishers?|Press|Publishing(?:\s+House)?|Books|Media))',
                    # 处理英文出版社格式
                    r'(?:Publisher|Published by)\s*[:：]?\s*([^;(（]+?(?:Publishers?|Press|Publishing(?:\s+House)?|Books|Media))',
                    # 通用格式，但要求至少包含中文或英文字符
                    r'(?:出版社|Publisher|出版商|Published by)\s*[:：]?\s*([^;(（]{3,}?[\u4e00-\u9fff\w]+[^;(（]*?)(?:\s*[(（]|$)',
                ]
                
                for pattern in press_patterns:
                    press_match = re.search(pattern, text)
                    if press_match:
                        press = clean_text(press_match.group(1))
                        # 过滤无效出版社名
                        if (press and 
                            len(press) >= 2 and  # 至少2个字符
                            re.search(r'[\u4e00-\u9fff\w]', press) and  # 必须包含中文或英文字符
                            not press.strip() in ['Publisher', '出版社', ':', '：', '‏', '‎']):
                            info['press'] = press
                            # 尝试从文本中提取年份
                            year_match = re.search(r'[(（]([^)）]+)[)）]', text)
                            if year_match:
                                info['year'] = extract_year(year_match.group(1))
                            break
                
                # 如果还没找到年份，尝试其他方式
                if not info['year']:
                    # 查找日期格式
                    date_patterns = [
                        r'(\d{4}年\d{1,2}月\d{1,2}日)',
                        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                        r'([A-Z][a-z]+ \d{1,2}, \d{4})',
                        r'(\d{4})',
                    ]
                    
                    for pattern in date_patterns:
                        date_match = re.search(pattern, text)
                        if date_match:
                            info['year'] = extract_year(date_match.group(1))
                            break
            
            # ISBN
            if 'ISBN' in text:
                isbn_patterns = [
                    r'ISBN[-‐]?(?:13|10)?\s*[:：]?\s*(\d[0-9X‐-]*)',
                    r'(\d{10}|\d{13})',
                    r'ISBN[-‐]?(?:13|10)?\s*[:：]?\s*([0-9X‐-]+)'
                ]
                
                for pattern in isbn_patterns:
                    isbn_match = re.search(pattern, text)
                    if isbn_match:
                        isbn = isbn_match.group(1)
                        # 清理ISBN，只保留数字和X
                        isbn = re.sub(r'[^0-9X]', '', isbn)
                        if len(isbn) in (10, 13):  # 只接受10位或13位的ISBN
                            info['isbn'] = isbn
                            break
            
            # 页数
            if any(key in text for key in ['页数', 'Pages', '页', 'Print length']):
                pages_patterns = [
                    r'(?:页数|Pages|页|Print length)\s*[:：]?\s*(\d+)',
                    r'(\d+)\s*(?:页|pages)',
                ]
                
                for pattern in pages_patterns:
                    pages_match = re.search(pattern, text)
                    if pages_match:
                        info['pages'] = pages_match.group(1)
                        break
        
        # 提取价格
        price_selectors = [
            '.a-price .a-offscreen',
            '#price',
            '.kindle-price #digital-list-price',
            '.swatchElement.selected .a-color-price'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                info['price'] = clean_text(price_elem.text)
                break
        
        # 提取图书描述
        description = ''
        desc_selectors = [
            '#bookDescription_feature_div noscript',
            '#bookDescription_feature_div .a-expander-content',
            '#productDescription .content',
            '#bookDescription_feature_div',
            '#book_description',
            '.book-description'
        ]
        
        for selector in desc_selectors:
            desc_elems = soup.select(selector)
            for desc_elem in desc_elems:
                if desc_elem and desc_elem.text.strip():
                    description = clean_text(desc_elem.text)
                    if description:
                        break
            if description:
                break
        
        info['description'] = description
        
        # 提取封面图片URL
        cover_selectors = [
            '#imgBlkFront',
            '#main-image',
            '#ebooksImgBlkFront',
            '#img-canvas img'
        ]
        
        for selector in cover_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                # 尝试不同的属性获取图片URL
                for attr in ['data-a-dynamic-image', 'data-src', 'src']:
                    img_url = img_elem.get(attr)
                    if img_url:
                        # 如果是JSON字符串（data-a-dynamic-image的情况）
                        if attr == 'data-a-dynamic-image':
                            try:
                                import json
                                urls = json.loads(img_url)
                                # 获取最大分辨率的图片URL
                                img_url = max(urls.items(), key=lambda x: int(x[1][0]) * int(x[1][1]))[0]
                            except:
                                continue
                        info['cover_url'] = img_url
                        break
                if info['cover_url']:
                    break
        
        return info
        
    except Exception as e:
        print(f"获取图书详情时出错: {str(e)}")
        return None

def extract_year(text: str) -> str:
    """
    从文本中提取年份
    
    Args:
        text: 包含年份的文本
        
    Returns:
        提取出的年份，如果没有找到则返回空字符串
    """
    # 匹配年份格式：YYYY或YYYY年
    year_match = re.search(r'(\d{4})(?:年)?', text)
    return year_match.group(1) if year_match else ''

def format_book_info(book: Dict[str, str]) -> str:
    """
    格式化图书信息为易读的字符串
    
    Args:
        book: 包含图书信息的字典
        
    Returns:
        格式化后的字符串
    """
    info_lines = ['--------------------------------------------------']
    
    # 基本信息
    info_lines.append(f'书名: {book.get("title", "")}')
    if book.get('author'):
        info_lines.append(f'作者: {book["author"]}')
    if book.get('press'):
        info_lines.append(f'出版社: {book["press"]}')
    if book.get('year'):
        info_lines.append(f'出版年份: {book["year"]}')
    if book.get('isbn'):
        info_lines.append(f'ISBN: {book["isbn"]}')
    
    # 其他信息
    if book.get('binding'):
        info_lines.append(f'装订: {book["binding"]}')
    if book.get('pages'):
        info_lines.append(f'页数: {book["pages"]}')
    if book.get('language'):
        info_lines.append(f'语言: {book["language"]}')
    if book.get('series'):
        info_lines.append(f'丛书: {book["series"]}')
    if book.get('price'):
        info_lines.append(f'价格: {book["price"]}')
    
    info_lines.append('--------------------------------------------------')
    
    # 内容简介
    if book.get('description'):
        info_lines.extend(['', '【内容简介】', book['description']])
    
    return '\n'.join(info_lines)
