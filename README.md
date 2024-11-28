# BookFinder 📚

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)

[English](README.md#english) | [中文](README.md#中文)

<div id="中文">

## 目录

- [简介](#简介)
- [功能特点](#功能特点)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)

## 简介

BookFinder 是一个强大的多源中文图书搜索工具，支持从多个在线书店和图书数据库搜索图书信息。它能够帮助您快速获取全面的图书信息，提高图书检索效率。

## 功能特点

- **多源搜索**：支持从多个来源搜索图书信息
  - 📚 豆瓣图书
  - 📚 香港美国书店
  - 📚 台湾美国书店
  - 📚 亚马逊图书
  - 📚 Google Books

- **丰富的图书信息**
  - 📖 基本信息：书名、作者、出版社、出版年份、ISBN等
  - 📝 详细介绍：内容简介、作者简介
  - 🖼️ 图片资源：图书封面（自动上传至图床）
  - 🔗 图书链接生成

- **自适应信息提取**
  - ✨ 自动清理和格式化文本
  - 🎯 自适应识别和提取关键信息
  - 🔄 处理多种数据格式和编码

- **错误处理**
  - ⚡ 异常处理机制
  - 🔄 自动重试机制
  - 📝 详细的错误日志

## 系统要求

- Python 3.8+
- Windows操作系统
- 科学上网环境（部分图书数据源需要）

## 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   # Windows
   copy .env.template .env
   # 或在Linux/macOS下
   cp .env.template .env
   ```

3. **修改配置**
   根据需要修改 `.env` 文件中的配置项

## 使用方法

1. 配置环境变量：
   
   复制 `.env.template` 文件并重命名为 `.env`，然后根据需要修改配置：

   ```bash
   # Windows
   copy .env.template .env
   # 或在Linux/macOS下
   cp .env.template .env
   ```

   在 `.env` 文件中配置以下环境变量：

   ```bash
   # 图床功能开关（true/false）
   IMGHOST_ENABLED=false

   # 如果启用图床功能（IMGHOST_ENABLED=true），需要配置以下变量：
   IMGHOST_BASE_URL=your_imghost_url      # 图床服务器基础URL
   IMGHOST_EMAIL=your_email               # 图床账号邮箱
   IMGHOST_PASSWORD=your_password         # 图床账号密码
   ```

   如果不启用图床功能（IMGHOST_ENABLED=false），程序将只显示图片的本地路径。

2. 运行主程序：
```bash
python main.py
```

3. 选择搜索源：
   - 1: 豆瓣图书
   - 2: 香港美国书店
   - 3: 台湾美国书店
   - 4: 亚马逊图书
   - 5: Google Books
   - 0: 返回

4. 输入搜索关键词：
   - 支持书名、作者、ISBN等关键词
   - 建议使用准确的书名或ISBN进行搜索
   - 空输入将返回搜索源选择

5. 查看搜索结果：
   - 显示匹配图书的基本信息列表
   - 输入序号查看详细信息
   - 输入 'b' 返回搜索
   - 无效输入会提示重新选择

6. 图书详情展示：
   - 基本信息：书名、作者、出版社等
   - 内容简介和作者简介
   - 封面图片（支持自动上传到图床）
   - 图书链接

## 图床配置说明

本项目支持使用 Lsky Pro 图床服务来存储图书封面。如果你想使用此功能：

1. 确保你有可用的 Lsky Pro 图床服务
2. 在环境变量中设置：
   - `IMGHOST_ENABLED=true` 启用图床功能
   - `IMGHOST_BASE_URL` 设置为你的图床地址（例如：https://img.example.com）
   - `IMGHOST_EMAIL` 设置为你的登录邮箱
   - `IMGHOST_PASSWORD` 设置为你的登录密码

3. 图床功能测试：
   ```bash
   python get_token.py
   ```
   如果配置正确，将显示"登录成功"。

## 使用许可

本项目仅供学习和研究使用，禁止用于商业用途。在使用本项目时，请遵守相关网站的使用条款和规定。

## 开源协议

本项目采用 MIT 许可证。详见 [MIT License](https://opensource.org/licenses/MIT)。

## 项目结构

```
db_book_search/
├── main.py              # 主程序入口
├── config.py            # 主配置文件
├── get_token.py         # 图床token获取工具
├── requirements.txt     # 依赖清单
├── token.json          # 图床token配置（可选）
└── sources/            # 数据源模块
    ├── utils.py        # 通用工具函数
    ├── image.py        # 图片处理模块
    ├── output.py       # 输出格式化模块
    ├── config.py       # 数据源配置文件
    ├── douban/         # 豆瓣图书模块
    ├── megbookhk/      # 香港美国书店模块
    ├── megbooktw/      # 台湾美国书店模块
    ├── amazon/         # 亚马逊图书模块
    └── google/         # Google Books模块
```

## 开发状态

- [x] 豆瓣图书搜索
- [x] 香港美国书店搜索
- [x] 台湾美国书店搜索
- [x] 亚马逊图书搜索
- [x] Google Books搜索

## 注意事项

1. 图床功能为可选功能：
   - 如果不配置token.json，程序仍然可以正常运行
   - 未配置图床时，图书封面将只显示原始URL
   - 配置图床可以实现封面的永久保存和快速访问

2. 网络访问说明：
   - 部分搜索源可能需要使用上科学网才能访问
   - 请确保您的网络环境正常
   - 程序包含自动重试机制，但仍可能受网络状况影响

3. 搜索结果说明：
   - 搜索结果的准确性和完整性取决于各数据源的实时状态
   - 不同数据源的信息可能存在差异
   - 建议交叉对比多个数据源的信息

4. 性能优化：
   - 程序包含缓存机制，可减少重复请求
   - 支持异步处理和并发搜索
   - 自动清理临时文件和缓存

## 常见问题

1. 搜索无结果：
   - 检查关键词是否准确
   - 尝试使用不同的搜索源
   - 确认网络连接正常

2. 图片上传失败：
   - 验证token.json配置是否正确
   - 检查网络连接状态
   - 查看错误日志获取详细信息

3. 程序运行错误：
   - 确保已安装所有依赖
   - 检查Python版本是否满足要求
   - 查看错误日志进行排查

---

<div id="english">

# BookFinder 📚

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [FAQ](#faq)
- [Contributing](#contributing)

## Introduction

BookFinder is a powerful multi-source Chinese book search tool that supports searching book information from multiple online bookstores and book databases. It helps you quickly obtain comprehensive book information and improve book retrieval efficiency.

## Features

- **Multi-source Search**
  - 📚 Douban Books
  - 📚 Hong Kong Books
  - 📚 Taiwan Books
  - 📚 Amazon Books
  - 📚 Google Books

- **Rich Book Information**
  - 📖 Basic Info: Title, Author, Publisher, Publication Year, ISBN, etc.
  - 📝 Detailed Description: Content Summary, Author Biography
  - 🖼️ Image Resources: Book Cover (Auto-upload to Image Host)
  - 🔗 Book Link Generation

- **Adaptive Information Extraction**
  - ✨ Automatic Text Cleaning and Formatting
  - 🎯 Adaptive Recognition and Key Information Extraction
  - 🔄 Multiple Data Format and Encoding Support

- **Error Handling**
  - ⚡ Exception Handling Mechanism
  - 🔄 Automatic Retry Mechanism
  - 📝 Detailed Error Logging

## Requirements

- Python 3.8+
- Windows Operating System
- Internet Access (VPN might be required for some sources)

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   ```bash
   # Windows
   copy .env.template .env
   # or on Linux/macOS
   cp .env.template .env
   ```

3. **Modify Configuration**
   Edit the configuration items in the `.env` file as needed

## Usage

1. Configure environment variables:
   
   Copy `.env.template` file and rename it to `.env`, then modify the configuration as needed:

   ```bash
   # Windows
   copy .env.template .env
   # or on Linux/macOS
   cp .env.template .env
   ```

   Configure the following environment variables in the `.env` file:

   ```bash
   # Image host feature switch (true/false)
   IMGHOST_ENABLED=false

   # If image host feature is enabled (IMGHOST_ENABLED=true), configure the following variables:
   IMGHOST_BASE_URL=your_imghost_url      # Image host server base URL
   IMGHOST_EMAIL=your_email               # Image host account email
   IMGHOST_PASSWORD=your_password         # Image host account password
   ```

   If image host feature is not enabled (IMGHOST_ENABLED=false), the program will only display the local path of the image.

2. Run the main program:
```bash
python main.py
```

3. Select search source:
   - 1: Douban Books
   - 2: Hong Kong Books
   - 3: Taiwan Books
   - 4: Amazon Books
   - 5: Google Books
   - 0: Back

4. Input search keywords:
   - Support book title, author, ISBN, etc.
   - Suggest using accurate book title or ISBN for search
   - Empty input will return to search source selection

5. View search results:
   - Display the list of basic information of matched books
   - Input the serial number to view detailed information
   - Input 'b' to return to search
   - Invalid input will prompt to re-select

6. Book details display:
   - Basic information: book title, author, publisher, etc.
   - Content summary and author biography
   - Book cover image (support auto-upload to image host)
   - Book link

## Image Host Configuration

This project supports using Lsky Pro image host service to store book covers. If you want to use this feature:

1. Ensure you have a valid Lsky Pro image host service
2. Configure the following environment variables:
   - `IMGHOST_ENABLED=true` to enable image host feature
   - `IMGHOST_BASE_URL` to set your image host server base URL (e.g. https://img.example.com)
   - `IMGHOST_EMAIL` to set your image host account email
   - `IMGHOST_PASSWORD` to set your image host account password

3. Test image host feature:
   ```bash
   python get_token.py
   ```
   If configured correctly, it will display "Login successful".

## License

This project is for learning and research purposes only, and is not allowed to be used for commercial purposes. When using this project, please follow the terms and conditions of the relevant websites.

## Open Source License

This project uses the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for details.

## Project Structure

```
db_book_search/
├── main.py              # Main program entry
├── config.py            # Main configuration file
├── get_token.py         # Image host token acquisition tool
├── requirements.txt     # Dependency list
├── token.json          # Image host token configuration (optional)
└── sources/            # Data source module
    ├── utils.py        # Common utility functions
    ├── image.py        # Image processing module
    ├── output.py       # Output formatting module
    ├── config.py       # Data source configuration file
    ├── douban/         # Douban Books module
    ├── megbookhk/      # Hong Kong Books module
    ├── megbooktw/      # Taiwan Books module
    ├── amazon/         # Amazon Books module
    └── google/         # Google Books module
```

## Development Status

- [x] Douban Books search
- [x] Hong Kong Books search
- [x] Taiwan Books search
- [x] Amazon Books search
- [x] Google Books search

## Notes

1. Image host feature is optional:
   - If token.json is not configured, the program can still run normally
   - If image host is not configured, the book cover will only display the original URL
   - Configuring image host can achieve permanent storage and fast access of book covers

2. Network access notes:
   - Some search sources may require using a VPN to access
   - Please ensure your network environment is normal
   - The program includes an automatic retry mechanism, but may still be affected by network conditions

3. Search result notes:
   - The accuracy and completeness of search results depend on the real-time status of each data source
   - Different data sources may have different information
   - Suggest comparing multiple data sources

4. Performance optimization:
   - The program includes a caching mechanism to reduce repeated requests
   - Supports asynchronous processing and concurrent search
   - Automatically cleans up temporary files and cache

## FAQ

1. No search results:
   - Check if the keywords are accurate
   - Try using different search sources
   - Ensure network connection is normal

2. Image upload failed:
   - Verify token.json configuration is correct
   - Check network connection status
   - View error log for detailed information

3. Program runtime error:
   - Ensure all dependencies are installed
   - Check Python version meets requirements
   - View error log for troubleshooting
