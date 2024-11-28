"""主程序入口"""
import os
from sources.douban.search import search_books as douban_search, get_book_details as douban_details
from sources.megbookhk.search import search_books as megbookhk_search, get_book_details as megbookhk_details
from sources.megbooktw.search import search_books as megbooktw_search, get_book_details as megbooktw_details
from sources.amazon.search import search_books as amazon_search, get_book_details as amazon_details
from sources.google.search import search_books as google_search, get_book_details as google_details
from sources.image import download_image, upload_local_image, sanitize_filename
import tempfile
import json
import requests
import config
from typing import Dict

def select_search_source() -> str:
    """
    让用户选择搜索源
    
    Returns:
        str: 选择的搜索源代号
    """
    while True:
        print("\n请选择搜索源：")
        print("1. 豆瓣图书")
        print("2. 香港美国书店")
        print("3. 台湾美国书店")
        print("4. 亚马逊图书")
        print("5. Google Books")
        print("0. 返回")
        
        choice = input("请输入选项序号: ").strip()
        
        if choice == "1":
            return "douban"
        elif choice == "2":
            return "megbookhk"
        elif choice == "3":
            return "megbooktw"
        elif choice == "4":
            return "amazon"
        elif choice == "5":
            return "google"
        elif choice == "0":
            return ""
        else:
            print("无效的选项，请重新选择！")

def format_book_info(book: dict, detailed: bool = False) -> None:
    """格式化显示图书信息"""
    if not book:
        print("无法获取图书信息")
        return
        
    if not detailed:
        # 搜索结果显示
        info = []
        if book.get('title'):
            info.append(book['title'])
        if book.get('author'):
            info.append(f"作者: {book['author']}")
        if book.get('press'):
            info.append(f"出版社: {book['press']}")
        if book.get('year'):
            info.append(f"出版年份: {book['year']}")
        print(" | ".join(info))
    else:
        # 详细信息显示
        print("\n图书详情:")
        print("-" * 50)
        
        # 基本信息
        if book.get('title'):
            print(f"书名: {book['title']}")
        if book.get('author'):
            print(f"作者: {book['author']}")
        if book.get('press'):
            print(f"出版社: {book['press']}")
        if book.get('year'):
            print(f"出版年份: {book['year']}")
        if book.get('pages'):
            print(f"页数: {book['pages']}")
        if book.get('price'):
            print(f"定价: {book['price']}")
        if book.get('isbn'):
            print(f"ISBN: {book['isbn']}")
        if book.get('url'):
            print(f"图书链接: {book['url']}")
            
        print("-" * 50)
        
        # 内容简介
        if book.get('description'):
            print("\n【内容简介】")
            print(book['description'])
            
        # 作者简介
        if book.get('author_intro'):
            print("\n【作者简介】")
            print(book['author_intro'])
            
        # 封面链接
        if book.get('cover_url'):
            print("\n【封面图片】")
            print(book['cover_url'])

def process_book_cover(book_info: dict) -> dict:
    """处理图书封面：下载并上传到图床"""
    if not book_info.get('cover_url'):
        return book_info

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 下载封面
            filename = sanitize_filename(book_info['title']) + "_cover.jpg"
            cover_path = os.path.join(temp_dir, filename)
            
            if download_image(book_info['cover_url'], cover_path):
                # 上传到图床
                upload_result = upload_local_image(cover_path)
                if upload_result and upload_result.get('url'):
                    book_info['cover_url'] = upload_result['url']
                    print(f"封面已上传到: {book_info['cover_url']}")
                else:
                    print("上传封面失败")
        except Exception as e:
            print(f"处理封面时出错: {str(e)}")
    
    return book_info

def main():
    """主函数"""
    while True:
        # 选择搜索源
        source = select_search_source()
        if not source:
            break
            
        # 获取搜索关键词
        keyword = input("\n请输入搜索关键词: ").strip()
        if not keyword:
            continue
            
        print(f"\n正在搜索 {keyword}...")
        
        # 根据选择的源进行搜索
        if source == "douban":
            search_results = douban_search(keyword)
            get_details = douban_details
        elif source == "megbookhk":
            search_results = megbookhk_search(keyword)
            get_details = megbookhk_details
        elif source == "megbooktw":
            search_results = megbooktw_search(keyword)
            get_details = megbooktw_details
        elif source == "amazon":
            search_results = amazon_search(keyword)
            get_details = amazon_details
        elif source == "google":
            search_results = google_search(keyword)
            get_details = google_details
        else:
            print("暂不支持该搜索源")
            continue
            
        if not search_results:
            print("未找到相关图书")
            continue
            
        # 显示搜索结果
        print("\n搜索结果:")
        for i, book in enumerate(search_results, 1):
            print(f"\n{i}. ", end='')
            format_book_info(book)
                
        # 获取用户选择
        while True:
            choice = input("\n请选择图书序号（输入 'b' 返回搜索）: ").strip()
            
            if choice.lower() == 'b':
                break
                
            try:
                index = int(choice)
                if 1 <= index <= len(search_results):
                    book = search_results[index - 1]
                    
                    print(f"\n获取《{book['title']}》的详细信息...")
                    book_info = get_details(book['url'])
                    
                    if not book_info:
                        print("无法获取图书详细信息，请尝试其他图书")
                        continue
                    
                    # 处理封面图片
                    try:
                        book_info = process_book_cover(book_info)
                    except Exception as e:
                        print(f"处理封面时出错: {str(e)}")
                        # 即使封面处理失败，也继续显示其他信息

                    # 显示图书详情
                    format_book_info(book_info, detailed=True)
                    
                    return book_info
                else:
                    print("无效的序号，请重新选择！")
            except ValueError:
                print("请输入有效的数字！")

if __name__ == '__main__':
    book = main()
    if book:
        print(f"\n已选择《{book['title']}》")
