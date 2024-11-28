"""配置文件"""
from typing import Dict
import os
from dotenv import load_dotenv

# 加载 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"尝试加载环境变量文件: {env_path}")
load_dotenv(env_path)

# HTTP请求配置
HEADERS: Dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# URL配置
DOUBAN_BASE_URL = 'https://book.douban.com'
DOUBAN_SEARCH_URL = f'{DOUBAN_BASE_URL}/j/subject_suggest?q={{}}'

# 图床配置
IMGHOST_ENABLED = os.getenv('IMGHOST_ENABLED', 'false').lower() == 'true'
IMGHOST_BASE_URL = os.getenv('IMGHOST_BASE_URL', '').strip()

print("\n=== 图床配置信息 ===")
print(f"IMGHOST_ENABLED: {IMGHOST_ENABLED}")
print(f"原始 IMGHOST_BASE_URL: {IMGHOST_BASE_URL}")

# 确保 BASE_URL 格式正确
if IMGHOST_ENABLED and IMGHOST_BASE_URL:
    # 如果URL不以http://或https://开头，添加https://
    if not IMGHOST_BASE_URL.startswith(('http://', 'https://')):
        IMGHOST_BASE_URL = 'https://' + IMGHOST_BASE_URL
        print(f"添加https://后: {IMGHOST_BASE_URL}")

    # 移除末尾的斜杠
    IMGHOST_BASE_URL = IMGHOST_BASE_URL.rstrip('/')
    print(f"移除末尾斜杠后: {IMGHOST_BASE_URL}")

    # 检查是否包含 /api/v1
    if '/api/v1' in IMGHOST_BASE_URL:
        base_parts = IMGHOST_BASE_URL.split('/api/v1')
        IMGHOST_BASE_URL = base_parts[0]
        print(f"移除 /api/v1 后: {IMGHOST_BASE_URL}")

# 构建API URLs
IMGHOST_API_BASE = f"{IMGHOST_BASE_URL}/api/v1" if IMGHOST_BASE_URL else ""
IMGHOST_UPLOAD_URL = f"{IMGHOST_API_BASE}/upload" if IMGHOST_API_BASE else ""

print(f"IMGHOST_API_BASE: {IMGHOST_API_BASE}")
print(f"IMGHOST_UPLOAD_URL: {IMGHOST_UPLOAD_URL}")
print("=== 图床配置信息 ===\n")

IMGHOST_EMAIL = os.getenv('IMGHOST_EMAIL', '').strip()
IMGHOST_PASSWORD = os.getenv('IMGHOST_PASSWORD', '').strip()

# 请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3      # 最大重试次数
