# 桜を題材にしたYouTube動画自動生成システム - 使用マニュアル

## 1. はじめに

このシステムは、桜の映像素材を使用して自動的に高品質な動画を生成し、YouTubeにアップロードするためのツールです。4K解像度の映像編集、テキストオーバーレイ、BGM挿入などの機能を備え、様々なスタイルの桜動画を簡単に作成できます。

### 1.1 主な機能

- 桜の映像素材から自動的に動画を生成
- 複数の動画スタイル（ランキング形式、地域特化型、テーマ型、季節進行型）
- 4K解像度での高品質出力
- テキストオーバーレイとアニメーション効果
- BGMと効果音の自動挿入
- YouTube Data APIを使用した動画アップロード

### 1.2 システム要件

- Python 3.8以上
- 必要なライブラリ: moviepy, opencv-python, pillow, pydub
- YouTube Data API用のAPIキー（アップロード機能を使用する場合）
- 十分なディスク容量（4K動画の処理には大量のストレージが必要）

## 2. インストール方法

### 2.1 Pythonのインストール

システムにPython 3.8以上がインストールされていることを確認してください。インストールされていない場合は、[Python公式サイト](https://www.python.org/downloads/)からダウンロードしてインストールしてください。

### 2.2 必要なライブラリのインストール

以下のコマンドを実行して、必要なライブラリをインストールします。

```bash
pip install moviepy opencv-python pillow pydub google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2.3 プロジェクトのセットアップ

1. プロジェクトディレクトリを作成します。

```bash
mkdir -p sakura_youtube_project/resources/{videos,music,sfx}
mkdir -p sakura_youtube_project/output
mkdir -p sakura_youtube_project/credentials
```

2. ソースコードファイルを `sakura_youtube_project/src` ディレクトリに配置します。

3. 桜の映像素材を `sakura_youtube_project/resources/videos` ディレクトリに配置します。

4. BGM素材を `sakura_youtube_project/resources/music` ディレクトリに配置します。

5. 効果音素材を `sakura_youtube_project/resources/sfx` ディレクトリに配置します。

## 3. 動画生成機能の使用方法

### 3.1 基本的な使用方法

以下のコマンドを実行して、基本的な桜動画を生成します。

```bash
python src/sakura_video_generator.py --output output/my_sakura_video.mp4
```

これにより、デフォルト設定（ランキング形式、3分間）の桜動画が生成されます。

### 3.2 動画スタイルの指定

以下のコマンドで、動画のスタイルを指定できます。

```bash
# ランキング形式（デフォルト）
python src/sakura_video_generator.py --style ranking

# 地域特化型
python src/sakura_video_generator.py --style regional

# テーマ型
python src/sakura_video_generator.py --style theme

# 季節進行型
python src/sakura_video_generator.py --style seasonal
```

### 3.3 動画の長さの指定

以下のコマンドで、動画の長さ（秒）を指定できます。

```bash
# 2分間の動画を生成
python src/sakura_video_generator.py --length 120
```

### 3.4 タイトルの指定

以下のコマンドで、動画のタイトルを指定できます。

```bash
python src/sakura_video_generator.py --title "日本の美しい桜特集2025"
```

### 3.5 BGMの指定

以下のコマンドで、使用するBGMファイルを指定できます。

```bash
python src/sakura_video_generator.py --bgm resources/music/sakura_theme.mp3
```

### 3.6 すべてのオプションを組み合わせた例

```bash
python src/sakura_video_generator.py \
  --output output/sakura_ranking_2025.mp4 \
  --style ranking \
  --length 180 \
  --title "2025年 日本の桜名所ベスト10" \
  --bgm resources/music/sakura_theme.mp3
```

## 4. YouTube自動アップロード機能の使用方法

### 4.1 YouTube Data APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセスし、新しいプロジェクトを作成します。

2. YouTube Data API v3を有効にします。

3. OAuth 2.0クライアントIDを作成し、認証情報をダウンロードします。

4. ダウンロードしたJSONファイルを `sakura_youtube_project/credentials/client_secret.json` として保存します。

### 4.2 基本的な使用方法

以下のコマンドを実行して、動画をYouTubeにアップロードします。

```bash
python src/youtube_uploader.py --video output/my_sakura_video.mp4
```

初回実行時は、ブラウザが開いてGoogleアカウントへのアクセス許可を求められます。許可すると、認証情報が `sakura_youtube_project/credentials/token.json` に保存され、以降の実行では自動的に使用されます。

### 4.3 タイトルと説明文の指定

以下のコマンドで、アップロードする動画のタイトルと説明文を指定できます。

```bash
# タイトルを指定
python src/youtube_uploader.py --video output/my_sakura_video.mp4 --title "日本の桜特集2025"

# 説明文ファイルを指定
python src/youtube_uploader.py --video output/my_sakura_video.mp4 --description description.txt
```

説明文ファイルは、UTF-8エンコードのテキストファイルで、動画の説明文を記述します。

### 4.4 タグとカテゴリの指定

以下のコマンドで、アップロードする動画のタグとカテゴリを指定できます。

```bash
# タグを指定
python src/youtube_uploader.py --video output/my_sakura_video.mp4 --tags "桜,日本,春,cherryblossom,japan"

# カテゴリを指定
python src/youtube_uploader.py --video output/my_sakura_video.mp4 --category 22
```

カテゴリIDは以下の通りです：
- 1: Film & Animation
- 2: Autos & Vehicles
- 10: Music
- 15: Pets & Animals
- 17: Sports
- 18: Short Movies
- 19: Travel & Events
- 20: Gaming
- 21: Videoblogging
- 22: People & Blogs
- 23: Comedy
- 24: Entertainment
- 25: News & Politics
- 26: Howto & Style
- 27: Education
- 28: Science & Technology
- 29: Nonprofits & Activism

### 4.5 プライバシー設定

以下のコマンドで、アップロードする動画のプライバシー設定を指定できます。

```bash
# 公開（誰でも視聴可能）
python src/youtube_uploader.py --video output/my_sakura_video.mp4 --privacy public

# 限定公開（URLを知っている人のみ視聴可能）
python src/youtube_uploader.py --video output/my_sakura_video.mp4 --privacy unlisted

# 非公開（自分のみ視聴可能）
python src/youtube_uploader.py --video output/my_sakura_video.mp4 --privacy private
```

### 4.6 すべてのオプションを組み合わせた例

```bash
python src/youtube_uploader.py \
  --video output/sakura_ranking_2025.mp4 \
  --title "2025年 日本の桜名所ベスト10" \
  --description descriptions/sakura_ranking.txt \
  --tags "桜,日本,春,ランキング,名所,cherryblossom,japan,spring" \
  --category 19 \
  --privacy public
```

## 5. テスト機能の使用方法

### 5.1 動画生成機能のテスト

以下のコマンドを実行して、動画生成機能をテストします。

```bash
python src/test_sakura_video.py --test-type generation
```

### 5.2 アップロード機能のテスト

以下のコマンドを実行して、アップロード機能をテストします。

```bash
python src/test_sakura_video.py --test-type upload --video-file output/test_video.mp4
```

### 5.3 すべての機能をテスト

以下のコマンドを実行して、動画生成からアップロードまでの一連の流れをテストします。

```bash
python src/test_sakura_video.py --test-type all
```

## 6. トラブルシューティング

### 6.1 動画生成に関する問題

#### 素材が見つからない場合

エラーメッセージ: `警告: 動画ファイルが見つかりません`

解決策:
1. `resources/videos` ディレクトリに桜の映像素材が配置されているか確認してください。
2. 素材ファイルの形式が対応しているか確認してください（mp4, mov, avi, mkvなど）。

#### メモリ不足エラー

エラーメッセージ: `MemoryError` または `RuntimeError: Error allocating memory`

解決策:
1. 動画の解像度を下げてみてください（`DEFAULT_RESOLUTION`の値を変更）。
2. 動画の長さを短くしてみてください（`--length`オプションで指定）。
3. より多くのRAMを搭載したマシンで実行してみてください。

### 6.2 YouTube APIに関する問題

#### 認証エラー

エラーメッセージ: `クライアントシークレットファイルが見つかりません`

解決策:
1. Google Cloud Consoleで認証情報を作成し、`credentials/client_secret.json`として保存してください。

#### アップロードクォータの超過

エラーメッセージ: `quotaExceeded`

解決策:
1. YouTube Data APIの1日のクォータ制限を超えている可能性があります。24時間待ってから再試行してください。
2. Google Cloud Consoleでクォータの増加をリクエストすることも可能です。

## 7. 拡張と改良のアイデア

### 7.1 機能拡張

- 音声ナレーションの追加（テキスト読み上げAPIを使用）
- AIによる映像の自動分類と選択
- 視聴者の反応に基づく動的コンテンツ調整
- 自動字幕生成

### 7.2 パフォーマンス最適化

- GPUアクセラレーションの活用
- 並列処理による処理速度の向上
- 中間ファイルの圧縮による容量削減

### 7.3 ユーザーインターフェース

- GUIの追加
- ウェブインターフェースの開発
- スケジュール機能の実装

## 8. 参考資料

- [MoviePyドキュメント](https://zulko.github.io/moviepy/)
- [OpenCVドキュメント](https://docs.opencv.org/)
- [YouTube Data API ドキュメント](https://developers.google.com/youtube/v3/docs)
- [Google API クライアントライブラリ](https://developers.google.com/api-client-library/python)

## 9. ライセンスと免責事項

このシステムは、個人的な使用や教育目的での使用を想定しています。商用利用する場合は、使用する素材のライセンスを必ず確認してください。

また、YouTubeの利用規約に違反するコンテンツのアップロードには使用しないでください。アップロードされたコンテンツに関する責任は、すべてユーザーが負うものとします。

---

© 2025 桜動画自動生成プロジェクト
