"""配置文件"""
from typing import Dict

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

CALIS_BASE_URL = 'http://opac.calis.edu.cn'
CALIS_SEARCH_URL = f'{CALIS_BASE_URL}/opac/simpleSearch.do'

# 图床配置
IMGHOST_BASE_URL = 'https://img.xingtan.one/api/v1'
IMGHOST_UPLOAD_URL = f'{IMGHOST_BASE_URL}/upload'

# 请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3      # 最大重试次数
