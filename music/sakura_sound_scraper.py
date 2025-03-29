import os
import sys
from bgmer_scraper_optimized import BGMerScraper
from sakura_sound_downloader import SakuraSoundDownloader

def main():
    """
    メイン関数 - 桜関連の音源をスクレイピングしてダウンロードする
    """
    # 出力ディレクトリの設定
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    print("=" * 50)
    print("日本の桜に関連する無料音源スクレイピングツール")
    print("=" * 50)
    
    # スクレイパーを初期化
    scraper = BGMerScraper()
    
    # 桜関連の音源を直接取得
    print("\n1. 桜関連の音源を取得中...")
    music_list = scraper.get_sakura_music_list()
    
    if not music_list:
        print("桜関連の音源が見つかりませんでした。")
        return
    
    print(f"\n合計 {len(music_list)} 件の桜関連音源が見つかりました。")
    
    # 各音源の詳細情報を取得
    print("\n2. 音源の詳細情報を取得中...")
    for i, music in enumerate(music_list):
        print(f"  [{i+1}/{len(music_list)}] {music['title']} の詳細を取得中...")
        music_list[i] = scraper.get_music_details(music)
        
        # ダウンロードリンクが見つからない場合は手動で抽出
        if not music_list[i].get('download_links'):
            print(f"  ダウンロードリンクが見つからないため、手動で抽出します...")
            download_links = scraper.extract_download_links_manually(music['url'])
            music_list[i]['download_links'] = download_links
    
    # 音源情報の表示
    print("\n3. 見つかった音源の情報:")
    for i, music in enumerate(music_list):
        print(f"\n  === 音源 {i+1} ===")
        print(f"  タイトル: {music['title']}")
        print(f"  URL: {music['url']}")
        print(f"  検索キーワード: {music['keyword']}")
        
        if music.get('description'):
            print(f"  説明: {music['description'][:100]}..." if len(music['description']) > 100 else f"  説明: {music['description']}")
        
        print("  ダウンロードリンク:")
        if music.get('download_links'):
            for type_, link in music['download_links'].items():
                print(f"    - {type_}: {link}")
        else:
            print("    ダウンロードリンクが見つかりませんでした。")
    
    # ダウンロード
    print("\n4. 音源のダウンロード:")
    
    # ダウンローダーを初期化
    downloader = SakuraSoundDownloader(download_dir=download_dir)
    
    # 全ての音源をダウンロード
    downloaded_files = downloader.download_all_music(music_list)
    
    # 結果の表示
    print("\n5. ダウンロード結果:")
    if downloaded_files:
        print(f"  合計 {len(downloaded_files)} 件の音源をダウンロードしました。")
        for file_path in downloaded_files:
            print(f"  - {file_path}")
    else:
        print("  音源のダウンロードに失敗しました。")
    
    print("\n処理が完了しました！")

if __name__ == "__main__":
    main()
