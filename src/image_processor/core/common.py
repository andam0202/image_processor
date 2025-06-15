"""共通処理ライブラリ."""

import os
import argparse
import logging
from pathlib import Path
from typing import Any
from collections.abc import Sequence

from image_processor.types import ProcessorStatus, ProcessingResult


def setup_logging(log_file: Path | None = None) -> None:
    """ログ設定をセットアップ。

    Parameters
    ----------
    log_file : Path | None
        ログファイルのパス。Noneの場合はコンソールのみに出力
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers,
        force=True,
    )


def create_directory(path: Path) -> None:
    """ディレクトリを作成（存在しない場合）。

    Parameters
    ----------
    path : Path
        作成するディレクトリのパス
    """
    path.mkdir(parents=True, exist_ok=True)


def get_files_by_extension(
    directory: Path, 
    extensions: Sequence[str],
    *,
    recursive: bool = False,
) -> list[Path]:
    """指定された拡張子のファイルを取得。

    Parameters
    ----------
    directory : Path
        検索対象のディレクトリ
    extensions : Sequence[str]
        対象拡張子のリスト（ドット付き、例: ['.jpg', '.png']）
    recursive : bool
        再帰的に検索するか

    Returns
    -------
    list[Path]
        見つかったファイルのパスリスト
    """
    if not directory.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {directory}")
    
    files: list[Path] = []
    glob_pattern = "**/*" if recursive else "*"
    
    for ext in extensions:
        # 小文字と大文字の両方を検索
        files.extend(directory.glob(f"{glob_pattern}{ext}"))
        files.extend(directory.glob(f"{glob_pattern}{ext.upper()}"))
    
    return sorted(set(files))  # 重複を除去してソート


def create_base_parser(description: str) -> argparse.ArgumentParser:
    """基本的なコマンドライン引数パーサーを作成。

    Parameters
    ----------
    description : str
        コマンドの説明文

    Returns
    -------
    argparse.ArgumentParser
        設定済みのパーサー
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-i", 
        "--input",
        type=Path,
        help="入力ディレクトリ",
        default=Path("data/input"),
    )
    parser.add_argument(
        "-o", 
        "--output",
        type=Path,
        help="出力ディレクトリ",
        default=Path("data/output"),
    )
    parser.add_argument(
        "-v", 
        "--verbose",
        action="store_true",
        help="詳細な出力を表示",
    )
    parser.add_argument(
        "-r", 
        "--recursive",
        action="store_true",
        help="再帰的にファイルを処理",
    )
    return parser


def validate_directories(input_dir: Path, output_dir: Path) -> bool:
    """入力・出力ディレクトリの検証。

    Parameters
    ----------
    input_dir : Path
        入力ディレクトリのパス
    output_dir : Path
        出力ディレクトリのパス

    Returns
    -------
    bool
        検証が成功した場合True
    """
    if not input_dir.exists():
        logging.error(f"入力ディレクトリが存在しません: {input_dir}")
        return False
    
    try:
        create_directory(output_dir)
        return True
    except OSError as e:
        logging.error(f"出力ディレクトリの作成に失敗: {output_dir} - {e}")
        return False


def remove_file_safely(file_path: Path) -> bool:
    """ファイルを安全に削除。

    Parameters
    ----------
    file_path : Path
        削除するファイルのパス

    Returns
    -------
    bool
        削除が成功した場合True
    """
    try:
        file_path.unlink()
        return True
    except OSError as e:
        logging.error(f"ファイルの削除に失敗: {file_path} - {e}")
        return False


def create_processing_result(
    status: ProcessorStatus,
    input_path: Path,
    output_path: Path | None = None,
    error_message: str | None = None,
    processing_time: float = 0.0,
) -> ProcessingResult:
    """処理結果オブジェクトを作成。

    Parameters
    ----------
    status : ProcessorStatus
        処理ステータス
    input_path : Path
        入力ファイルのパス
    output_path : Path | None
        出力ファイルのパス
    error_message : str | None
        エラーメッセージ
    processing_time : float
        処理時間（秒）

    Returns
    -------
    ProcessingResult
        処理結果オブジェクト
    """
    return ProcessingResult(
        status=status,
        input_path=input_path,
        output_path=output_path,
        error_message=error_message,
        processing_time=processing_time,
    )


def format_file_size(size_bytes: int) -> str:
    """ファイルサイズを人間が読みやすい形式でフォーマット。

    Parameters
    ----------
    size_bytes : int
        バイト数

    Returns
    -------
    str
        フォーマットされたファイルサイズ
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"