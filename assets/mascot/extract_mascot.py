# -*- coding: utf-8 -*-
"""
マスコット素材の切り出し+透過化（仕様書v3.8 §16.2）
入力: penguin_refs/kingchan_素材集_v1_原本.png（2730x1536・本人生成AI画像・リポジトリ外）
出力: assets/mascot/*.webp（各ポーズ透過・≤40KB目標）
手順: ①ポーズ矩形で切り出し ②外周からのフラッドフィルで薄青背景を除去（色距離）
      ③最大連結成分のみ残す（雪の結晶・文字ラベル・影の孤島を除去）
      ④マスク1px収縮+ぼかしでエッジのアンチエイリアスを保つ
再生成: python extract_mascot.py <素材集PNGのパス>
"""
import sys, os
from collections import deque
from PIL import Image, ImageFilter

SRC = sys.argv[1] if len(sys.argv) > 1 else r"D:\共有フォルダ\02_Human_Notes\Projects\自作プロダクト構想\penguin_refs\kingchan_素材集_v1_原本.png"
OUT = os.path.dirname(os.path.abspath(__file__))
SCALE = 1.365  # 表示座標(2000x1125)→原寸(2730x1536)

# ポーズ矩形（表示座標系で指定）
BOXES = {
    'front':  (60, 50, 350, 460),
    'side1':  (420, 50, 700, 460),
    'side2':  (1380, 50, 1640, 460),
    'back':   (1650, 50, 1950, 460),
    'walk':   (60, 480, 350, 800),
    'slide1': (400, 490, 700, 790),
    'slide2': (1300, 550, 1710, 790),
    'greet':  (1700, 480, 1995, 800),
    'tilt':   (60, 820, 355, 1110),
    'clap1':  (430, 820, 700, 1110),
    'clap2':  (1380, 820, 1665, 1110),
    'sleep':  (1670, 850, 1995, 1115),
    'hero':   (740, 180, 1340, 1090),
}
# 出力の最大高さ（用途別・重量≤40KBのための縮小）
MAXH = {'hero': 720, 'front': 560, 'blink': 560, 'greet': 560, 'tilt': 560, 'sleep': 420}
DEFAULT_MAXH = 380


def cutout(im, box):
    x0, y0, x1, y1 = [int(v * SCALE) for v in box]
    tile = im.crop((x0, y0, x1, y1)).convert('RGBA')
    w, h = tile.size
    px = tile.load()
    # 背景色=四隅の平均
    corners = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))

    def is_bg(p, tol):
        return (p[0] - bg[0]) ** 2 + (p[1] - bg[1]) ** 2 + (p[2] - bg[2]) ** 2 < tol * tol

    # ①外周フラッドフィルで背景除去（影の淡青も食うよう許容広め・キャラは濃色輪郭で守られる）
    mask = [[False] * w for _ in range(h)]      # True=背景
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not mask[y][x] and is_bg(px[x, y], 70):
                mask[y][x] = True; q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not mask[y][x] and is_bg(px[x, y], 70):
                mask[y][x] = True; q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0 <= nx < w and 0 <= ny < h and not mask[ny][nx] and is_bg(px[nx, ny], 70):
                mask[ny][nx] = True; q.append((nx, ny))
    # ②最大連結成分（前景）以外を除去=雪・文字・影の島
    seen = [[False] * w for _ in range(h)]
    best, bestn = [], 0
    for sy in range(h):
        for sx in range(w):
            if mask[sy][sx] or seen[sy][sx]:
                continue
            comp = []
            q2 = deque([(sx, sy)]); seen[sy][sx] = True
            while q2:
                x, y = q2.popleft(); comp.append((x, y))
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and not mask[ny][nx]:
                        seen[ny][nx] = True; q2.append((nx, ny))
            if len(comp) > bestn:
                best, bestn = comp, len(comp)
    keep = [[False] * w for _ in range(h)]
    for x, y in best:
        keep[y][x] = True
    # ③アルファ生成: 1px収縮→1pxぼかしでAAエッジを再現
    m = Image.new('L', (w, h), 0)
    mp = m.load()
    for y in range(h):
        for x in range(w):
            if keep[y][x]:
                mp[x, y] = 255
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    tile.putalpha(m)
    # ④タイトにトリム
    bbox = m.getbbox()
    return tile.crop(bbox) if bbox else tile


def make_blink():
    """瞬きフレーム自作（§16.2-2）: heroの目を頭色で塗り潰し→閉じ目の弧を描く"""
    from PIL import ImageDraw
    im = Image.open(os.path.join(OUT, 'hero.webp')).convert('RGBA')
    ex, ey, er = 219, 159, 16                   # 目の中心と塗り潰し半径
    head = im.getpixel((ex - er - 12, ey))      # 目の左横の頭スレート色をサンプル
    d = ImageDraw.Draw(im)
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=head)
    # 閉じ目=下向きの弧（太さ5px・キャラの輪郭色に合わせた濃色）
    d.arc([ex - 14, ey - 16, ex + 14, ey + 10], start=25, end=155, fill=(34, 34, 44, 255), width=5)
    p = os.path.join(OUT, 'blink.webp')
    im.save(p, 'WEBP', quality=88, method=6)
    print('blink', im.size, os.path.getsize(p), 'bytes')


def main():
    im = Image.open(SRC)
    for name, box in BOXES.items():
        t = cutout(im, box)
        mh = MAXH.get(name, DEFAULT_MAXH)
        if t.height > mh:
            t = t.resize((round(t.width * mh / t.height), mh), Image.LANCZOS)
        p = os.path.join(OUT, name + '.webp')
        t.save(p, 'WEBP', quality=88, method=6)
        print(name, t.size, os.path.getsize(p), 'bytes')
    make_blink()


if __name__ == '__main__':
    main()
