#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
桜動画生成とYouTubeアップロードのテストスクリプト
==========================================

このスクリプトは桜動画生成機能とYouTubeアップロード機能をテストします。
テスト用のダミー素材を使用して、動画生成からアップロードまでの一連の流れを確認します。

使用方法:
    python test_sakura_video.py --test-type generation
    python test_sakura_video.py --test-type upload
    python test_sakura_video.py --test-type all
"""

import os
import sys
import argparse
import subprocess
import time
import glob
from typing import List, Dict, Optional, Any

# プロジェクトのルートディレクトリ
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ソースディレクトリ
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# リソースディレクトリ
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")
VIDEO_DIR = os.path.join(RESOURCES_DIR, "videos")
MUSIC_DIR = os.path.join(RESOURCES_DIR, "music")
SFX_DIR = os.path.join(RESOURCES_DIR, "sfx")

# 出力ディレクトリ
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# テスト用ダミー素材ディレクトリ
TEST_DIR = os.path.join(PROJECT_ROOT, "test")
TEST_VIDEOS_DIR = os.path.join(TEST_DIR, "videos")
TEST_MUSIC_DIR = os.path.join(TEST_DIR, "music")

def setup_test_environment():
    """テスト環境をセットアップ"""
    print("テスト環境をセットアップしています...")
    
    # 必要なディレクトリを作成
    os.makedirs(TEST_DIR, exist_ok=True)
    os.makedirs(TEST_VIDEOS_DIR, exist_ok=True)
    os.makedirs(TEST_MUSIC_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # テスト用のダミー動画素材を確認
    if not glob.glob(os.path.join(TEST_VIDEOS_DIR, "*.mp4")):
        print("警告: テスト用の動画素材が見つかりません。")
        print(f"テスト動画を {TEST_VIDEOS_DIR} に配置してください。")
        print("または、実際の素材ディレクトリを使用します。")
    
    # テスト用のダミー音楽素材を確認
    if not glob.glob(os.path.join(TEST_MUSIC_DIR, "*.mp3")):
        print("警告: テスト用の音楽素材が見つかりません。")
        print(f"テスト音楽を {TEST_MUSIC_DIR} に配置してください。")
        print("または、実際の素材ディレクトリを使用します。")
    
    print("テスト環境のセットアップが完了しました。")

def test_video_generation(use_test_data: bool = True) -> str:
    """動画生成機能をテスト"""
    print("動画生成機能のテストを開始します...")
    
    # 出力ファイル名
    output_file = os.path.join(OUTPUT_DIR, f"test_sakura_video_{int(time.time())}.mp4")
    
    # 素材ディレクトリ
    videos_dir = TEST_VIDEOS_DIR if use_test_data and glob.glob(os.path.join(TEST_VIDEOS_DIR, "*.mp4")) else VIDEO_DIR
    music_dir = TEST_MUSIC_DIR if use_test_data and glob.glob(os.path.join(TEST_MUSIC_DIR, "*.mp3")) else MUSIC_DIR
    
    # 動画生成スクリプトのパス
    generator_script = os.path.join(SRC_DIR, "sakura_video_generator.py")
    
    # 動画生成コマンド
    command = [
        sys.executable,
        generator_script,
        "--output", output_file,
        "--style", "ranking",
        "--length", "30",  # テスト用に短い動画
        "--title", "桜動画生成テスト"
    ]
    
    # 環境変数で素材ディレクトリを指定
    env = os.environ.copy()
    env["VIDEO_DIR"] = videos_dir
    env["MUSIC_DIR"] = music_dir
    
    try:
        print(f"コマンドを実行: {' '.join(command)}")
        process = subprocess.run(
            command,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("コマンド出力:")
        print(process.stdout)
        
        if os.path.exists(output_file):
            print(f"動画生成テストが成功しました: {output_file}")
            return output_file
        else:
            print("エラー: 動画ファイルが生成されませんでした。")
            print("エラー出力:")
            print(process.stderr)
            return ""
    
    except subprocess.CalledProcessError as e:
        print(f"エラー: 動画生成中にエラーが発生しました (終了コード: {e.returncode})")
        print("エラー出力:")
        print(e.stderr)
        return ""
    except Exception as e:
        print(f"エラー: 予期しない例外が発生しました: {str(e)}")
        return ""

def test_youtube_upload(video_file: str) -> bool:
    """YouTube アップロード機能をテスト"""
    if not video_file or not os.path.exists(video_file):
        print(f"エラー: アップロードする動画ファイルが見つかりません: {video_file}")
        return False
    
    print(f"YouTube アップロード機能のテストを開始します: {video_file}")
    
    # アップロードスクリプトのパス
    uploader_script = os.path.join(SRC_DIR, "youtube_uploader.py")
    
    # アップロードコマンド
    command = [
        sys.executable,
        uploader_script,
        "--video", video_file,
        "--title", f"桜動画アップロードテスト {int(time.time())}",
        "--privacy", "private"  # テスト用に非公開設定
    ]
    
    try:
        print(f"コマンドを実行: {' '.join(command)}")
        process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("コマンド出力:")
        print(process.stdout)
        
        if "アップロードされた動画ID" in process.stdout:
            print("YouTube アップロードテストが成功しました。")
            return True
        else:
            print("警告: アップロードは完了しましたが、動画IDが見つかりません。")
            return True
    
    except subprocess.CalledProcessError as e:
        print(f"エラー: アップロード中にエラーが発生しました (終了コード: {e.returncode})")
        print("エラー出力:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"エラー: 予期しない例外が発生しました: {str(e)}")
        return False

def parse_arguments():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description="桜動画生成とYouTubeアップロードのテスト")
    
    parser.add_argument(
        "--test-type",
        choices=["generation", "upload", "all"],
        default="all",
        help="テストタイプ (generation: 動画生成のみ, upload: アップロードのみ, all: 両方)"
    )
    
    parser.add_argument(
        "--video-file",
        help="アップロードテスト用の動画ファイル (upload または all テストで使用)"
    )
    
    parser.add_argument(
        "--use-test-data",
        action="store_true",
        help="テスト用のダミーデータを使用する"
    )
    
    return parser.parse_args()

def main():
    """メイン関数"""
    args = parse_arguments()
    
    # テスト環境をセットアップ
    setup_test_environment()
    
    # テスト結果
    generation_success = False
    upload_success = False
    generated_video = ""
    
    # 動画生成テスト
    if args.test_type in ["generation", "all"]:
        generated_video = test_video_generation(args.use_test_data)
        generation_success = bool(generated_video)
    
    # アップロードテスト
    if args.test_type in ["upload", "all"]:
        video_file = args.video_file if args.test_type == "upload" and args.video_file else generated_video
        if video_file:
            upload_success = test_youtube_upload(video_file)
        else:
            print("エラー: アップロードテスト用の動画ファイルが指定されていません。")
            upload_success = False
    
    # テスト結果のサマリー
    print("\nテスト結果サマリー:")
    if args.test_type in ["generation", "all"]:
        print(f"動画生成テスト: {'成功' if generation_success else '失敗'}")
    if args.test_type in ["upload", "all"]:
        print(f"YouTube アップロードテスト: {'成功' if upload_success else '失敗'}")
    
    # 終了コード
    if args.test_type == "generation" and not generation_success:
        sys.exit(1)
    elif args.test_type == "upload" and not upload_success:
        sys.exit(1)
    elif args.test_type == "all" and (not generation_success or not upload_success):
        sys.exit(1)
    else:
        print("すべてのテストが成功しました。")
        sys.exit(0)

if __name__ == "__main__":
    main()
