# main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise RuntimeError("请在 .env 文件中设置 DEEPSEEK_API_KEY")

# 初始化 FastAPI 应用
app = FastAPI(title="ChatSense Backend with DeepSeek")

# 请求模型
class Messages(BaseModel):
    messages: list[str]

# DeepSeek 调用封装
async def call_deepseek(prompt: str, system_prompt: str):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt}
        ],
        "stream": False
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=body)
        # 如果状态不是 2xx，就把返回体一并抛给客户端
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            detail = resp.text or f"{resp.status_code} Error"
            raise HTTPException(status_code=resp.status_code, detail=detail)
        # 解析 JSON，否则报错
        try:
            return resp.json()
        except ValueError:
            raise HTTPException(status_code=500, detail="DeepSeek 返回了非 JSON 响应")

# 摘要接口
@app.post("/summarize")
async def summarize(msgs: Messages):
    prompt = (
        "请你扮演一个微信聊天助手，\n"
        "以下是一段未读消息列表，请帮忙提炼成一段简洁的要点摘要：\n\n"
        + "\n".join(msgs.messages)
        + "\n\n摘要："
    )
    data = await call_deepseek(prompt, system_prompt="You are a helpful assistant.")
    summary = data["choices"][0]["message"]["content"].strip()
    return {"summary": summary}

# 回复建议接口
@app.post("/reply")
async def reply(msgs: Messages):
    prompt = (
        "你是一个礼貌得体的微信助手，\n"
        "下面是当前聊天的上下文，请基于此给出三条适合的、措辞礼貌的回复建议：\n\n"
        + "\n".join(msgs.messages)
        + "\n\n回复建议：\n1."
    )
    data = await call_deepseek(prompt, system_prompt="You are a polite assistant.")
    content = data["choices"][0]["message"]["content"].strip()
    suggestions = [line.strip() for line in content.splitlines() if line.strip()]
    return {"suggestions": suggestions}
