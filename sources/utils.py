"""通用工具函数模块"""
import os
import time
import re
from typing import Optional, Dict, Any, Callable
import requests
from requests.exceptions import RequestException

def retry_on_failure(max_retries: int = 3) -> Callable:
    """
    装饰器：在网络请求失败时进行重试
    
    Args:
        max_retries: 最大重试次数
    
    Returns:
        装饰后的函数
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(1)  # 简单的延迟重试
            return None
        return wrapper
    return decorator

def make_request(url: str, headers: Dict[str, str], params: Optional[Dict] = None, 
                timeout: int = 10) -> Optional[requests.Response]:
    """
    发送HTTP请求
    
    Args:
        url: 请求URL
        headers: 请求头
        params: 请求参数
        timeout: 超时时间（秒）

    Returns:
        Response对象或None（如果请求失败）
    """
    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    return response

def get_with_retry(url: str, max_retries: int = 3, delay: float = 1.0) -> Optional[requests.Response]:
    """
    带重试的GET请求
    
    Args:
        url: 请求URL
        max_retries: 最大重试次数
        delay: 重试延迟时间（秒）
        
    Returns:
        Response对象或None（如果所有重试都失败）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except RequestException as e:
            if attempt == max_retries - 1:  # 最后一次重试
                return None
            time.sleep(delay)
    
    return None

def clean_text(text: str) -> str:
    """
    清理文本，移除多余的空白字符
    
    Args:
        text: 输入文本
    
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    return text.strip()

def clean_text_new(text: str) -> str:
    """
    清理文本，去除多余的空白字符
    
    Args:
        text: 输入文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    return ' '.join(text.split())

def extract_year(text: str) -> Optional[str]:
    """
    从文本中提取年份
    
    Args:
        text: 包含年份的文本

    Returns:
        年份字符串或None
    """
    if not text:
        return None
    
    # 匹配四位数字年份
    year_match = re.search(r'(\d{4})', text)
    if year_match:
        return year_match.group(1)
    return None

def extract_year_new(text: str) -> str:
    """
    从文本中提取年份
    
    Args:
        text: 输入文本
        
    Returns:
        提取的年份或空字符串
    """
    import re
    if not text:
        return ""
    year_match = re.search(r'(\d{4})', text)
    return year_match.group(1) if year_match else ""

def upload_image(image_url: str, filename: str) -> Optional[str]:
    """
    上传图片到图床
    """
    try:
        # 下载图片
        response = requests.get(image_url)
        if response.status_code != 200:
            return None

        # 获取文件类型和大小
        content_type = response.headers.get('content-type', '')
        file_size = len(response.content)
        
        # 准备文件
        files = {'file': (filename, response.content, content_type)}
        
        # 上传到图床
        upload_response = requests.post(
            UPLOAD_URL,
            files=files,
            headers=UPLOAD_HEADERS
        )
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            if result.get('status'):
                return result['data']['url']
        return None
        
    except Exception as e:
        return None
