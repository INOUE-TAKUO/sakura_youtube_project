##日本の桜に関する動画自動アップロードスクリプト

このリポジトリは、日本の桜に関する動画を自動でYouTubeにアップロードするスクリプトを含んでいます。

ディレクトリ構成

.
├── video/    # 動画ファイルを保存するディレクトリ
├── music/    # BGM音源ファイルを保存するディレクトリ
├── script/   # 動画生成およびYouTubeアップロード用スクリプト
├── config/   # 設定ファイルを保存
└── README.md # 本ドキュメント

動作環境

Python 3.x

Google API (YouTube Data API)

その他必要なライブラリは requirements.txt に記載

インストール方法

リポジトリをクローン
```
git clone https://github.com/your-repo.git
cd your-repo
```

必要なライブラリをインストール
```
pip install -r requirements.txt
```
config/ にAPIキーや設定を記入

使い方

video/ にアップロードしたい動画を配置

music/ にBGMを配置（オプション）

スクリプトを実行
```
python script/upload.py
```
ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。

