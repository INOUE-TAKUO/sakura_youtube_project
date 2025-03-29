import os
import requests
import time
import random
from bgmer_scraper import BGMerScraper

class SakuraSoundDownloader:
    """
    桜関連の音源をダウンロードするクラス
    """
    def __init__(self, download_dir="sakura_sounds_downloads"):
        """
        初期化
        
        Args:
            download_dir (str): ダウンロード先ディレクトリ
        """
        self.download_dir = download_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # ダウンロードディレクトリの作成
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download_music(self, music_info, prefer_long=True):
        """
        音源をダウンロードする
        
        Args:
            music_info (dict): 音源情報
            prefer_long (bool): LONG版を優先するかどうか
            
        Returns:
            str: ダウンロードしたファイルのパス、失敗した場合はNone
        """
        if not music_info.get('download_links'):
            print(f"'{music_info['title']}' にダウンロードリンクがありません。")
            return None
        
        # ダウンロードするリンクを選択
        download_link = None
        if prefer_long and 'long' in music_info['download_links']:
            download_link = music_info['download_links']['long']
        elif 'short' in music_info['download_links']:
            download_link = music_info['download_links']['short']
        elif 'default' in music_info['download_links']:
            download_link = music_info['download_links']['default']
        else:
            # 最初のリンクを使用
            download_link = next(iter(music_info['download_links'].values()))
        
        if not download_link:
            print(f"'{music_info['title']}' の有効なダウンロードリンクが見つかりませんでした。")
            return None
        
        # ファイル名を生成
        filename = self._sanitize_filename(music_info['title'])
        if prefer_long and 'long' in music_info['download_links']:
            filename += "_long"
        elif 'short' in music_info['download_links']:
            filename += "_short"
        
        # 拡張子を確認
        if download_link.lower().endswith('.mp3'):
            filename += ".mp3"
        elif download_link.lower().endswith('.wav'):
            filename += ".wav"
        elif download_link.lower().endswith('.ogg'):
            filename += ".ogg"
        else:
            filename += ".mp3"  # デフォルトはMP3と仮定
        
        file_path = os.path.join(self.download_dir, filename)
        
        # ダウンロード
        try:
            print(f"'{music_info['title']}' をダウンロード中...")
            response = self.session.get(download_link, stream=True)
            response.raise_for_status()
            
            # ファイルに保存
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"'{music_info['title']}' のダウンロードが完了しました: {file_path}")
            
            # サーバー負荷軽減のための待機
            time.sleep(random.uniform(1, 3))
            
            return file_path
            
        except Exception as e:
            print(f"'{music_info['title']}' のダウンロード中にエラーが発生しました: {e}")
            # 部分的にダウンロードされたファイルを削除
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    def download_all_music(self, music_list, prefer_long=True):
        """
        複数の音源をダウンロードする
        
        Args:
            music_list (list): 音源情報のリスト
            prefer_long (bool): LONG版を優先するかどうか
            
        Returns:
            list: ダウンロードしたファイルのパスのリスト
        """
        downloaded_files = []
        
        for i, music in enumerate(music_list):
            print(f"\n[{i+1}/{len(music_list)}] '{music['title']}' をダウンロードしています...")
            file_path = self.download_music(music, prefer_long)
            
            if file_path:
                downloaded_files.append(file_path)
        
        return downloaded_files
    
    def _sanitize_filename(self, filename):
        """
        ファイル名に使用できない文字を置換する
        
        Args:
            filename (str): 元のファイル名
            
        Returns:
            str: 安全なファイル名
        """
        # ファイル名に使用できない文字を置換
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 長すぎるファイル名を切り詰める
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename

# 使用例
if __name__ == "__main__":
    # スクレイパーを初期化
    scraper = BGMerScraper()
    
    # 桜関連の音源を検索
    print("桜関連の音源を検索中...")
    music_list = scraper.search_sakura_music()
    
    if not music_list:
        print("桜関連の音源が見つかりませんでした。")
        exit()
    
    print(f"\n合計 {len(music_list)} 件の桜関連音源が見つかりました。\n")
    
    # 各音源の詳細情報を取得
    for i, music in enumerate(music_list):
        print(f"[{i+1}/{len(music_list)}] {music['title']} の詳細を取得中...")
        music_list[i] = scraper.get_music_details(music)
    
    # ダウンローダーを初期化
    downloader = SakuraSoundDownloader()
    
    # 全ての音源をダウンロード
    downloaded_files = downloader.download_all_music(music_list)
    
    print(f"\n合計 {len(downloaded_files)} 件の音源をダウンロードしました。")
    for file_path in downloaded_files:
        print(f"- {file_path}")
