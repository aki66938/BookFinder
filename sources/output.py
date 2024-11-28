"""通用搜索结果输出格式化"""
from __future__ import absolute_import

from typing import Dict, List, Optional

def format_search_results(results: List[Dict[str, str]], show_fields: Optional[List[str]] = None) -> List[Dict[str, str]]:
    """
    格式化输出搜索结果
    
    Args:
        results: 搜索结果列表
        show_fields: 要显示的字段列表，默认显示标题、作者、出版社、年份
    
    Returns:
        搜索结果列表
    """
    if not results:
        return []

    if show_fields is None:
        show_fields = ['title', 'author', 'press', 'year']

    for i, book in enumerate(results, 1):
        print(f"\n{i}. {book['title']}")
        for field in show_fields:
            if field != 'title' and book.get(field):  # 标题已经显示过了
                print(f"   {field_to_label(field)}: {book[field]}")
    
    return results

def format_book_details(book_info: Dict[str, str], show_fields: Optional[List[str]] = None) -> Optional[Dict[str, str]]:
    """
    格式化输出图书详细信息
    
    Args:
        book_info: 图书信息字典
        show_fields: 要显示的字段列表，默认显示所有可用字段
    
    Returns:
        图书信息字典
    """
    if not book_info:
        return None

    if show_fields is None:
        show_fields = ['title', 'author', 'press', 'year', 'isbn', 'description']

    print("\n图书详情:")
    for field in show_fields:
        if book_info.get(field):
            if field == 'description':
                print(f"\n内容简介:")
                print(book_info[field])
            else:
                print(f"{field_to_label(field)}: {book_info[field]}")
    
    return book_info

def field_to_label(field: str) -> str:
    """
    将字段名转换为显示标签
    
    Args:
        field: 字段名
    
    Returns:
        显示标签
    """
    labels = {
        'title': '书名',
        'author': '作者',
        'press': '出版社',
        'year': '出版年份',
        'isbn': 'ISBN',
        'description': '内容简介',
        'url': '链接',
        'cover_url': '封面'
    }
    return labels.get(field, field)
