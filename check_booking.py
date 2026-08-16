import requests
import os

webhook = os.environ["DISCORD_WEBHOOK"]

requests.post(
    webhook,
    json={
        "content": "🐱 テスト通知です！\nネコノシマ予約監視システムから正常に通知できています。"
    },
    timeout=30
)
