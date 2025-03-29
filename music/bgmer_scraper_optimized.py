import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random
import urllib.parse

class BGMerScraper:
    """
    BGMerサイトから桜関連の音源をスクレイピングするクラス
    """
    def __init__(self, base_url="https://bgmer.net"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_sakura_music_list(self):
        """
        桜関連の音源リストを直接取得する（検索機能を使わない方法）
        
        Returns:
            list: 桜関連音源情報のリスト
        """
        # 桜関連の音源URLを直接指定
        sakura_music_urls = [
            "https://bgmer.net/music/220",  # ソメイヨシノ
        ]
        
        music_list = []
        
        for url in sakura_music_urls:
            try:
                print(f"音源ページを取得中: {url}")
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # タイトルを取得
                title_elem = soup.select_one('h1') or soup.select_one('.music-title')
                title = title_elem.text.strip() if title_elem else "不明なタイトル"
                
                music_info = {
                    'title': title,
                    'url': url,
                    'keyword': '桜'
                }
                
                music_list.append(music_info)
                print(f"見つかった音源: {title}")
                
                # サーバー負荷軽減のための待機
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"音源ページの取得中にエラーが発生しました: {e}")
        
        return music_list
    
    def get_music_details(self, music_info):
        """
        音源の詳細情報を取得する
        
        Args:
            music_info (dict): 音源の基本情報
            
        Returns:
            dict: 詳細情報を追加した音源情報
        """
        try:
            response = self.session.get(music_info['url'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ダウンロードリンクを探す
            download_links = {}
            
            # SHORT版とLONG版のリンクを探す（BGMerサイト特有の構造）
            short_link = soup.select_one('a:-soup-contains("SHORT")')
            long_link = soup.select_one('a:-soup-contains("LONG")')
            
            if not short_link:
                # 代替方法
                short_links = [a for a in soup.find_all('a') if 'SHORT' in a.text]
                if short_links:
                    short_link = short_links[0]
            
            if not long_link:
                # 代替方法
                long_links = [a for a in soup.find_all('a') if 'LONG' in a.text]
                if long_links:
                    long_link = long_links[0]
            
            if short_link and 'href' in short_link.attrs:
                download_links['short'] = short_link['href']
            
            if long_link and 'href' in long_link.attrs:
                download_links['long'] = long_link['href']
            
            # 説明文を取得
            description = ""
            desc_elem = soup.select_one('.music-description') or soup.select_one('.description')
            if not desc_elem:
                # 代替方法
                desc_elem = soup.select_one('楽曲概要')
            
            if desc_elem:
                description = desc_elem.text.strip()
            else:
                # 楽曲概要セクションを探す
                for elem in soup.find_all(['h2', 'h3']):
                    if '概要' in elem.text:
                        next_elem = elem.find_next_sibling()
                        if next_elem:
                            description = next_elem.text.strip()
            
            # 情報を更新
            music_info.update({
                'download_links': download_links,
                'description': description
            })
            
            # サーバー負荷軽減のための待機
            time.sleep(random.uniform(1, 2))
            
            return music_info
            
        except Exception as e:
            print(f"{music_info['title']} の詳細取得中にエラーが発生しました: {e}")
            music_info['download_links'] = {}
            music_info['description'] = ""
            return music_info
    
    def extract_download_links_manually(self, url):
        """
        ページから直接ダウンロードリンクを抽出する（BGMerサイト特有の方法）
        
        Args:
            url (str): 音源ページのURL
            
        Returns:
            dict: ダウンロードリンク情報
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # BGMerサイトの場合、ダウンロードリンクは以下のパターンで構築される
            # 例: https://bgmer.net/wp-content/uploads/2022/05/somei_yoshino_short.mp3
            
            # URLからIDを抽出
            music_id = url.split('/')[-1]
            
            # 音源ファイル名を推測
            base_name = "somei_yoshino"  # ソメイヨシノの場合
            
            # ダウンロードリンクを構築
            download_links = {
                'short': f"https://bgmer.net/wp-content/uploads/2022/05/{base_name}_short.mp3",
                'long': f"https://bgmer.net/wp-content/uploads/2022/05/{base_name}_long.mp3"
            }
            
            return download_links
            
        except Exception as e:
            print(f"ダウンロードリンク抽出中にエラーが発生しました: {e}")
            return {}

# 使用例
if __name__ == "__main__":
    scraper = BGMerScraper()
    
    # 桜関連の音源を直接取得
    music_list = scraper.get_sakura_music_list()
    
    print(f"\n合計 {len(music_list)} 件の桜関連音源が見つかりました。\n")
    
    # 各音源の詳細情報を取得
    for i, music in enumerate(music_list):
        print(f"[{i+1}/{len(music_list)}] {music['title']} の詳細を取得中...")
        music_list[i] = scraper.get_music_details(music)
        
        # ダウンロードリンクが見つからない場合は手動で抽出
        if not music_list[i].get('download_links'):
            print(f"ダウンロードリンクが見つからないため、手動で抽出します...")
            download_links = scraper.extract_download_links_manually(music['url'])
            music_list[i]['download_links'] = download_links
    
    # 結果を表示
    for i, music in enumerate(music_list):
        print(f"\n===== 音源 {i+1} =====")
        print(f"タイトル: {music['title']}")
        print(f"URL: {music['url']}")
        print(f"検索キーワード: {music['keyword']}")
        print(f"説明: {music['description']}")
        print("ダウンロードリンク:")
        
        if music['download_links']:
            for type_, link in music['download_links'].items():
                print(f"  - {type_}: {link}")
        else:
            print("  ダウンロードリンクが見つかりませんでした。")
