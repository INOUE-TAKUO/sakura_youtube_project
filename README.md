#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
桜の動画スクレイピングとダウンロードツール - 使用方法ガイド

このドキュメントでは、sakura_video_downloader.pyの使用方法と機能について説明します。
このツールは、YouTubeなどの動画サイトから桜に関する動画を検索し、
自動的にダウンロードするためのものです。
"""

# 基本的な使用方法

## インストール方法

このツールを使用するには、以下の依存関係が必要です：

1. Python 3.6以上
2. yt-dlp
3. ffmpeg

以下のコマンドでインストールできます：

```bash
# yt-dlpのインストール
pip install yt-dlp

# ffmpegのインストール（Ubuntu/Debian）
sudo apt-get install ffmpeg

# ffmpegのインストール（macOS - Homebrewを使用）
brew install ffmpeg

# ffmpegのインストール（Windows）
# https://ffmpeg.org/download.html からダウンロードしてパスを通してください
```

## 基本的な使い方

```bash
# 基本的な検索とダウンロード
python sakura_video_downloader.py --query "桜 タイムラプス" --number 5

# 高解像度（1080p）でダウンロード
python sakura_video_downloader.py --query "桜 4K" --resolution 1080

# 特定のプレイリストからダウンロード
python sakura_video_downloader.py --playlist "https://www.youtube.com/playlist?list=PLaGbbRbRmQIbAekzGTCrtVCDirtmKM7ru"

# 出力ディレクトリを指定
python sakura_video_downloader.py --query "京都 桜" --output "/path/to/output/directory"

# 字幕付きでダウンロード
python sakura_video_downloader.py --query "桜 名所" --subtitles
```

引数なしで実行すると、プリセットの選択肢が表示されます：

```bash
python sakura_video_downloader.py
```

## コマンドラインオプション

| オプション | 短縮形 | 説明 | デフォルト値 |
|------------|--------|------|-------------|
| --query | -q | 検索クエリ | なし |
| --playlist | -p | プレイリストURL | なし |
| --output | -o | 出力ディレクトリ | カレントディレクトリ/downloads/sakura_[日時] |
| --number | -n | ダウンロードする最大動画数 | 10 |
| --format | -f | 動画フォーマット | mp4 |
| --resolution | -r | 動画解像度 | 720 |
| --language | -l | 言語設定 | ja |
| --subtitles | -s | 字幕をダウンロードする | False |
| --site | なし | 検索サイト（youtube, nicovideo, vimeo） | youtube |

# 機能詳細

## 検索機能

このツールは、指定されたキーワードを使用して動画を検索します。検索は以下のサイトで行えます：

- YouTube（デフォルト）
- ニコニコ動画
- Vimeo

検索結果は指定された最大数（デフォルトは10）までダウンロードされます。

## プレイリスト機能

特定のプレイリストURLを指定すると、そのプレイリスト内の動画をダウンロードします。
これは、キュレーションされた桜の動画コレクションを一括でダウンロードするのに便利です。

## メタデータ

ダウンロードした各動画について、以下のメタデータがJSONファイルとして保存されます：

- タイトル
- アップロード日
- 再生時間
- 視聴回数
- 高評価数
- アップローダー情報

## サムネイル

各動画のサムネイル画像も自動的にダウンロードされます。

# 使用例

## 例1: 桜のタイムラプス動画を検索してダウンロード

```bash
python sakura_video_downloader.py --query "桜 タイムラプス" --number 5
```

この例では、「桜 タイムラプス」というキーワードで検索し、最大5つの動画をダウンロードします。

## 例2: 高画質の桜の動画をダウンロード

```bash
python sakura_video_downloader.py --query "桜 4K" --resolution 1080 --format mp4
```

この例では、「桜 4K」というキーワードで検索し、1080p解像度でmp4形式の動画をダウンロードします。

## 例3: 特定の桜のプレイリストをダウンロード

```bash
python sakura_video_downloader.py --playlist "https://www.youtube.com/playlist?list=PLaGbbRbRmQIbAekzGTCrtVCDirtmKM7ru" --number 20
```

この例では、指定されたプレイリストから最大20の動画をダウンロードします。

# 注意事項

1. **著作権に関する注意**: ダウンロードした動画は個人的な使用にとどめ、再配布や商用利用は行わないでください。

2. **帯域幅の使用**: 大量の動画をダウンロードする場合は、ネットワーク帯域幅に注意してください。

3. **ディスク容量**: 高解像度の動画は大きなディスク容量を必要とします。十分な空き容量があることを確認してください。

4. **サイトの利用規約**: 各動画サイトの利用規約を遵守してください。

# トラブルシューティング

## 一般的な問題

1. **動画がダウンロードできない**:
   - インターネット接続を確認してください
   - 検索クエリを変更してみてください
   - サイトの仕様変更により、yt-dlpの更新が必要かもしれません

2. **ffmpegエラー**:
   - ffmpegが正しくインストールされているか確認してください
   - パスが通っているか確認してください

3. **解像度が指定通りでない**:
   - 指定した解像度が利用できない場合、利用可能な最も近い解像度が選択されます

## 更新方法

yt-dlpを最新バージョンに更新するには：

```bash
pip install -U yt-dlp
```

# 開発情報

このツールは以下のライブラリを使用しています：

- yt-dlp: 動画のダウンロードと検索
- argparse: コマンドライン引数の解析
- json: メタデータの処理
- datetime: タイムスタンプの生成
- os: ファイルシステム操作

# ライセンス

このツールは個人的な使用を目的として作成されました。
商用利用や再配布については、各動画サイトの利用規約を遵守してください。
