# weixin_assistant.py

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import requests
import pyperclip
from pywinauto import Application
from dotenv import load_dotenv

# ========== 加载 DeepSeek API Key ==========
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    messagebox.showerror("配置错误", "请在 .env 文件中设置 DEEPSEEK_API_KEY")
    exit(1)

# ========== DeepSeek 同步调用函数 ==========
def call_deepseek_sync(prompt: str, system_prompt: str) -> str:
    """
    直接调用 DeepSeek ChatCompletions 接口，返回 AI 生成的文本。
    """
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt}
        ],
        "stream": False
    }
    resp = requests.post(url, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # DeepSeek 返回结构： { choices: [ { message: { content: "..." } } ] }
    return data["choices"][0]["message"]["content"].strip()

# ========== 程序常量（可按需调整） ==========
DEF_COUNT   = 100   # 默认要抓取的微信消息总条数
DEF_WHEEL   = 30    # 鼠标滚轮一次滚动的距离（正数向上）
DEF_PAUSE   = 0.2   # 每次滚动后暂停时长（秒）
DEF_REPLY_N = 20    # 默认“回复建议”要聚焦的最新消息条数

# ========== 抓取微信消息 ==========
def fetch_recent_messages(count, wheel_dist=DEF_WHEEL, pause_seconds=DEF_PAUSE, scroll_times=30):
    """
    抓取微信当前窗口中最近 `count` 条消息（“发送者: 内容”格式）。
    通过 wheel_mouse_input 滚轮 scroll_times 次，点击“查看更多”加载更多，再全量收集 ListItem。
    """
    app = Application(backend="uia").connect(path="WeChat.exe")
    win = app.window(title_re=".*微信.*")
    win.restore()
    win.set_focus()

    msg_list = win.child_window(title="消息", control_type="List")

    # 先滚动若干次加载历史消息
    for _ in range(scroll_times):
        msg_list.wheel_mouse_input(wheel_dist=wheel_dist)
        time.sleep(pause_seconds)
        # 如果弹出“查看更多”按钮，点击加载更多
        try:
            more_btn = win.child_window(title_re="查看更多.*", control_type="Button")
            if more_btn.exists(timeout=0.3):
                more_btn.click_input()
                time.sleep(pause_seconds)
        except:
            pass

    # 收集所有可见的 ListItem，将其转换成 "发送者: 内容" 形式
    items = msg_list.descendants(control_type="ListItem")
    collected = []
    seen_uids = set()
    for it in items:
        if len(collected) >= count:
            break
        try:
            uid = tuple(it.element_info.runtime_id)
        except:
            uid = (it.element_info.name, it.element_info.control_type)
        if uid in seen_uids:
            continue
        seen_uids.add(uid)

        texts = it.descendants(control_type="Text")
        if len(texts) < 2:
            continue
        sender = texts[0].window_text().strip()
        for txt in texts[1:]:
            content = txt.window_text().strip()
            collected.append(f"{sender}: {content}")
            if len(collected) >= count:
                break

    return collected[:count]

def call_summarize(msgs, count):
    """
    对最后 count 条聊天记录进行流畅、连贯、自然的中文段落式总结。
    """
    to_send = msgs[-count:]
    prompt = (
        "请将以下聊天记录的核心内容以一段流畅、连贯、自然的中文段落进行总结：\n\n"
        + "\n".join(to_send)
    )
    # 优化后的系统提示：提示模型要抓住主要讨论点、结论、行动项或共识
    system_prompt = (
        "你是一个擅长提炼会议/聊天要点的助手。"
        "总结时要抓住主要讨论点、关键结论、行动项或重要共识；"
        "避免简单罗列或逐条复述，语言要精炼、逻辑清晰；"
        "忽略无关寒暄、重复或跑题内容；"
        "重点突出最终达成的结果、需要跟进的事项或存在的分歧。"
    )
    raw = call_deepseek_sync(prompt, system_prompt)
    # 将模型返回的自然段直接输出
    return raw


def call_reply(msgs, user_id, count):
    """
    只针对最新 count 条聊天记录生成 3 条措辞得体、高情商的回复选项。
    """
    recent = msgs[-count:]
    prompt = (
        f"以下是最新的 {len(recent)} 条聊天记录（时间由旧到新）：\n\n"
        + "\n".join(recent)
        + "\n\n请为非“{user_id}”的用户生成 3 条措辞得体、体现高情商的回复。"
        " 不要在回复里提及 “{user_id}” 本人，也不要赞扬“{user_id}”。"
        "\n请按以下格式输出：\n"
        "1. 回复文本\n"
        "2. 回复文本\n"
        "3. 回复文本\n"
    )
    system_prompt = (
        "你是一个高情商的回复生成助手。生成回复时请遵循：\n"
        "1. 尊重与同理心：展现对对方的理解与尊重；\n"
        "2. 积极正面：语言积极、建设性，避免负面或指责性词汇；\n"
        "3. 清晰明确：目的明确，避免含糊；\n"
        "4. 分寸感：语气恰当，符合双方关系与语境；\n"
        "5. 解决问题导向：聚焦推进对话或解决问题；\n"
        "生成的三条回复必须在侧重点或表达方式上有所区分，"
        "并且都紧密结合聊天记录中的具体信息，避免千篇一律。"
    )
    raw = call_deepseek_sync(prompt, system_prompt)

    # 只保留以“1.”、“2.”、“3.”开头的三行。若对方返回不带序号，则按首三行分割。
    lines = raw.splitlines()
    numbered = [line.strip() for line in lines if line.strip().startswith(("1.", "2.", "3."))]
    if len(numbered) >= 3:
        return numbered[:3]
    # 如果没有找到对应序号，则 fallback：取前三个非空行
    plain = [line.strip() for line in lines if line.strip()]
    return plain[:3]

# ========== GUI 主类 ==========
class WeChatAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Echo AI")
        self.geometry("600x700")            # 窗口变大一些
        self.resizable(False, False)

        # 模式选择（“摘要”“回复”“助手”）
        self.mode_var = tk.StringVar(value="both")
        mode_frame = ttk.LabelFrame(self, text="模式设置", padding=10)
        mode_frame.pack(fill="x", padx=10, pady=(10,5))
        for txt, val in [("摘要模式", "summarize"), ("智能回复模式", "reply"), ("摘要+回复模式", "both")]:
            ttk.Radiobutton(mode_frame, text=txt, variable=self.mode_var, value=val).pack(side="left", padx=5)

        # 参数行：抓取条数、用户ID、回复条数（纵向排列）
        param_frame = ttk.LabelFrame(self, text="自定义参数设置", padding=10)
        param_frame.pack(fill="x", padx=10, pady=(5,10))

        # 抓取条数
        ttk.Label(param_frame, text="抓取消息数:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.count_entry = ttk.Entry(param_frame, width=10)
        self.count_entry.grid(row=0, column=1, padx=5, pady=5)
        self.count_entry.insert(0, str(DEF_COUNT))

        # 用户ID
        ttk.Label(param_frame, text="用户 ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.id_entry = ttk.Entry(param_frame, width=20)
        self.id_entry.grid(row=1, column=1, padx=5, pady=5)
        self.id_entry.insert(0, "my_wechat_id")

        # 回复条数
        ttk.Label(param_frame, text="回复参考消息数:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.reply_n_entry = ttk.Entry(param_frame, width=10)
        self.reply_n_entry.grid(row=2, column=1, padx=5, pady=5)
        self.reply_n_entry.insert(0, str(DEF_REPLY_N))

        # 开始按钮
        self.start_btn = ttk.Button(self, text="开始", command=self.on_start)
        self.start_btn.pack(pady=10)

        # 结果展示：两个标签页
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.sum_text = scrolledtext.ScrolledText(self.nb, wrap="word")
        self.rep_text = scrolledtext.ScrolledText(self.nb, wrap="word")
        self.nb.add(self.sum_text, text="摘要")
        self.nb.add(self.rep_text, text="回复")

    def on_start(self):
        try:
            cnt    = int(self.count_entry.get())
            uid    = self.id_entry.get().strip()
            replyn = int(self.reply_n_entry.get())
        except ValueError:
            messagebox.showerror("输入错误", "抓取条数和回复条数必须为数字，ID 不能为空")
            return

        self.start_btn.config(state="disabled")
        threading.Thread(target=self.run_task, args=(cnt, uid, replyn), daemon=True).start()

    def run_task(self, cnt, uid, replyn):
        try:
            msgs = fetch_recent_messages(cnt)

            if self.mode_var.get() in ("summarize", "both"):
                summary = call_summarize(msgs, cnt)
                self.sum_text.delete("1.0", "end")
                self.sum_text.insert("1.0", summary)

            if self.mode_var.get() in ("reply", "both"):
                suggestions = call_reply(msgs, uid, replyn)
                self.rep_text.delete("1.0", "end")
                for i, line in enumerate(suggestions, 1):
                    self.rep_text.insert("end", f"{i}. {line}\n")

        except Exception as e:
            messagebox.showerror("运行错误", str(e))
        finally:
            self.start_btn.config(state="normal")


if __name__ == "__main__":
    WeChatAssistant().mainloop()