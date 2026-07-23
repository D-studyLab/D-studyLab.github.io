# -*- coding: utf-8 -*-
"""ルートOGP画像を生成する（マスコット入り）。
使い方: python assets/mascot/make_ogp.py
マスコットや文言を変えたら再実行して og.png を作り直す。"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG      = (12, 13, 18)     # 黒鉛
PANEL   = (20, 22, 29)
AMBER   = (232, 163, 61)   # 琥珀
AMBER_L = (245, 185, 92)
TXT     = (237, 235, 230)  # 暖白
SUB     = (154, 152, 144)

BOLD = r"C:\Windows\Fonts\YuGothB.ttc"
MED  = r"C:\Windows\Fonts\YuGothM.ttc"

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# 背景: 右下へ向かうごく淡いグラデーション
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)],
           fill=(int(BG[0] + 10 * t), int(BG[1] + 11 * t), int(BG[2] + 15 * t)))

# 左端の琥珀のアクセントバー
d.rectangle([0, 0, 10, H], fill=AMBER)

# マスコット（右側に大きく）
m = Image.open("assets/mascot/hero.webp").convert("RGBA")
mh = 470
mw = int(m.width * mh / m.height)
m = m.resize((mw, mh), Image.LANCZOS)
img.paste(m, (W - mw - 80, H - mh - 60), m)

# テキスト
f_logo = ImageFont.truetype(BOLD, 40, index=0)
f_head = ImageFont.truetype(BOLD, 62, index=0)
f_sub  = ImageFont.truetype(MED, 25, index=0)

x = 74
d.text((x, 92), "D-studyLab", font=f_logo, fill=AMBER)
d.text((x, 196), "考えたら、作る。", font=f_head, fill=TXT)
d.text((x, 276), "作ったら、出す。", font=f_head, fill=TXT)
d.line([(x, 384), (x + 120, 384)], fill=AMBER_L, width=3)
d.text((x, 414), "ブラウザゲーム・ブログ・お店のウェブ制作", font=f_sub, fill=SUB)
d.text((x, 454), "研究とものづくりを行き来する個人ラボ", font=f_sub, fill=SUB)

img.save("og.png", optimize=True)
print("wrote og.png", img.size)
