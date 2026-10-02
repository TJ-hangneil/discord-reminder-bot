import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

import asyncio
from datetime import datetime
import discord
from discord import app_commands

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
  await tree.sync()
  print(f"ログインしました: {client.user}")


@tree.command(
    name="remind", description="指定した日時にDMでリマインダーを送信します"
)
@app_commands.describe(
    date="日時（例: 2026-10-03 15:30 または 10/03 15:30）",
    content="リマインドする内容",
)
async def remind(
    interaction: discord.Interaction, date: str, content: str
):
  # 1. 入力された日時文字列をdatetimeオブジェクトに変換
  try:
    # 年が省略された場合は今年（2026年）として処理する
    if len(date.split()[0]) <= 5:  # "MM/DD HH:MM" のような形式を想定
      date_str = f"2026-{date}"
      dt = datetime.strptime(date_str, "%Y-%m/%d %H:%M")
    else:
      dt = datetime.strptime(date, "%Y-%m-%d %H:%M")
  except ValueError:
    await interaction.response.send_message(
        "日時の形式が正しくないよ！ 例: `10/03 15:30` または `2026-10-03"
        " 15:30` のように入力してね。",
        ephemeral=True,
    )
    return

  # 2. 未来の時間かどうかチェック
  now = datetime.now()
  wait_seconds = (dt - now).total_seconds()

  if wait_seconds <= 0:
    await interaction.response.send_message(
        "過去の日時は指定できないよ！未来の時間を指定してね。", ephemeral=True
    )
    return

  # 3. 予約完了のメッセージを送信
  await interaction.response.send_message(
      f"✅ リマインダーを設定したよ！\n**日時:** {dt.strftime('%Y年%m月%d日 %H時%M分')}\n**内容:** {content}",
      ephemeral=True,
  )

  # 4. 指定時間までバックグラウンドで待機
  await asyncio.sleep(wait_seconds)

  # 5. 時間になったらDMを送信
  try:
    user = interaction.user
    await user.send(f"⏰ **リマインダー時間だよ！**\n\n{content}")
  except discord.Forbidden:
    # ユーザーがDMをブロックしている場合などのエラー対策
    print(f"{interaction.user.name} さんのDMに送信できませんでした。")


# パソコンの秘密のメモ帳からトークンを引っ張ってくる
token = os.getenv("DISCORD_TOKEN")
client.run(token)