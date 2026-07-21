# カスタムドメイン設定手順（d-studylab.com → ポータル）

このポータル（リポジトリ `D-studyLab/D-studyLab.github.io`）に独自ドメインを当てる手順です。**本人が10分で実行できる粒度**で書いています。ドメインを買ってから作業してください。

> ⚠ 現時点ではドメイン未購入のため、`CNAME` ファイルはまだ作りません（作ると Pages が存在しないドメインを待って表示不能になる恐れがあるため）。本手順の Step 3 で初めて作成します。

---

## 前提

- 例として `d-studylab.com` を **Apex ドメイン（wwwなし）** で使う想定です。
- レジストラは **Cloudflare Registrar** を推奨（原価に近い・WHOIS代理・DNS管理が同じ画面）。他社で買っても DNS 設定の考え方は同じです。

---

## Step 1｜ドメインを買う（Cloudflare Registrar）

1. Cloudflare にログイン → 左メニュー **Domain Registration → Register Domains**。
2. `d-studylab.com` を検索して購入（.com はおおむね年 $10 前後）。
3. 購入すると、そのドメインは自動的に Cloudflare の DNS 管理下に入ります（ネームサーバー変更不要）。

> 他社で買った場合: そのレジストラの管理画面で下記 Step 2 の DNS レコードを設定するか、ネームサーバーを Cloudflare に向けてから Cloudflare 側で設定します。

---

## Step 2｜DNS レコードを設定する

Cloudflare の対象ドメイン → **DNS → Records** で、GitHub Pages 用のレコードを追加します。

### Apex（`d-studylab.com`）用 A レコード 4本

GitHub Pages の Apex は A レコードで4つの IP を指します。

| Type | Name | IPv4 address |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

（AAAA/IPv6 も足すとより堅牢です。任意: `2606:50c0:8000::153` / `8001::153` / `8002::153` / `8003::153`）

### `www` 用 CNAME レコード 1本

| Type | Name | Target |
|---|---|---|
| CNAME | `www` | `d-studylab.github.io` |

### ⚠ Cloudflare の「プロキシ」は最初オフに

各レコードの **Proxy status（オレンジ雲）を "DNS only"（グレー雲）** にしてください。オレンジのままだと GitHub の証明書発行が失敗することがあります。HTTPS が有効になった後にオレンジへ戻すのは任意です。

---

## Step 3｜GitHub Pages にカスタムドメインを登録

1. `github.com/D-studyLab/D-studyLab.github.io` → **Settings → Pages**。
2. **Custom domain** に `d-studylab.com` を入力して **Save**。
   - これで GitHub がリポジトリのルートに `CNAME` ファイル（中身は `d-studylab.com`）を自動コミットします。**手動で作る必要はありません。**
   - もし手動で作る場合は、リポジトリ直下に `CNAME` という名前（拡張子なし）で1行だけ `d-studylab.com` と書いたファイルを置いて push します。
3. DNS チェックが通ると「DNS check successful」と表示されます（反映に数分〜最大1日）。

---

## Step 4｜HTTPS を強制する

1. Step 3 の DNS チェック通過後、同じ Pages 画面に **Enforce HTTPS** のチェックボックスが現れます。
2. GitHub が Let's Encrypt 証明書を自動発行します（数分〜数十分）。証明書が出るまでチェックできないことがあるので、少し待ってから **Enforce HTTPS にチェック**。
3. これで `http://` アクセスも自動で `https://` にリダイレクトされます。

---

## Step 5｜確認

- `https://d-studylab.com/` が 200 で表示される
- `https://www.d-studylab.com/` が `d-studylab.com` にリダイレクトされる（GitHub が自動処理）
- 各ゲーム（`https://d-studylab.github.io/<slug>/`）は**そのまま github.io で共存**します。ポータルのカードのリンク先は現状 `d-studylab.github.io/<slug>/` を指しているので、ドメイン移行後もリンク切れは起きません（将来まとめて独自ドメインに寄せる場合は別タスクで一括変更）。

---

## トラブル時のチェックリスト

- **証明書が出ない / HTTPS強制が押せない** → Cloudflare のプロキシがオレンジになっていないか確認（DNS only にする）。数十分待つ。
- **DNS check が失敗** → A レコード4本の IP が上記と一致しているか、Name が `@`（Apex）か確認。
- **www だけ繋がらない** → `www` の CNAME が `d-studylab.github.io`（末尾ドット有無はどちらでも可）か確認。

---

作成: 2026-07-21 ／ D-studyLab
