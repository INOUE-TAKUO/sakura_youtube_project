#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
桜を題材にしたYouTube動画自動生成スクリプト
====================================

このスクリプトは桜の映像素材を使用して、自動的に高品質な動画を生成します。
MoviePy、OpenCV、Pillowなどのライブラリを使用して、映像編集、テキストオーバーレイ、
音声合成などの機能を実装しています。

使用方法:
    python sakura_video_generator.py --output output.mp4 --style ranking --length 180

オプション:
    --output: 出力ファイル名（デフォルト: sakura_video.mp4）
    --style: 動画スタイル（ranking, regional, theme, seasonal）
    --length: 動画の長さ（秒）（デフォルト: 180）
    --title: 動画のタイトル（デフォルト: 自動生成）
    --bgm: BGMファイルのパス（デフォルト: ランダム選択）
    --narration: ナレーションの有無（True/False）（デフォルト: False）
"""

import os
import sys
import random
import argparse
import glob
import textwrap
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, vfx, afx, VideoClip
)
from pydub import AudioSegment

# プロジェクトのルートディレクトリ
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# リソースディレクトリ
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")
VIDEO_DIR = os.path.join(RESOURCES_DIR, "videos")
MUSIC_DIR = os.path.join(RESOURCES_DIR, "music")
SFX_DIR = os.path.join(RESOURCES_DIR, "sfx")
FONT_DIR = os.path.join(RESOURCES_DIR, "fonts")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# デフォルト設定
DEFAULT_RESOLUTION = (3840, 2160)  # 4K
DEFAULT_FPS = 30
DEFAULT_DURATION = 180  # 3分
DEFAULT_BITRATE = "20000k"
DEFAULT_CODEC = "libx264"
DEFAULT_AUDIO_CODEC = "aac"
DEFAULT_AUDIO_BITRATE = "192k"

# フォント設定
DEFAULT_FONT = "Arial" if os.name == "nt" else "DejaVuSans"
DEFAULT_FONT_SIZE = 60
DEFAULT_FONT_COLOR = "white"
DEFAULT_FONT_STROKE_COLOR = "black"
DEFAULT_FONT_STROKE_WIDTH = 2

# 動画スタイル
VIDEO_STYLES = {
    "ranking": "日本の桜名所ランキング",
    "regional": "地域別桜の名所",
    "theme": "テーマ別桜の魅力",
    "seasonal": "桜の開花から散るまで"
}

# 地域リスト
REGIONS = [
    "北海道", "東北", "関東", "中部", "関西", "中国", "四国", "九州", "沖縄"
]

# テーマリスト
THEMES = [
    "夜桜", "桜と富士山", "桜と城", "桜と川", "桜と湖", "桜と伝統建築"
]

class SakuraVideoGenerator:
    """桜の動画を自動生成するクラス"""
    
    def __init__(
        self,
        output_file: str = "sakura_video.mp4",
        style: str = "ranking",
        length: int = DEFAULT_DURATION,
        title: Optional[str] = None,
        bgm_file: Optional[str] = None,
        use_narration: bool = False
    ):
        """
        初期化メソッド
        
        Args:
            output_file: 出力ファイル名
            style: 動画スタイル（ranking, regional, theme, seasonal）
            length: 動画の長さ（秒）
            title: 動画のタイトル（Noneの場合は自動生成）
            bgm_file: BGMファイルのパス（Noneの場合はランダム選択）
            use_narration: ナレーションの有無
        """
        self.output_file = os.path.join(OUTPUT_DIR, output_file)
        self.style = style
        self.length = length
        self.title = title
        self.bgm_file = bgm_file
        self.use_narration = use_narration
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 動画素材のリストを取得
        self.video_files = self._get_video_files()
        
        # BGMファイルのリストを取得
        self.music_files = self._get_music_files()
        
        # 効果音ファイルのリストを取得
        self.sfx_files = self._get_sfx_files()
        
        # タイトルが指定されていない場合は自動生成
        if self.title is None:
            self.title = self._generate_title()
        
        # BGMが指定されていない場合はランダム選択
        if self.bgm_file is None and self.music_files:
            self.bgm_file = random.choice(self.music_files)
    
    def _get_video_files(self) -> List[str]:
        """動画素材のリストを取得"""
        if not os.path.exists(VIDEO_DIR):
            print(f"警告: 動画ディレクトリが見つかりません: {VIDEO_DIR}")
            return []
        
        video_files = []
        for ext in ["*.mp4", "*.mov", "*.avi", "*.mkv"]:
            video_files.extend(glob.glob(os.path.join(VIDEO_DIR, ext)))
        
        if not video_files:
            print(f"警告: 動画ファイルが見つかりません: {VIDEO_DIR}")
        
        return video_files
    
    def _get_music_files(self) -> List[str]:
        """BGM素材のリストを取得"""
        if not os.path.exists(MUSIC_DIR):
            print(f"警告: 音楽ディレクトリが見つかりません: {MUSIC_DIR}")
            return []
        
        music_files = []
        for ext in ["*.mp3", "*.wav", "*.m4a", "*.ogg"]:
            music_files.extend(glob.glob(os.path.join(MUSIC_DIR, ext)))
        
        if not music_files:
            print(f"警告: 音楽ファイルが見つかりません: {MUSIC_DIR}")
        
        return music_files
    
    def _get_sfx_files(self) -> List[str]:
        """効果音素材のリストを取得"""
        if not os.path.exists(SFX_DIR):
            print(f"警告: 効果音ディレクトリが見つかりません: {SFX_DIR}")
            return []
        
        sfx_files = []
        for ext in ["*.mp3", "*.wav", "*.m4a", "*.ogg"]:
            sfx_files.extend(glob.glob(os.path.join(SFX_DIR, ext)))
        
        return sfx_files
    
    def _generate_title(self) -> str:
        """動画スタイルに基づいてタイトルを自動生成"""
        current_year = datetime.now().year
        
        if self.style == "ranking":
            return f"{current_year}年 日本の美しい桜名所ベスト10"
        elif self.style == "regional":
            region = random.choice(REGIONS)
            return f"{region}の絶景桜スポット特集 {current_year}"
        elif self.style == "theme":
            theme = random.choice(THEMES)
            return f"日本の{theme}特集 {current_year}"
        elif self.style == "seasonal":
            return f"桜の一生 〜開花から散るまでの美しい姿〜 {current_year}"
        else:
            return f"日本の美しい桜特集 {current_year}"
    
    def _create_title_clip(self, duration: float = 5.0) -> VideoClip:
        """タイトルクリップを作成"""
        # 背景画像（黒背景）
        background = ImageClip(
            np.zeros((DEFAULT_RESOLUTION[1], DEFAULT_RESOLUTION[0], 3), dtype=np.uint8)
        ).set_duration(duration)
        
        # メインタイトル
        main_title = TextClip(
            self.title,
            fontsize=DEFAULT_FONT_SIZE * 2,
            color=DEFAULT_FONT_COLOR,
            stroke_color=DEFAULT_FONT_STROKE_COLOR,
            stroke_width=DEFAULT_FONT_STROKE_WIDTH,
            font=DEFAULT_FONT
        ).set_position(('center', 'center')).set_duration(duration)
        
        # サブタイトル（英語）
        sub_title = TextClip(
            f"Beautiful Cherry Blossoms in Japan {datetime.now().year}",
            fontsize=DEFAULT_FONT_SIZE,
            color=DEFAULT_FONT_COLOR,
            font=DEFAULT_FONT
        ).set_position(('center', 'center')).set_duration(duration)
        
        # タイトルとサブタイトルを合成
        title_clip = CompositeVideoClip([
            background,
            main_title.set_position(('center', DEFAULT_RESOLUTION[1] // 2 - DEFAULT_FONT_SIZE * 2)),
            sub_title.set_position(('center', DEFAULT_RESOLUTION[1] // 2 + DEFAULT_FONT_SIZE))
        ], size=DEFAULT_RESOLUTION)
        
        # フェードイン・フェードアウト効果を追加
        title_clip = title_clip.fadein(1.0).fadeout(1.0)
        
        return title_clip
    
    def _create_ending_clip(self, duration: float = 5.0) -> VideoClip:
        """エンディングクリップを作成"""
        # 背景画像（黒背景）
        background = ImageClip(
            np.zeros((DEFAULT_RESOLUTION[1], DEFAULT_RESOLUTION[0], 3), dtype=np.uint8)
        ).set_duration(duration)
        
        # エンディングテキスト
        ending_text = TextClip(
            "ご視聴ありがとうございました",
            fontsize=DEFAULT_FONT_SIZE * 1.5,
            color=DEFAULT_FONT_COLOR,
            stroke_color=DEFAULT_FONT_STROKE_COLOR,
            stroke_width=DEFAULT_FONT_STROKE_WIDTH,
            font=DEFAULT_FONT
        ).set_position(('center', 'center')).set_duration(duration)
        
        # チャンネル登録テキスト
        subscribe_text = TextClip(
            "チャンネル登録よろしくお願いします",
            fontsize=DEFAULT_FONT_SIZE,
            color=DEFAULT_FONT_COLOR,
            font=DEFAULT_FONT
        ).set_position(('center', 'center')).set_duration(duration)
        
        # エンディングクリップを合成
        ending_clip = CompositeVideoClip([
            background,
            ending_text.set_position(('center', DEFAULT_RESOLUTION[1] // 2 - DEFAULT_FONT_SIZE * 2)),
            subscribe_text.set_position(('center', DEFAULT_RESOLUTION[1] // 2 + DEFAULT_FONT_SIZE))
        ], size=DEFAULT_RESOLUTION)
        
        # フェードイン・フェードアウト効果を追加
        ending_clip = ending_clip.fadein(1.0).fadeout(1.0)
        
        return ending_clip
    
    def _prepare_video_segments(self) -> List[VideoFileClip]:
        """動画セグメントを準備"""
        if not self.video_files:
            raise ValueError("動画ファイルが見つかりません。素材を追加してください。")
        
        # 動画の合計時間（タイトルとエンディングを除く）
        content_duration = self.length - 10.0  # タイトルとエンディングで10秒
        
        # 各セグメントの長さ（10〜15秒）
        segment_durations = []
        remaining_duration = content_duration
        
        while remaining_duration > 0:
            duration = min(random.uniform(10.0, 15.0), remaining_duration)
            segment_durations.append(duration)
            remaining_duration -= duration
        
        # 動画ファイルをランダムに選択（重複を避ける）
        selected_videos = random.sample(
            self.video_files,
            min(len(self.video_files), len(segment_durations))
        )
        
        # 足りない場合はランダムに追加
        while len(selected_videos) < len(segment_durations):
            selected_videos.append(random.choice(self.video_files))
        
        # 動画セグメントを作成
        video_segments = []
        for video_file, duration in zip(selected_videos, segment_durations):
            try:
                clip = VideoFileClip(video_file)
                
                # 動画の長さが指定した長さより短い場合はループ
                if clip.duration < duration:
                    clip = clip.loop(duration=duration)
                else:
                    # ランダムな開始位置から指定した長さだけ切り出し
                    max_start = max(0, clip.duration - duration)
                    start = random.uniform(0, max_start)
                    clip = clip.subclip(start, start + duration)
                
                # 解像度を統一
                if clip.size != DEFAULT_RESOLUTION:
                    clip = clip.resize(height=DEFAULT_RESOLUTION[1])
                    
                    # リサイズ後の幅が目標解像度より大きい場合はクロップ
                    if clip.size[0] > DEFAULT_RESOLUTION[0]:
                        x_center = clip.size[0] // 2
                        x1 = x_center - DEFAULT_RESOLUTION[0] // 2
                        clip = clip.crop(x1=x1, y1=0, x2=x1 + DEFAULT_RESOLUTION[0], y2=DEFAULT_RESOLUTION[1])
                    # リサイズ後の幅が目標解像度より小さい場合は黒帯を追加
                    elif clip.size[0] < DEFAULT_RESOLUTION[0]:
                        bg = ImageClip(
                            np.zeros((DEFAULT_RESOLUTION[1], DEFAULT_RESOLUTION[0], 3), dtype=np.uint8)
                        ).set_duration(clip.duration)
                        x_offset = (DEFAULT_RESOLUTION[0] - clip.size[0]) // 2
                        clip = CompositeVideoClip(
                            [bg, clip.set_position((x_offset, 0))],
                            size=DEFAULT_RESOLUTION
                        )
                
                # トランジション効果を追加（フェードイン・フェードアウト）
                clip = clip.fadein(0.5).fadeout(0.5)
                
                video_segments.append(clip)
            except Exception as e:
                print(f"警告: 動画ファイルの処理中にエラーが発生しました: {video_file}")
                print(f"エラー詳細: {str(e)}")
                continue
        
        return video_segments
    
    def _add_text_overlays(self, video_segments: List[VideoFileClip]) -> List[VideoFileClip]:
        """テキストオーバーレイを追加"""
        segments_with_text = []
        
        for i, clip in enumerate(video_segments):
            # スタイルに応じたテキスト内容を生成
            if self.style == "ranking":
                text = f"第{len(video_segments) - i}位"
                subtext = f"Rank {len(video_segments) - i}"
            elif self.style == "regional":
                text = random.choice(REGIONS)
                subtext = f"Region: {text}"
            elif self.style == "theme":
                text = random.choice(THEMES)
                subtext = f"Theme: {text}"
            elif self.style == "seasonal":
                stages = ["つぼみ", "開花", "満開", "散り始め", "葉桜"]
                text = stages[min(i, len(stages) - 1)]
                subtext = f"Stage: {text}"
            else:
                text = f"桜の風景 {i + 1}"
                subtext = f"Cherry Blossom Scene {i + 1}"
            
            # メインテキスト
            main_text = TextClip(
                text,
                fontsize=DEFAULT_FONT_SIZE * 1.5,
                color=DEFAULT_FONT_COLOR,
                stroke_color=DEFAULT_FONT_STROKE_COLOR,
                stroke_width=DEFAULT_FONT_STROKE_WIDTH,
                font=DEFAULT_FONT
            ).set_position(('center', 50)).set_duration(clip.duration)
            
            # サブテキスト
            sub_text = TextClip(
                subtext,
                fontsize=DEFAULT_FONT_SIZE,
                color=DEFAULT_FONT_COLOR,
                font=DEFAULT_FONT
            ).set_position(('center', 50 + DEFAULT_FONT_SIZE * 2)).set_duration(clip.duration)
            
            # テキストを追加
            clip_with_text = CompositeVideoClip(
                [clip, main_text, sub_text],
                size=DEFAULT_RESOLUTION
            )
            
            segments_with_text.append(clip_with_text)
        
        return segments_with_text
    
    def _add_audio(self, video: VideoClip) -> VideoClip:
        """BGMと効果音を追加"""
        if self.bgm_file and os.path.exists(self.bgm_file):
            try:
                # BGMを読み込み
                bgm = AudioFileClip(self.bgm_file)
                
                # 動画の長さに合わせてループ
                if bgm.duration < video.duration:
                    bgm = afx.audio_loop(bgm, duration=video.duration)
                else:
                    bgm = bgm.subclip(0, video.duration)
                
                # 音量を調整（0.5 = 50%）
                bgm = bgm.volumex(0.5)
                
                # BGMを動画に追加
                video = video.set_audio(bgm)
            except Exception as e:
                print(f"警告: BGMの処理中にエラーが発生しました: {self.bgm_file}")
                print(f"エラー詳細: {str(e)}")
        
        return video
    
    def generate_video(self) -> str:
        """動画を生成"""
        try:
            print(f"動画生成を開始します: スタイル={self.style}, 長さ={self.length}秒")
            
            # タイトルクリップを作成
            title_clip = self._create_title_clip()
            
            # エンディングクリップを作成
            ending_clip = self._create_ending_clip()
            
            # 動画セグメントを準備
            video_segments = self._prepare_video_segments()
            
            # テキストオーバーレイを追加
            video_segments = self._add_text_overlays(video_segments)
            
            # すべてのクリップを連結
            final_video = concatenate_videoclips(
                [title_clip] + video_segments + [ending_clip]
            )
            
            # BGMを追加
            final_video = self._add_audio(final_video)
            
            # 動画を書き出し
            print(f"動画を書き出しています: {self.output_file}")
            final_video.write_videofile(
                self.output_file,
                fps=DEFAULT_FPS,
                codec=DEFAULT_CODEC,
                bitrate=DEFAULT_BITRATE,
                audio_codec=DEFAULT_AUDIO_CODEC,
                audio_bitrate=DEFAULT_AUDIO_BITRATE,
                threads=4
            )
            
            print(f"動画生成が完了しました: {self.output_file}")
            return self.output_file
            
        except Exception as e:
            print(f"エラー: 動画生成中に問題が発生しました")
            print(f"エラー詳細: {str(e)}")
            raise
    
def parse_arguments():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description="桜を題材にしたYouTube動画自動生成スクリプト")
    
    parser.add_argument(
        "--output", "-o",
        default="sakura_video.mp4",
        help="出力<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>