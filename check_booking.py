import requests
from bs4 import BeautifulSoup
import hashlib
import os
import json

URL = "https://neconoshima.jp/booking/"

r = requests.get(URL, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

# 「予約フォーム」の後にある予約受付案内を取得
text = soup.get_text("\n")

start = text.find("現在、ご予約の受付は")

if start == -1:
    print("予約受付情報が見つかりませんでした")
    exit()

end = text.find("できるだけ公平にご案内できるよう", start)

if end == -1:
    end = start + 1000

booking_info = text[start:end].strip()

print("現在の予約受付情報:")
print(booking_info)

current_hash = hashlib.sha256(booking_info.encode()).hexdigest()

FILE = "hash.json"

old_hash = None

if os.path.exists(FILE):
    with open(FILE, "r") as f:
        old_hash = json.load(f).get("hash")

if old_hash is not None and current_hash != old_hash:

    webhook = os.environ["DISCORD_WEBHOOK"]

    message = (
        "🐱 **ネコノシマの予約受付情報が更新されました！**\n\n"
        + booking_info
        + "\n\n"
        + URL
    )

    requests.post(
        webhook,
        json={"content": message},
        timeout=30
    )

with open(FILE, "w") as f:
    json.dump({"hash": current_hash}, f)
