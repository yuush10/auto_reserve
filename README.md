# What's auto_reserve
This is a webhook project that enables notifications to be sent to Line when a night becomes available among the holidays on a reservation website.

# Use Case
## 1. ほったらかしキャンプ場 空き状況チェッカー

### 概要
このプロジェクトは、ほったらかしキャンプ場の空き状況を自動的にチェックし、空きが出た場合にLINE Messaging APIを使用して通知を送信するPythonスクリプトです。

### 機能
- ほったらかしキャンプ場の予約ページをスクレイピング
- 祝日前日の空き状況をチェック
- 空きが見つかった場合、LINEに通知を送信

### 必要条件
- Python 3.7以上
- pip（Pythonパッケージマネージャー）

### セットアップ
1. リポジトリをクローンします：
```
git clone https://github.com/yourusername/hottarakashi-camp-checker.git
cd hottarakashi-camp-checker
text
```

2. 仮想環境を作成し、有効化します：
```
python -m venv venv
source venv/bin/activate # Linuxの場合
venv\Scripts\activate # Windowsの場合
text
```

3. 必要なパッケージをインストールします：
```
pip install -r requirements.txt
text
```
4. `.env`ファイルを作成し、以下の環境変数を設定します：
```
CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
USER_ID=your_line_user_id
text
```
## 使用方法
スクリプトを実行します：
```
python main.py
text
```
## LINE Messaging API設定
1. [LINE Developers](https://developers.line.biz/)でアカウントを作成し、新しいチャネルを作成します。
2. Messaging API設定で、チャネルアクセストークンを取得します。
3. あなたのLINEユーザーIDを取得します。
4. これらの情報を`.env`ファイルに設定します。

## 注意事項
- このスクリプトは教育目的で作成されています。使用する際は、対象ウェブサイトの利用規約を確認してください。
- 過度な頻度でのアクセスは避けてください。

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献
プルリクエストは歓迎します。大きな変更を加える場合は、まずissueを開いて変更内容について議論してください。

## 作者
Yu Ushio

こちらのWebページを参考にさせていただきました。ありがとうございました！

Pythonで「ふもとっぱら」キャンプ場へ行き放題Botをつくってみた
https://note.com/youhei0917/n/n1d7c88b1411f

GitHubを使って（git pushで）、Netlifyでサイトを公開する
https://qiita.com/21HideK/items/584419b55e1b1941ee24