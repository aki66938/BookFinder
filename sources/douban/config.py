"""豆瓣搜索配置文件"""

# 豆瓣搜索相关配置
DOUBAN_BASE_URL = "https://book.douban.com"
DOUBAN_SEARCH_URL = "https://book.douban.com/j/subject_suggest"
DOUBAN_BOOK_URL = "https://book.douban.com/subject/{}"

# 请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3      # 最大重试次数

# 请求头配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://book.douban.com/",
    "Origin": "https://book.douban.com",
    "Connection": "keep-alive"
}

# 图片上传配置
CHEVERETO_API_URL = "https://img.xingtan.one/api/1/upload"
CHEVERETO_API_KEY = ""  # 需要用户自行配置

# 临时文件目录
TEMP_DIR = "temp"

# 搜索结果配置
MAX_SEARCH_RESULTS = 10

# 重试配置
RETRY_DELAY = 1  # 秒
