#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube自動アップロードスクリプト
============================

このスクリプトは生成した桜の動画をYouTubeに自動的にアップロードします。
YouTube Data APIを使用して、動画のアップロード、タイトル設定、説明文設定、
タグ設定などの機能を実装しています。

使用方法:
    python youtube_uploader.py --video sakura_video.mp4 --title "日本の桜特集2025" --description "description.txt"

オプション:
    --video: アップロードする動画ファイル（必須）
    --title: 動画のタイトル（デフォルト: ファイル名）
    --description: 説明文ファイルのパス（デフォルト: 自動生成）
    --tags: カンマ区切りのタグリスト（デフォルト: 自動生成）
    --category: 動画カテゴリID（デフォルト: 22=People & Blogs）
    --privacy: プライバシー設定（public, unlisted, private）（デフォルト: private）
"""

import os
import sys
import argparse
import http.client
import httplib2
import random
import time
from datetime import datetime
from typing import List, Dict, Optional, Any

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# プロジェクトのルートディレクトリ
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 認証情報ディレクトリ
CREDENTIALS_DIR = os.path.join(PROJECT_ROOT, "credentials")
CLIENT_SECRETS_FILE = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.json")

# 必要なスコープ
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# デフォルト設定
DEFAULT_CATEGORY = "22"  # People & Blogs
DEFAULT_PRIVACY = "private"  # private, public, unlisted

# 桜関連のデフォルトタグ
DEFAULT_TAGS = [
    "桜", "さくら", "サクラ", "cherry blossom", "japan", "日本", "春", "spring",
    "花見", "hanami", "自然", "nature", "風景", "landscape", "4K", "絶景", "beautiful"
]

class YouTubeUploader:
    """YouTubeに動画をアップロードするクラス"""
    
    def __init__(
        self,
        video_file: str,
        title: Optional[str] = None,
        description_file: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: str = DEFAULT_CATEGORY,
        privacy: str = DEFAULT_PRIVACY
    ):
        """
        初期化メソッド
        
        Args:
            video_file: アップロードする動画ファイル
            title: 動画のタイトル（Noneの場合はファイル名）
            description_file: 説明文ファイルのパス（Noneの場合は自動生成）
            tags: タグリスト（Noneの場合は自動生成）
            category: 動画カテゴリID
            privacy: プライバシー設定（public, unlisted, private）
        """
        self.video_file = video_file
        self.title = title or os.path.splitext(os.path.basename(video_file))[0]
        self.description_file = description_file
        self.tags = tags or DEFAULT_TAGS
        self.category = category
        self.privacy = privacy
        
        # 認証情報ディレクトリが存在しない場合は作成
        os.makedirs(CREDENTIALS_DIR, exist_ok=True)
        
        # YouTube APIクライアント
        self.youtube = self._get_authenticated_service()
    
    def _get_authenticated_service(self):
        """認証済みのYouTube APIサービスを取得"""
        credentials = None
        
        # トークンファイルが存在する場合は読み込み
        if os.path.exists(TOKEN_FILE):
            credentials = Credentials.from_authorized_user_info(
                info=eval(open(TOKEN_FILE).read()),
                scopes=SCOPES
            )
        
        # 認証情報が存在しないか、無効な場合は新たに取得
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRETS_FILE):
                    print(f"エラー: クライアントシークレットファイルが見つかりません: {CLIENT_SECRETS_FILE}")
                    print("Google Cloud Consoleで認証情報を作成し、以下のパスに保存してください:")
                    print(CLIENT_SECRETS_FILE)
                    sys.exit(1)
                
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                credentials = flow.run_local_server(port=0)
            
            # トークンを保存
            with open(TOKEN_FILE, "w") as token:
                token.write(str(credentials.to_json()))
        
        return build("youtube", "v3", credentials=credentials)
    
    def _get_description(self) -> str:
        """動画の説明文を取得"""
        if self.description_file and os.path.exists(self.description_file):
            with open(self.description_file, "r", encoding="utf-8") as f:
                return f.read()
        
        # デフォルトの説明文を生成
        current_year = datetime.now().year
        description = f"""日本の美しい桜の風景 {current_year}

