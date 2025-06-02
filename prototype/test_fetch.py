# test_fetch.py
# 测试 WeChat 消息抓取功能

import argparse
from weixin_capture import connect_wechat, fetch_recent_messages

def main(count, wheel, pause):
    app = connect_wechat()
    if not app:
        print("无法连接到微信，请检查。")
        return

    print(f"开始测试：抓取最近 {count} 条消息 (wheel={wheel}, pause={pause})...")
    msgs = fetch_recent_messages(app, count, wheel_dist=wheel, pause_seconds=pause)
    total = len(msgs)
    print(f"共抓取到 {total} 条消息。\n")

    sample = min(10, total)
    print(f"前 {sample} 条消息示例：")
    for i, m in enumerate(msgs[:sample], 1):
        print(f"{i}. {m}")
    if total > sample:
        print(f"... 还有 {total - sample} 条未显示")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=100)
    parser.add_argument('--wheel', type=int, default=10)
    parser.add_argument('--pause', type=float, default=0.3)
    args = parser.parse_args()
    main(args.count, args.wheel, args.pause)
