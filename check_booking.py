import requests
from bs4 import BeautifulSoup
import hashlib
import os
import json
import time

URL = "https://neconoshima.jp/booking/"

# 最大3回アクセスを試す
for attempt in range(3):
    try:
        r = requests.get(
            URL,
            timeout=(10, 20),
            headers={
                "User-Agent": "Mozilla/5.0 (Neconoshima Booking Monitor)"
            }
        )
        r.raise_for_status()
        break

    except requests.RequestException as e:
        print(f"アクセス失敗 {attempt + 1}/3: {e}")

        if attempt == 2:
            raise

        time.sleep(5)

soup = BeautifulSoup(r.text, "html.parser")

text = soup.get_text("\n")

# 予約受付案内だけを取得
start = text.find("現在、ご予約の受付は")

if start == -1:
    print("予約受付情報が見つかりませんでした")
    exit()

end = text.find("できるだけ公平にご案内できるよう", start)

if end == -1:
    end = start + 1500

booking_info = text[start:end].strip()

print("現在の予約受付情報:")
print(booking_info)

current_hash = hashlib.sha256(
    booking_info.encode()
).hexdigest()

FILE = "hash.json"

old_hash = None

if os.path.exists(FILE):
    with open(FILE, "r") as f:
        old_hash = json.load(f).get("hash")

# 初回は記録だけ
# 2回目以降、内容が変わったらDiscord通知
if old_hash is not None and current_hash != old_hash:

    webhook = os.environ["DISCORD_WEBHOOK"]

    message = (
        "🐱 **ネコノシマの予約受付情報が更新されました！**\n\n"
        + booking_info
        + "\n\n"
        + URL
    )

    response = requests.post(
        webhook,
        json={"content": message},
        timeout=30
    )

    response.raise_for_status()

with open(FILE, "w") as f:
    json.dump({"hash": current_hash}, f)