この動画では日本各地の美しい桜の風景をお届けします。
春の訪れを告げる桜は、日本文化において特別な存在です。

#桜 #日本 #春 #cherryblossom #japan #spring #花見

撮影地:
- 日本各地の桜の名所

音楽:
- フリー素材を使用

※この動画は自動生成されています。
"""
        return description
    
    def upload_video(self) -> Dict[str, Any]:
        """動画をアップロード"""
        if not os.path.exists(self.video_file):
            raise FileNotFoundError(f"動画ファイルが見つかりません: {self.video_file}")
        
        # 動画のメタデータを設定
        body = {
            "snippet": {
                "title": self.title,
                "description": self._get_description(),
                "tags": self.tags,
                "categoryId": self.category
            },
            "status": {
                "privacyStatus": self.privacy,
                "selfDeclaredMadeForKids": False
            }
        }
        
        # アップロード用のメディアファイルを準備
        media = MediaFileUpload(
            self.video_file,
            mimetype="video/*",
            resumable=True
        )
        
        try:
            print(f"動画のアップロードを開始します: {self.title}")
            
            # アップロードリクエストを作成
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            # アップロードを実行（プログレスコールバック付き）
            response = self._resumable_upload(request)
            
            print(f"動画のアップロードが完了しました: {response['id']}")
            print(f"タイトル: {response['snippet']['title']}")
            print(f"URL: https://www.youtube.com/watch?v={response['id']}")
            
            return response
            
        except HttpError as e:
            print(f"エラー: アップロード中にHTTPエラーが発生しました: {e.resp.status} {e.content}")
            raise
        except Exception as e:
            print(f"エラー: アップロード中に問題が発生しました: {str(e)}")
            raise
    
    def _resumable_upload(self, request):
        """再開可能なアップロードを実行"""
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                print(".", end="", flush=True)
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"\rアップロード進捗: {progress}%", end="", flush=True)
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    if retry > 10:
                        raise
                    retry += 1
                    time.sleep(random.randint(1, 5))
                else:
                    raise
        
        print()  # 改行
        return response

def parse_arguments():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description="YouTube自動アップロードスクリプト")
    
    parser.add_argument(
        "--video", "-v",
        required=True,
        help="アップロードする動画ファイル（必須）"
    )
    
    parser.add_argument(
        "--title", "-t",
        help="動画のタイトル（デフォルト: ファイル名）"
    )
    
    parser.add_argument(
        "--description", "-d",
        help="説明文ファイルのパス（デフォルト: 自動生成）"
    )
    
    parser.add_argument(
        "--tags",
        help="カンマ区切りのタグリスト（デフォルト: 自動生成）"
    )
    
    parser.add_argument(
        "--category", "-c",
        default=DEFAULT_CATEGORY,
        help=f"動画カテゴリID（デフォルト: {DEFAULT_CATEGORY}=People & Blogs）"
    )
    
    parser.add_argument(
        "--privacy", "-p",
        choices=["public", "unlisted", "private"],
        default=DEFAULT_PRIVACY,
        help=f"プライバシー設定（デフォルト: {DEFAULT_PRIVACY}）"
    )
    
    return parser.parse_args()

def main():
    """メイン関数"""
    args = parse_arguments()
    
    # タグをリストに変換
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]
    
    # アップローダーを初期化
    uploader = YouTubeUploader(
        video_file=args.video,
        title=args.title,
        description_file=args.description,
        tags=tags,
        category=args.category,
        privacy=args.privacy
    )
    
    # 動画をアップロード
    response = uploader.upload_video()
    
    print(f"アップロードされた動画ID: {response['id']}")
    print(f"視聴URL: https://www.youtube.com/watch?v={response['id']}")
    print("完了しました。")

if __name__ == "__main__":
    main()
