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
    
    def search_sakura_music(self, keywords=["桜", "サクラ", "さくら", "ソメイヨシノ"]):
        """
        指定したキーワードに関連する音源を検索する
        
        Args:
            keywords (list): 検索キーワードのリスト
            
        Returns:
            list: 検索結果の音源情報リスト
        """
        music_list = []
        
        for keyword in keywords:
            print(f"キーワード '{keyword}' で検索中...")
            
            # 検索URLを構築
            search_url = f"{self.base_url}/?s={urllib.parse.quote(keyword)}"
            
            try:
                response = self.session.get(search_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 検索結果から音源情報を抽出
                music_items = soup.select('article.music')
                
                for item in music_items:
                    title_elem = item.select_one('h2.music-title a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    url = title_elem.get('href')
                    
                    # 重複チェック
                    if any(music['url'] == url for music in music_list):
                        continue
                    
                    music_info = {
                        'title': title,
                        'url': url,
                        'keyword': keyword
                    }
                    
                    music_list.append(music_info)
                    print(f"見つかった音源: {title}")
                
                # サーバー負荷軽減のための待機
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"検索中にエラーが発生しました: {e}")
        
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
            
            # SHORT版とLONG版のリンクを探す
            short_link = soup.select_one('a:contains("SHORT")')
            long_link = soup.select_one('a:contains("LONG")')
            
            if short_link:
                download_links['short'] = short_link.get('href')
            
            if long_link:
                download_links['long'] = long_link.get('href')
            
            # 代替方法: クラスやIDで検索
            if not download_links:
                download_elements = soup.select('.download-button a, .btn-download')
                for elem in download_elements:
                    text = elem.text.lower()
                    href = elem.get('href')
                    if href and href.endswith('.mp3'):
                        if 'short' in text:
                            download_links['short'] = href
                        elif 'long' in text:
                            download_links['long'] = href
                        else:
                            download_links['default'] = href
            
            # 説明文を取得
            description = ""
            desc_elem = soup.select_one('.music-description, .description')
            if desc_elem:
                description = desc_elem.text.strip()
            
            # 情報を更新
            music_info.update({
                'download_links': download_links,
                'description': description
            })
            
            # サーバー負荷軽減のための待機
            time.sleep(random.uniform(1, 3))
            
            return music_info
            
        except Exception as e:
            print(f"{music_info['title']} の詳細取得中にエラーが発生しました: {e}")
            music_info['download_links'] = {}
            music_info['description'] = ""
            return music_info
    
    def extract_download_links_from_page(self, url):
        """
        ページから直接ダウンロードリンクを抽出する
        
        Args:
            url (str): 音源ページのURL
            
        Returns:
            dict: ダウンロードリンク情報
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # JavaScriptを解析してダウンロードリンクを探す
            scripts = soup.find_all('script')
            download_links = {}
            
            for script in scripts:
                if script.string:
                    # MP3ファイルへのリンクを探す
                    mp3_urls = re.findall(r'https?://[^\s"\']+\.mp3', script.string)
                    
                    for url in mp3_urls:
                        if 'short' in url.lower():
                            download_links['short'] = url
                        elif 'long' in url.lower():
                            download_links['long'] = url
                        else:
                            download_links['default'] = url
            
            # HTMLからも探す
            links = soup.find_all('a', href=re.compile(r'\.mp3$'))
            for link in links:
                href = link.get('href')
                text = link.text.lower()
                
                if 'short' in text:
                    download_links['short'] = href
                elif 'long' in text:
                    download_links['long'] = href
                else:
                    download_links.setdefault('default', href)
            
            return download_links
            
        except Exception as e:
            print(f"ダウンロードリンク抽出中にエラーが発生しました: {e}")
            return {}

# 使用例
if __name__ == "__main__":
    scraper = BGMerScraper()
    
    # 桜関連の音源を検索
    music_list = scraper.search_sakura_music()
    
    print(f"\n合計 {len(music_list)} 件の桜関連音源が見つかりました。\n")
    
    # 各音源の詳細情報を取得
    for i, music in enumerate(music_list):
        print(f"[{i+1}/{len(music_list)}] {music['title']} の詳細を取得中...")
        music_list[i] = scraper.get_music_details(music)
    
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
