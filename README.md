# Student-Plaza-3F-VISA-Extension
学生プラザ３F 在留期間更新に関する書類

## 使い方
## Web版
GitHub Pages 上で動作する静的版を用意しました。ページを開くだけで利用できます。

- 公開URL: https://senamatsuda.github.io/Student-Plaza-3F-VISA-Extension/
- 使い方: 身分 → 状況 → 奨学金区分（任意）の順にプルダウンを選ぶと必要書類が表示されます。

### ローカルで Flask サーバーを動かす場合（任意）
`web_app.py` は、Web UI をローカルで動かしたい場合に利用できます。

1. 依存関係（Flask）のインストール
   ```
   pip install flask
   ```
2. サーバーを起動
   ```
   python web_app.py --host 0.0.0.0 --port 5000
   ```
3. ブラウザでアクセス
   `http://localhost:5000` を開き、身分→状況→奨学金区分の順に選ぶと必要書類が表示されます。
