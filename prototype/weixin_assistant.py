# weixin_assistant.py

import time
import threading
import socket
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import pyperclip
from pywinauto import Application

# —— 内嵌启动 FastAPI 后端 —— 
import uvicorn
from main import app as fastapi_app

def _serve_backend():
    config = uvicorn.Config(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

# 启动后端线程
threading.Thread(target=_serve_backend, daemon=True).start()

# 等待后端就绪（最多等待 5 秒）
for _ in range(25):
    try:
        sock = socket.create_connection(("127.0.0.1", 8000), timeout=0.2)
        sock.close()
        break
    except OSError:
        time.sleep(0.2)
else:
    messagebox.showerror("启动失败", "后端服务未能启动，请检查环境")
    sys.exit(1)


# —— 程序常量 —— 
BACKEND_URL = "http://127.0.0.1:8000"
DEF_COUNT   = 100   # 默认抓取条数
DEF_WHEEL   = 30    # 默认滚轮距离
DEF_PAUSE   = 0.2   # 默认滚动后停顿（秒）
DEF_REPLY_N = 20    # 默认“回复建议”关注的最新条数


# —— 抓取微信消息 —— 
def fetch_recent_messages(count,
                          wheel_dist=DEF_WHEEL,
                          pause_seconds=DEF_PAUSE,
                          scroll_times=30):
    app = Application(backend="uia").connect(path="WeChat.exe")
    win = app.window(title_re=".*微信.*")
    win.restore(); win.set_focus()
    msg_list = win.child_window(title="消息", control_type="List")

    for _ in range(scroll_times):
        msg_list.wheel_mouse_input(wheel_dist=wheel_dist)
        time.sleep(pause_seconds)
        try:
            btn = win.child_window(title_re="查看更多.*", control_type="Button")
            if btn.exists(timeout=0.3):
                btn.click_input()
                time.sleep(pause_seconds)
        except:
            pass

    items, seen, col = msg_list.descendants(control_type="ListItem"), set(), []
    for it in items:
        if len(col) >= count:
            break
        try: uid = tuple(it.element_info.runtime_id)
        except: uid = (it.element_info.name, it.element_info.control_type)
        if uid in seen:
            continue
        seen.add(uid)
        texts = it.descendants(control_type="Text")
        if len(texts) < 2:
            continue
        sender = texts[0].window_text().strip()
        for t in texts[1:]:
            col.append(f"{sender}: {t.window_text().strip()}")
            if len(col) >= count:
                break
    return col[:count]


# —— 调用 /summarize —— 
def call_summarize(msgs, count):
    to_send = msgs[-count:]
    prompt = "请将以下消息要点以分点形式摘要：\n\n" + "\n".join(to_send)
    r = requests.post(f"{BACKEND_URL}/summarize",
                      json={"messages":[prompt]},
                      timeout=60)
    r.raise_for_status()
    summary = r.json().get("summary","")
    return "\n".join(f"• {ln.strip()}"
                     for ln in summary.replace("。","。\n").splitlines()
                     if ln.strip())


# —— 调用 /reply —— 
def call_reply(msgs, user_id, count):
    recent = msgs[-count:]
    prompt = (
        f"用户ID：{user_id}\n"
        f"以下是最新的 {len(recent)} 条消息：\n\n"
        + "\n".join(recent)
        + "\n\n请基于以上内容，为非用户本人生成三条礼貌回复："
    )
    r = requests.post(f"{BACKEND_URL}/reply",
                      json={"messages":[prompt]},
                      timeout=60)
    r.raise_for_status()
    return r.json().get("suggestions", [])


# —— GUI 主类 —— 
class WeChatAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice of Priestess")
        self.geometry("500x600")
        self.resizable(False, False)

        # 模式
        self.mode_var = tk.StringVar(value="both")
        mf = ttk.LabelFrame(self, text="模式设置", padding=10)
        mf.pack(fill="x", padx=10, pady=(10,5))
        for txt,val in [("摘要","summarize"),("回复","reply"),("摘要+回复","both")]:
            ttk.Radiobutton(mf, text=txt, variable=self.mode_var, value=val).pack(side="left", padx=5)

        # 参数
        p = ttk.Frame(self); p.pack(fill="x", padx=10, pady=5)
        ttk.Label(p, text="抓取条数:").grid(row=0,col=0,sticky="e")
        self.count_entry = ttk.Entry(p, width=6); self.count_entry.grid(row=0,col=1)
        self.count_entry.insert(0, DEF_COUNT)
        ttk.Label(p, text=" 用户ID:").grid(row=0,col=2,sticky="e")
        self.id_entry = ttk.Entry(p, width=12); self.id_entry.grid(row=0,col=3)
        self.id_entry.insert(0, "my_wechat_id")
        ttk.Label(p, text=" 回复条数:").grid(row=0,col=4,sticky="e")
        self.reply_n_entry = ttk.Entry(p, width=6); self.reply_n_entry.grid(row=0,col=5)
        self.reply_n_entry.insert(0, DEF_REPLY_N)

        # 开始按钮
        self.start_btn = ttk.Button(self, text="开始", command=self.on_start)
        self.start_btn.pack(pady=10)

        # 结果 Notebook
        nb = ttk.Notebook(self); nb.pack(fill="both",expand=True,padx=10,pady=10)
        self.sum_text = scrolledtext.ScrolledText(nb, wrap="word")
        self.rep_text = scrolledtext.ScrolledText(nb, wrap="word")
        nb.add(self.sum_text, text="摘要"), nb.add(self.rep_text, text="回复")

    def on_start(self):
        try:
            cnt    = int(self.count_entry.get())
            uid    = self.id_entry.get().strip()
            replyn = int(self.reply_n_entry.get())
        except ValueError:
            messagebox.showerror("输入错误","请确保数值格式正确，ID 不能为空")
            return
        self.start_btn.config(state="disabled")
        threading.Thread(target=self.run_task, args=(cnt,uid,replyn), daemon=True).start()

    def run_task(self, cnt, uid, replyn):
        try:
            msgs = fetch_recent_messages(cnt)
            if self.mode_var.get() in ("summarize","both"):
                s = call_summarize(msgs, cnt)
                self.sum_text.delete("1.0","end"); self.sum_text.insert("1.0",s)
            if self.mode_var.get() in ("reply","both"):
                rs = call_reply(msgs, uid, replyn)
                self.rep_text.delete("1.0","end")
                for i,x in enumerate(rs,1):
                    self.rep_text.insert("end",f"{i}. {x}\n")
        except Exception as e:
            messagebox.showerror("运行错误", str(e))
        finally:
            self.start_btn.config(state="normal")


if __name__ == "__main__":
    WeChatAssistant().mainloop()
