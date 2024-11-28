"""
获取 Lsky Pro token 的命令行工具
"""
from sources.image import get_lsky_token
import getpass

def main():
    print("Lsky Pro 登录")
    print("-" * 20)
    email = input("请输入邮箱: ")
    password = getpass.getpass("请输入密码: ")
    
    token = get_lsky_token(email, password)
    if token:
        print("\n登录成功！")
    else:
        print("\n登录失败，请检查邮箱和密码是否正确")

if __name__ == "__main__":
    main()
