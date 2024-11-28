"""豆瓣搜索异常类"""

class DoubanSearchError(Exception):
    """豆瓣搜索基础异常类"""
    pass

class NetworkError(DoubanSearchError):
    """网络请求异常"""
    pass

class ParseError(DoubanSearchError):
    """解析数据异常"""
    pass

class ImageProcessError(DoubanSearchError):
    """图片处理异常"""
    pass

class ConfigError(DoubanSearchError):
    """配置错误异常"""
    pass
