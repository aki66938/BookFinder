# BookFinder 📚

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)

[English](README_EN.md) | [中文](README.md)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [System Requirements](#system-requirements)
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
  - 📚 Hong Kong American Bookstore
  - 📚 Taiwan American Bookstore
  - 📚 Amazon Books
  - 📚 Google Books

- **Rich Book Information**
  - 📖 Basic Info: Title, Author, Publisher, Publication Year, ISBN, etc.
  - 📝 Detailed Description: Content Summary, Author Introduction
  - 🖼️ Image Resources: Book Cover (Auto-upload to Image Host)
  - 🔗 Book Link Generation

- **Adaptive Information Extraction**
  - ✨ Automatic Text Cleaning and Formatting
  - 🎯 Adaptive Recognition and Key Information Extraction
  - 🔄 Handle Multiple Data Formats and Encodings

- **Error Handling**
  - ⚡ Exception Handling Mechanism
  - 🔄 Automatic Retry Mechanism
  - 📝 Detailed Error Logging

## System Requirements

- Python 3.8+
- Windows Operating System
- Internet Access (Some book data sources may require VPN)

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
   Modify the configuration items in the `.env` file as needed

## Usage

1. Configure environment variables:
   
   Copy the `.env.template` file and rename it to `.env`, then modify the configuration as needed:

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

   If image host feature is not enabled (IMGHOST_ENABLED=false), the program will only display local paths for images.

2. Run the main program:
```bash
python main.py
```

3. Select search source:
   - 1: Douban Books
   - 2: Hong Kong American Bookstore
   - 3: Taiwan American Bookstore
   - 4: Amazon Books
   - 5: Google Books
   - 0: Return

4. Enter search keywords:
   - Supports book title, author, ISBN, etc.
   - Recommend using accurate book title or ISBN for search
   - Empty input will return to source selection

5. View search results:
   - Display the list of basic information of matched books
   - Input the serial number to view detailed information
   - Input 'b' to return to search
   - Invalid input will prompt to re-select

## Project Structure

```
db_book_search/
├── main.py              # Main program entry
├── config.py            # Main configuration file
├── get_token.py         # Image host token acquisition tool
├── requirements.txt     # Dependencies list
├── token.json          # Image host token config (optional)
└── sources/            # Data source modules
    ├── utils.py        # Common utility functions
    ├── image.py        # Image processing module
    ├── output.py       # Output formatting module
    ├── config.py       # Data source config file
    ├── douban/         # Douban Books module
    ├── megbookhk/      # Hong Kong American Bookstore module
    ├── megbooktw/      # Taiwan American Bookstore module
    ├── amazon/         # Amazon Books module
    └── google/         # Google Books module
```

## Development Status

- [x] Douban Books Search
- [x] Hong Kong American Bookstore Search
- [x] Taiwan American Bookstore Search
- [x] Amazon Books Search
- [x] Google Books Search

## Notes

1. Image host feature is optional:
   - The program can still run normally without token.json
   - Without image host configuration, book covers will only show original URLs
   - Configuring image host enables permanent storage and quick access to covers

2. Network Access Notes:
   - Some search sources may require VPN access
   - Please ensure your network environment is normal
   - The program includes automatic retry mechanism but may still be affected by network conditions

3. Search Results Notes:
   - The accuracy and completeness of search results depend on the real-time status of each data source
   - Information may vary between different data sources
   - Recommend cross-comparing information from multiple data sources

## License

This project is for learning and research purposes only, commercial use is prohibited. When using this project, please comply with the terms of use and regulations of relevant websites.

## Open Source License

This project is licensed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for details.
