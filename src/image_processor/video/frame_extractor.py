"""動画からフレームを抽出する機能."""

import subprocess
import logging
from pathlib import Path
from typing import Iterator
import time

from image_processor.types import ProcessorStatus, ProcessingResult, VideoConfig
from image_processor.core.common import create_processing_result, format_file_size


class FrameExtractor:
    """動画からフレームを抽出するクラス."""

    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        """フレーム抽出器を初期化。

        Parameters
        ----------
        ffmpeg_path : str
            FFmpegの実行パス
        """
        self.ffmpeg_path = ffmpeg_path
        self.logger = logging.getLogger(__name__)

    def check_ffmpeg(self) -> bool:
        """FFmpegが利用可能かチェック。

        Returns
        -------
        bool
            FFmpegが利用可能な場合True
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_video_info(self, video_path: Path) -> dict[str, str] | None:
        """動画の基本情報を取得。

        Parameters
        ----------
        video_path : Path
            動画ファイルのパス

        Returns
        -------
        dict[str, str] | None
            動画情報（duration, fps, width, height等）、失敗時はNone
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", str(video_path),
                "-f", "null", "-"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            # FFmpegは動画情報をstderrに出力
            output = result.stderr
            
            # 基本的な情報を抽出
            info = {}
            
            # 時間長を抽出
            if "Duration:" in output:
                duration_line = [line for line in output.split('\n') if 'Duration:' in line][0]
                duration = duration_line.split('Duration:')[1].split(',')[0].strip()
                info['duration'] = duration
            
            # フレームレートを抽出
            if " fps" in output:
                fps_line = [line for line in output.split('\n') if ' fps' in line][0]
                fps = fps_line.split(' fps')[0].split()[-1]
                info['fps'] = fps
            
            # 解像度を抽出
            if "Video:" in output:
                video_line = [line for line in output.split('\n') if 'Video:' in line][0]
                if 'x' in video_line:
                    resolution_part = video_line.split()
                    for part in resolution_part:
                        if 'x' in part and part.replace('x', '').replace(',', '').isdigit():
                            width, height = part.rstrip(',').split('x')
                            info['width'] = width
                            info['height'] = height
                            break
            
            return info if info else None
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self.logger.error(f"動画情報の取得に失敗: {e}")
            return None

    def extract_frames(
        self,
        video_path: Path,
        output_dir: Path,
        *,
        config: VideoConfig | None = None,
    ) -> ProcessingResult:
        """動画からフレームを抽出。

        Parameters
        ----------
        video_path : Path
            入力動画ファイルのパス
        output_dir : Path
            出力ディレクトリ
        config : VideoConfig | None
            動画処理設定

        Returns
        -------
        ProcessingResult
            処理結果
        """
        start_time = time.perf_counter()
        
        if not video_path.exists():
            return create_processing_result(
                status="error",
                input_path=video_path,
                error_message=f"動画ファイルが存在しません: {video_path}",
            )
        
        if not self.check_ffmpeg():
            return create_processing_result(
                status="error",
                input_path=video_path,
                error_message="FFmpegが見つかりません。インストールしてください。",
            )
        
        # 設定のデフォルト値
        frame_interval = config.get("frame_interval", 30) if config else 30
        start_sec = config.get("start_time", 0.0) if config else 0.0
        end_sec = config.get("end_time") if config else None
        
        try:
            # 出力ディレクトリを作成
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 出力ファイル名のパターン
            output_pattern = output_dir / f"{video_path.stem}_frame_%04d.png"
            
            # FFmpegコマンドを構築
            cmd = [
                self.ffmpeg_path,
                "-i", str(video_path),
                "-vf", f"select='not(mod(n,{frame_interval}))'",
                "-vsync", "vfr",
                "-start_number", "1",
            ]
            
            # 開始時間を指定
            if start_sec > 0:
                cmd.extend(["-ss", str(start_sec)])
            
            # 終了時間を指定
            if end_sec is not None:
                cmd.extend(["-t", str(end_sec - start_sec)])
            
            cmd.append(str(output_pattern))
            
            self.logger.info(f"フレーム抽出開始: {video_path.name}")
            self.logger.debug(f"FFmpegコマンド: {' '.join(cmd)}")
            
            # FFmpegを実行
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分でタイムアウト
            )
            
            if result.returncode != 0:
                error_msg = f"FFmpegエラー: {result.stderr}"
                self.logger.error(error_msg)
                return create_processing_result(
                    status="error",
                    input_path=video_path,
                    error_message=error_msg,
                    processing_time=time.perf_counter() - start_time,
                )
            
            # 抽出されたフレーム数を確認
            extracted_frames = list(output_dir.glob(f"{video_path.stem}_frame_*.png"))
            
            if not extracted_frames:
                return create_processing_result(
                    status="error",
                    input_path=video_path,
                    error_message="フレームが抽出されませんでした",
                    processing_time=time.perf_counter() - start_time,
                )
            
            self.logger.info(f"フレーム抽出完了: {len(extracted_frames)}枚")
            
            return create_processing_result(
                status="success",
                input_path=video_path,
                output_path=output_dir,
                processing_time=time.perf_counter() - start_time,
            )
            
        except subprocess.TimeoutExpired:
            return create_processing_result(
                status="error",
                input_path=video_path,
                error_message="処理がタイムアウトしました",
                processing_time=time.perf_counter() - start_time,
            )
        except Exception as e:
            return create_processing_result(
                status="error",
                input_path=video_path,
                error_message=f"予期しないエラー: {e}",
                processing_time=time.perf_counter() - start_time,
            )

    def extract_frames_batch(
        self,
        video_paths: list[Path],
        output_base_dir: Path,
        *,
        config: VideoConfig | None = None,
    ) -> Iterator[ProcessingResult]:
        """複数の動画からフレームを一括抽出。

        Parameters
        ----------
        video_paths : list[Path]
            入力動画ファイルのパスリスト
        output_base_dir : Path
            出力ベースディレクトリ
        config : VideoConfig | None
            動画処理設定

        Yields
        ------
        ProcessingResult
            各動画の処理結果
        """
        for video_path in video_paths:
            # 動画ごとに個別の出力ディレクトリを作成
            output_dir = output_base_dir / video_path.stem
            
            yield self.extract_frames(video_path, output_dir, config=config)

    def create_summary_report(
        self,
        results: list[ProcessingResult],
        output_path: Path,
    ) -> None:
        """処理結果のサマリーレポートを作成。

        Parameters
        ----------
        results : list[ProcessingResult]
            処理結果のリスト
        output_path : Path
            レポート出力パス
        """
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count
        total_time = sum(r["processing_time"] for r in results)
        
        report_lines = [
            "# フレーム抽出レポート",
            "",
            f"## 概要",
            f"- 処理ファイル数: {len(results)}",
            f"- 成功: {success_count}",
            f"- エラー: {error_count}",
            f"- 総処理時間: {total_time:.2f}秒",
            "",
            "## 詳細結果",
        ]
        
        for result in results:
            status_emoji = "✅" if result["status"] == "success" else "❌"
            report_lines.append(
                f"- {status_emoji} {result['input_path'].name} "
                f"({result['processing_time']:.2f}s)"
            )
            
            if result["error_message"]:
                report_lines.append(f"  - エラー: {result['error_message']}")
        
        output_path.write_text("\n".join(report_lines), encoding="utf-8")
        self.logger.info(f"レポートを作成: {output_path}")


def main() -> None:
    """メイン関数（テスト用）."""
    import sys
    from image_processor.core.common import setup_logging
    
    setup_logging()
    
    if len(sys.argv) < 2:
        print("使用法: python frame_extractor.py <動画ファイル>")
        sys.exit(1)
    
    video_path = Path(sys.argv[1])
    output_dir = Path("data/output") / "frames"
    
    extractor = FrameExtractor()
    
    # 動画情報を表示
    info = extractor.get_video_info(video_path)
    if info:
        print("動画情報:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # フレーム抽出
    result = extractor.extract_frames(video_path, output_dir)
    
    if result["status"] == "success":
        print(f"✅ フレーム抽出成功: {result['processing_time']:.2f}秒")
        print(f"出力先: {result['output_path']}")
    else:
        print(f"❌ エラー: {result['error_message']}")


if __name__ == "__main__":
    main()