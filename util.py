import re
from markdown import markdown
from bs4 import BeautifulSoup

def clean_text(text: str) -> str:
    """
    文本预处理：
    1. 去除所有URL
    2. 转换Markdown为纯文本
    3. 去除多余空白字符
    """
    if not text:
        return ""

    # 去除URL（保留被 [] 包裹的文本）
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # Markdown转HTML再提取纯文本
    html = markdown(text)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")

    # 可选：其他清洗规则
    text = re.sub(r'\s+', ' ', text).strip()  # 合并连续空白
    text = re.sub(r'\[([^\]]+)\]', r'\1', text)  # 去除方括号但保留内容

    return text