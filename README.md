# Echo AI微信助手 / Echo AI WeChat Assistant

> **中文说明**  
> Echo AI 是一个基于 Python 的桌面应用，旨在帮助用户高效地处理微信聊天记录。  
> 它提供以下两项核心功能：  
> 1. **聊天摘要**：提取聊天记录中的核心内容，并以流畅、连贯、自然的中文段落进行总结。  
> 2. **智能回复建议**：基于最新的聊天内容，生成三条措辞得体、体现高情商的回复选项。  
>  
> 本应用调用 DeepSeek 语言模型 API 完成自然语言处理，最终通过 PyInstaller 打包成独立可执行文件，用户可以直接双击运行，无需额外后端服务。  

> **English Explanation**  
> Echo AI is a Python-based desktop application designed to help users efficiently handle WeChat conversation logs.  
> It provides two core features:  
> 1. **Chat Summarization**: Extracts the core points from a chat history and produces a fluent, coherent Chinese summary paragraph.  
> 2. **Smart Reply Suggestions**: Generates three polite, emotionally intelligent reply options based on the latest chat content.  
>  
> The app leverages the DeepSeek language model API for natural language processing and is packaged into a standalone executable with PyInstaller. Users can run it directly without any additional backend service.

---

## 目录 / Table of Contents

1. [项目特点 / Features](#项目特点--features)  
2. [环境要求 / Requirements](#环境要求--requirements)  
3. [安装与运行 / Installation & Usage](#安装与运行--installation--usage)  
4. [打包为可执行文件 / Packaging as Executable](#打包为可执行文件--packaging-as-executable)  
5. [使用说明 / How to Use](#使用说明--how-to-use)  
6. [数据安全与隐私 / Data Security & Privacy](#数据安全与隐私--data-security--privacy)  
7. [贡献指南 / Contributing](#贡献指南--contributing)  
8. [许可证 / License](#许可证--license)  
9. [联系方式 / Contact](#联系方式--contact)  

---

## 项目特点 / Features

- **聊天摘要 / Chat Summarization**  
  - 自动提取聊天记录中的关键点，生成简洁明了的摘要段落。  
  - Automatically extracts key points from chat logs and produces a concise summary paragraph.

- **智能回复 / Smart Reply Suggestions**  
  - 提供三条风格多样、措辞得体的回复选项，帮助用户快速应对对话。  
  - Offers three diverse, well‐phrased reply options to help users respond quickly in conversations.

- **简洁界面 / Simple UI**  
  - 直观易用的图形界面，用户仅需选择模式、输入参数，即可完成操作。  
  - Intuitive graphical interface: users select a mode, enter parameters, and get results.

- **可复制 & 可定制 / Copyable & Customizable**  
  - 生成的摘要与回复可以一键复制，方便粘贴到微信中。  
  - Summaries and replies can be copied with one click for easy pasting into WeChat.

---

## 环境要求 / Requirements

- **操作系统 / OS**:  
  - Windows 10 或更高版本  
  - Windows 10 or higher

- **Python 版本 / Python Version**:  
  - Python 3.8 或更高  
  - Python 3.8 or later

- **依赖库 / Python Packages**:  
  ```text
  pywinauto
  requests
  python-dotenv
  pyperclip

##  使用说明 / How to Use
-**1.打开微信聊天窗口。**
-**1.Open the WeChat conversation window.**

-**2.双击exe文件启动 Echo AI。**
-**2.Launch the Echo AI by double clicking the exe file.**

-**3.在“模式设置”中选择：**

  - “摘要模式”：仅生成聊天摘要。

  - “智能回复模式”：仅生成回复建议。

  - “摘要+回复模式”：同时生成摘要和回复。
-**3.Select a mode under “Mode Settings”:**

  - “Summarize Mode”: Generate only the summary.

  - “Smart Reply Mode”: Generate only reply suggestions.

  - “Both Mode”: Generate both summary and replies.

-**4.在“自定义参数设置”中输入：**

  - 抓取消息数：要从微信中抓取的历史消息数量。

  - 用户 ID：您的微信昵称或唯一标识，用于避免模型对自己生成回复。

  - 回复参考消息数：模型仅针对最近 N 条消息生成回复建议。
-**4.Enter in “Custom Parameters”:**

  - Fetch Count: Number of historical messages to fetch from WeChat.

  - User ID: Your WeChat nickname or unique identifier to prevent the model from replying to yourself.

  - Reply Reference Count: Number of most recent messages to use as context for generating reply suggestions.

-**5.点击“开始”按钮，程序将：**

  - 自动切换到微信窗口并滚动加载历史消息。

  - 调用 DeepSeek API 生成摘要和/或回复建议。

  - 在下方标签页展示结果，可一键复制。
-**5.Click “Start” and the application will:**

  - Automatically switch to the WeChat window and scroll to load historical messages.

  - Call the DeepSeek API to generate the summary and/or reply suggestions.

  - Display results in the tabs below for easy copy & paste.
