"""通用图片处理模块"""
import os
import re
import json
import requests
from typing import Optional, Dict
from sources.utils import retry_on_failure, make_request
from config import (
    IMGHOST_UPLOAD_URL, 
    REQUEST_TIMEOUT, 
    IMGHOST_BASE_URL,
    IMGHOST_API_BASE,
    IMGHOST_ENABLED,
    IMGHOST_EMAIL,
    IMGHOST_PASSWORD
)

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不合法字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的文件名
    """
    # 移除不合法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制长度
    return filename[:100]

@retry_on_failure(max_retries=3)
def download_image(url: str, save_path: str) -> bool:
    """
    下载图片并保存到本地
    
    Args:
        url: 图片URL
        save_path: 保存路径

    Returns:
        下载是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 下载图片
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # 保存图片
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
        
    except Exception:
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

def upload_local_image(image_path: str) -> Optional[Dict[str, str]]:
    """
    上传本地图片到图床
    
    Args:
        image_path: 本地图片路径

    Returns:
        包含图片URL的字典，如果上传失败则返回None
    """
    max_retries = 3
    retry_delay = 2  # 重试延迟（秒）
    
    for attempt in range(max_retries):
        try:
            # 首先尝试从文件读取token
            token = None
            token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')
            
            if os.path.exists(token_path):
                try:
                    with open(token_path, 'r', encoding='utf-8') as f:
                        token_data = json.load(f)
                        token = token_data.get('token')
                except:
                    pass
                    
            # 如果没有token，尝试重新获取
            if not token:
                token = get_lsky_token(IMGHOST_EMAIL, IMGHOST_PASSWORD)
                if not token:
                    return None

            # 验证文件是否存在和可读
            if not os.path.exists(image_path):
                print(f"文件不存在: {image_path}")
                return None
                
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                print("错误: 文件大小为0")
                return None
                
            if file_size > 5 * 1024 * 1024:  # 5MB限制
                print("错误: 文件大小超过5MB限制")
                return None
                
            # 检测文件类型
            import imghdr
            image_type = imghdr.what(image_path)
            if not image_type:
                print("错误: 不是有效的图片文件")
                return None
                
            content_type = f'image/{image_type}'
            
            # 准备文件名
            original_filename = os.path.basename(image_path)
            safe_filename = re.sub(r'[^\w\-_\.]', '', original_filename)
            if not safe_filename:
                safe_filename = f'image.{image_type}'
            
            # 准备请求头
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            # 上传图片
            with open(image_path, 'rb') as f:
                files = {
                    'file': (safe_filename, f, content_type)
                }
                
                response = requests.post(
                    IMGHOST_UPLOAD_URL,
                    headers=headers,
                    files=files,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == True:
                        result = {
                            'url': data['data'].get('url', ''),
                            'id': data['data'].get('id', '')
                        }
                        return result
                    else:
                        print(f"上传失败: {data.get('message', '未知错误')}")
                else:
                    print(f"上传失败，HTTP状态码: {response.status_code}")
            
            # 如果不是最后一次尝试，等待一段时间后重试
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
        
        except Exception as e:
            print(f"上传图片时出错: {str(e)}")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                retry_delay *= 2
    
    return None

def process_cover_image(book_info: Dict[str, str], temp_dir: str = 'temp') -> Dict[str, str]:
    """
    处理图书封面图片：下载并上传到图床
    
    Args:
        book_info: 图书信息字典，必须包含'title'字段，可选'cover_url'字段
        temp_dir: 临时文件目录
        
    Returns:
        更新后的图书信息字典
    """
    if not book_info.get('cover_url'):
        return book_info
        
    # 如果图床功能未启用，直接返回原始URL
    if not IMGHOST_ENABLED:
        return book_info

    # 如果缺少必要的配置，返回原始URL
    if not all([IMGHOST_BASE_URL, IMGHOST_EMAIL, IMGHOST_PASSWORD]):
        print("警告: 图床功能已启用但配置不完整，请设置 IMGHOST_BASE_URL, IMGHOST_EMAIL 和 IMGHOST_PASSWORD 环境变量")
        return book_info
        
    # 创建临时目录
    os.makedirs(temp_dir, exist_ok=True)
    
    # 下载图片
    temp_path = os.path.join(temp_dir, sanitize_filename(f"{book_info['title']}_cover.jpg"))
    if download_image(book_info['cover_url'], temp_path):
        # 上传到图床
        result = upload_local_image(temp_path)
        if result and result.get('url'):
            book_info['cover_url'] = result['url']
            
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return book_info

def get_lsky_token(email: str, password: str) -> Optional[str]:
    """
    通过登录获取 Lsky Pro 的 token
    
    Args:
        email: 登录邮箱
        password: 登录密码
        
    Returns:
        成功返回 token，失败返回 None
    """
    if not IMGHOST_ENABLED:
        print("错误: 图床功能未启用，请在 .env 中设置 IMGHOST_ENABLED=true")
        return None
        
    if not IMGHOST_BASE_URL:
        print("错误: 图床URL未设置，请在 .env 中设置 IMGHOST_BASE_URL")
        return None
        
    if not email or not password:
        print("错误: 邮箱或密码为空，请在 .env 中设置 IMGHOST_EMAIL 和 IMGHOST_PASSWORD")
        return None
    
    try:
        login_url = f"{IMGHOST_API_BASE}/tokens"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        data = {
            'email': email,
            'password': password
        }
        
        response = requests.post(login_url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status'):
                token = data['data'].get('token')
                if token:
                    # 保存token到文件
                    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')
                    with open(token_path, 'w', encoding='utf-8') as f:
                        json.dump({'token': token}, f, ensure_ascii=False, indent=4)
                    return token
            else:
                print(f"登录失败: {data.get('message', '未知错误')}")
        else:
            print(f"HTTP请求失败，状态码: {response.status_code}")
            if response.text:
                try:
                    error_data = response.json()
                    print(f"错误信息: {error_data.get('message', '未知错误')}")
                except:
                    print(f"响应内容: {response.text[:200]}")
        
        return None
        
    except requests.exceptions.ConnectionError:
        print(f"连接错误: 无法连接到图床服务器 {IMGHOST_BASE_URL}")
    except requests.exceptions.Timeout:
        print(f"连接超时: 服务器响应时间超过 {REQUEST_TIMEOUT} 秒")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
    
    return None
