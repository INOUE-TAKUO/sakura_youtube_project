#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
桜の動画スクレイピングとダウンロードツール

このスクリプトは、YouTubeなどの動画サイトから桜に関する動画を検索し、
自動的にダウンロードするためのツールです。yt-dlpライブラリを使用しています。
"""

import os
import sys
import argparse
import json
from datetime import datetime
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

class SakuraVideoDownloader:
    """桜の動画をダウンロードするためのクラス"""
    
    def __init__(self, output_dir=None, max_downloads=10, video_format='mp4', 
                 resolution='720', language='ja', subtitles=False):
        """
        初期化メソッド
        
        Args:
            output_dir (str): ダウンロード先ディレクトリ
            max_downloads (int): ダウンロードする最大動画数
            video_format (str): ダウンロードする動画フォーマット
            resolution (str): 動画の解像度
            language (str): 検索言語設定
            subtitles (bool): 字幕をダウンロードするかどうか
        """
        # 出力ディレクトリの設定
        if output_dir is None:
            self.output_dir = os.path.join(os.getcwd(), 'downloads', 
                                          f'sakura_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        else:
            self.output_dir = output_dir
            
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # メタデータ保存用ディレクトリ
        self.metadata_dir = os.path.join(self.output_dir, 'metadata')
        if not os.path.exists(self.metadata_dir):
            os.makedirs(self.metadata_dir)
            
        # 設定パラメータ
        self.max_downloads = max_downloads
        self.video_format = video_format
        self.resolution = resolution
        self.language = language
        self.subtitles = subtitles
        
        # ダウンロード済み動画のリスト
        self.downloaded_videos = []
        
        # yt-dlpのオプション設定
        self.ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'writeinfojson': True,
            'writethumbnail': True,
            'writesubtitles': subtitles,
            'writeautomaticsub': subtitles,
            'subtitleslangs': [language] if subtitles else None,
            'ignoreerrors': True,
            'nooverwrites': True,
            'quiet': False,
            'verbose': False,
            'max_downloads': max_downloads,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': video_format,
            }],
        }
        
    def search_and_download(self, query, site='youtube'):
        """
        指定したクエリで動画を検索してダウンロードする
        
        Args:
            query (str): 検索クエリ
            site (str): 検索サイト (youtube, nicovideo, vimeo)
            
        Returns:
            list: ダウンロードした動画のリスト
        """
        print(f"「{query}」の検索を開始します...")
        
        # サイト別の検索URL形式
        search_url = {
            'youtube': f'ytsearch{self.max_downloads}:{query}',
            'nicovideo': f'nicosearch{self.max_downloads}:{query}',
            'vimeo': f'vimsearch{self.max_downloads}:{query}'
        }
        
        if site not in search_url:
            print(f"エラー: サポートされていないサイト '{site}'")
            return []
        
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(search_url[site], download=True)
                
                if info and 'entries' in info:
                    # 検索結果の処理
                    for entry in info['entries']:
                        if entry:
                            video_info = {
                                'id': entry.get('id', 'unknown'),
                                'title': entry.get('title', 'unknown'),
                                'url': entry.get('webpage_url', 'unknown'),
                                'upload_date': entry.get('upload_date', 'unknown'),
                                'duration': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                                'like_count': entry.get('like_count', 0),
                                'uploader': entry.get('uploader', 'unknown')
                            }
                            self.downloaded_videos.append(video_info)
                            
                    # メタデータをJSONファイルに保存
                    metadata_file = os.path.join(self.metadata_dir, f'search_results_{site}_{query.replace(" ", "_")}.json')
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(self.downloaded_videos, f, ensure_ascii=False, indent=4)
                        
                    print(f"{len(self.downloaded_videos)}件の動画をダウンロードしました。")
                    return self.downloaded_videos
                else:
                    print("検索結果が見つかりませんでした。")
                    return []
                    
        except DownloadError as e:
            print(f"ダウンロードエラー: {e}")
            return []
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return []
            
    def download_playlist(self, playlist_url):
        """
        プレイリストURLから動画をダウンロードする
        
        Args:
            playlist_url (str): プレイリストのURL
            
        Returns:
            list: ダウンロードした動画のリスト
        """
        print(f"プレイリスト '{playlist_url}' のダウンロードを開始します...")
        
        # プレイリスト用にオプションを調整
        playlist_opts = self.ydl_opts.copy()
        playlist_opts['playlistend'] = self.max_downloads
        
        try:
            with YoutubeDL(playlist_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=True)
                
                if info and 'entries' in info:
                    # プレイリスト結果の処理
                    playlist_videos = []
                    for entry in info['entries']:
                        if entry:
                            video_info = {
                                'id': entry.get('id', 'unknown'),
                                'title': entry.get('title', 'unknown'),
                                'url': entry.get('webpage_url', 'unknown'),
                                'upload_date': entry.get('upload_date', 'unknown'),
                                'duration': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                                'like_count': entry.get('like_count', 0),
                                'uploader': entry.get('uploader', 'unknown')
                            }
                            playlist_videos.append(video_info)
                            
                    # メタデータをJSONファイルに保存
                    playlist_id = info.get('id', 'unknown_playlist')
                    metadata_file = os.path.join(self.metadata_dir, f'playlist_{playlist_id}.json')
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(playlist_videos, f, ensure_ascii=False, indent=4)
                        
                    print(f"プレイリストから{len(playlist_videos)}件の動画をダウンロードしました。")
                    self.downloaded_videos.extend(playlist_videos)
                    return playlist_videos
                else:
                    print("プレイリストが見つかりませんでした。")
                    return []
                    
        except DownloadError as e:
            print(f"ダウンロードエラー: {e}")
            return []
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return []
            
    def get_download_summary(self):
        """
        ダウンロードの概要を取得する
        
        Returns:
            dict: ダウンロードの概要情報
        """
        # ダウンロードディレクトリ内のmp4ファイルを数える
        mp4_files = [f for f in os.listdir(self.output_dir) if f.endswith('.mp4')]
        total_videos = len(mp4_files)
        
        # メタデータからの情報取得を試みる
        total_duration = 0
        for video in self.downloaded_videos:
            total_duration += video.get('duration', 0)
        
        # メタデータが不完全な場合は、ディレクトリ内のjsonファイルから情報を取得
        if total_duration == 0 or len(self.downloaded_videos) == 0:
            json_files = [f for f in os.listdir(self.output_dir) if f.endswith('.info.json')]
            for json_file in json_files:
                try:
                    with open(os.path.join(self.output_dir, json_file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_duration += data.get('duration', 0)
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
        
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'total_videos': total_videos,
            'total_duration': f"{int(hours)}時間{int(minutes)}分{int(seconds)}秒",
            'output_directory': self.output_dir,
            'download_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='桜の動画をダウンロードするツール')
    
    # 基本オプション
    parser.add_argument('-q', '--query', type=str, help='検索クエリ')
    parser.add_argument('-p', '--playlist', type=str, help='プレイリストURL')
    parser.add_argument('-o', '--output', type=str, help='出力ディレクトリ')
    parser.add_argument('-n', '--number', type=int, default=10, help='ダウンロードする最大動画数')
    parser.add_argument('-f', '--format', type=str, default='mp4', help='動画フォーマット')
    parser.add_argument('-r', '--resolution', type=str, default='720', help='動画解像度')
    parser.add_argument('-l', '--language', type=str, default='ja', help='言語設定')
    parser.add_argument('-s', '--subtitles', action='store_true', help='字幕をダウンロードする')
    parser.add_argument('--site', type=str, default='youtube', 
                        choices=['youtube', 'nicovideo', 'vimeo'], 
                        help='検索サイト')
    
    # 桜関連の検索クエリプリセット
    sakura_queries = [
        "日本 桜",
        "cherry blossom japan",
        "sakura japan",
        "桜 名所",
        "桜 4K",
        "桜 タイムラプス",
        "京都 桜",
        "東京 桜"
    ]
    
    # 桜関連のプレイリストプリセット
    sakura_playlists = [
        "https://www.youtube.com/playlist?list=PLaGbbRbRmQIbAekzGTCrtVCDirtmKM7ru",  # 日本の桜の絶景
        "https://www.youtube.com/playlist?list=PLVc8Zw3MujdHOLWWJ9bkkmn-bX78Oo996",  # 日本全国「桜・お花見」三昧！
        "https://www.youtube.com/playlist?list=PLVc8Zw3MujdE_obvo2PbIzYEdCvTzlasR"   # 日本全国「桜・お花見」三昧！HD長編シリーズ
    ]
    
    args = parser.parse_args()
    
    # ダウンローダーの初期化
    downloader = SakuraVideoDownloader(
        output_dir=args.output,
        max_downloads=args.number,
        video_format=args.format,
        resolution=args.resolution,
        language=args.language,
        subtitles=args.subtitles
    )
    
    # 引数がない場合はヘルプを表示
    if len(sys.argv) == 1:
        print("引数が指定されていません。以下のプリセットから選択するか、--helpでヘルプを表示してください。")
        print("\n桜関連の検索クエリプリセット:")
        for i, query in enumerate(sakura_queries, 1):
            print(f"{i}. {query}")
            
        print("\n桜関連のプレイリストプリセット:")
        for i, playlist in enumerate(sakura_playlists, 1):
            print(f"{i}. {playlist}")
            
        choice = input("\n選択してください（例: q1でクエリ1、p2でプレイリスト2）: ")
        
        if choice.startswith('q'):
            try:
                index = int(choice[1:]) - 1
                if 0 <= index < len(sakura_queries):
                    args.query = sakura_queries[index]
                    args.playlist = None
                else:
                    print("無効な選択です。")
                    return
            except ValueError:
                print("無効な選択です。")
                return
        elif choice.startswith('p'):
            try:
                index = int(choice[1:]) - 1
                if 0 <= index < len(sakura_playlists):
                    args.playlist = sakura_playlists[index]
                    args.query = None
                else:
                    print("無効な選択です。")
                    return
            except ValueError:
                print("無効な選択です。")
                return
        else:
            print("無効な選択です。")
            return
    
    # 検索クエリが指定されている場合
    if args.query:
        downloader.search_and_download(args.query, args.site)
    
    # プレイリストが指定されている場合
    if args.playlist:
        downloader.download_playlist(args.playlist)
    
    # ダウンロード概要の表示
    summary = downloader.get_download_summary()
    print("\n===== ダウンロード概要 =====")
    print(f"ダウンロードした動画数: {summary['total_videos']}")
    print(f"合計時間: {summary['total_duration']}")
    print(f"出力ディレクトリ: {summary['output_directory']}")
    print(f"ダウンロード完了時刻: {summary['download_time']}")
    print("===========================")

if __name__ == "__main__":
    main()
