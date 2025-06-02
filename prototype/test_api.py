# test_api.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_summarize():
    payload = {
        "messages": [
            "张三: 大家早上好",
            "李四: 请问今天作业谁做完了？"
        ]
    }
    resp = requests.post(f"{BASE_URL}/summarize", json=payload)
    print("摘要接口状态码：", resp.status_code)
    try:
        print("摘要接口返回：", resp.json())
    except ValueError:
        print("摘要接口返回非 JSON：", resp.text)

def test_reply():
    payload = {
        "messages": [
            "领导: 下午请准备报告",
            "你: 好的，我这就去准备。"
        ]
    }
    resp = requests.post(f"{BASE_URL}/reply", json=payload)
    print("回复建议接口状态码：", resp.status_code)
    try:
        print("回复建议接口返回：", resp.json())
    except ValueError:
        print("回复建议接口返回非 JSON：", resp.text)

if __name__ == "__main__":
    print("== Testing /summarize ==")
    test_summarize()
    print("\n== Testing /reply ==")
    test_reply()
