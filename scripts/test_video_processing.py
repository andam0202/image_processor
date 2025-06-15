#!/usr/bin/env python3
"""動画処理機能のテストスクリプト."""

import sys
from pathlib import Path
import logging

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from image_processor.video.frame_extractor import FrameExtractor
from image_processor.core.common import setup_logging, format_file_size
from image_processor.types import VideoConfig


def main() -> None:
    """メイン関数."""
    # ログ設定
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🎬 動画処理テストを開始します...")
    
    # ファイルパス設定
    input_file = Path("data/input/test_movie1.mp4")
    output_dir = Path("data/output/test_frames")
    
    # ファイル存在確認
    if not input_file.exists():
        print(f"❌ エラー: 動画ファイルが見つかりません: {input_file}")
        return
    
    # ファイル情報表示
    file_size = input_file.stat().st_size
    print(f"📁 入力ファイル: {input_file.name}")
    print(f"📊 ファイルサイズ: {format_file_size(file_size)}")
    
    # フレーム抽出器を初期化
    extractor = FrameExtractor()
    
    # FFmpeg確認
    print("🔧 FFmpegの確認中...")
    if not extractor.check_ffmpeg():
        print("❌ エラー: FFmpegが見つかりません。")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: https://ffmpeg.org/download.html")
        return
    else:
        print("✅ FFmpegが利用可能です")
    
    # 動画情報取得
    print("📹 動画情報を取得中...")
    video_info = extractor.get_video_info(input_file)
    
    if video_info:
        print("動画情報:")
        for key, value in video_info.items():
            print(f"  {key}: {value}")
    else:
        print("⚠️  動画情報の取得に失敗しました（処理は続行）")
    
    # フレーム抽出設定
    config: VideoConfig = {
        "frame_interval": 30,  # 30フレームごと
        "start_time": 0.0,     # 開始時間
        # "end_time": 10.0,    # 最初の10秒間のみ（オプション）
    }
    
    print(f"⚙️  設定: {config['frame_interval']}フレームごとに抽出")
    
    # フレーム抽出実行
    print("🎞️  フレーム抽出を開始...")
    result = extractor.extract_frames(
        video_path=input_file,
        output_dir=output_dir,
        config=config,
    )
    
    # 結果表示
    if result["status"] == "success":
        print(f"✅ フレーム抽出成功！")
        print(f"⏱️  処理時間: {result['processing_time']:.2f}秒")
        print(f"📂 出力先: {result['output_path']}")
        
        # 抽出されたフレーム数を確認
        if result["output_path"]:
            frame_files = list(result["output_path"].glob("*.png"))
            print(f"🖼️  抽出フレーム数: {len(frame_files)}枚")
            
            if frame_files:
                print("最初の5つのフレーム:")
                for i, frame_file in enumerate(sorted(frame_files)[:5]):
                    frame_size = format_file_size(frame_file.stat().st_size)
                    print(f"  {i+1}. {frame_file.name} ({frame_size})")
                
                if len(frame_files) > 5:
                    print(f"  ... 他 {len(frame_files) - 5} ファイル")
    else:
        print(f"❌ エラー: {result['error_message']}")
        print(f"⏱️  処理時間: {result['processing_time']:.2f}秒")
    
    # レポート作成
    report_path = output_dir / "extraction_report.md"
    extractor.create_summary_report([result], report_path)
    print(f"📄 レポートを作成: {report_path}")
    
    print("\n🎉 テスト完了！")


if __name__ == "__main__":
    main()