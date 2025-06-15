"""Utility helper functions."""

from pathlib import Path
from typing import Any
import json
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from image_processor.types import ProcessorStatus


def chunk_list[T](items: list[T], chunk_size: int) -> Iterator[list[T]]:
    """リストを指定サイズのチャンクに分割。

    Parameters
    ----------
    items : list[T]
        分割対象のリスト
    chunk_size : int
        チャンクサイズ

    Yields
    ------
    list[T]
        指定サイズのチャンク

    Raises
    ------
    ValueError
        chunk_sizeが1未満の場合
    """
    if chunk_size < 1:
        raise ValueError("チャンクサイズは1以上である必要があります")
    
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def safe_json_load(file_path: Path) -> dict[str, Any] | None:
    """JSONファイルを安全に読み込み。

    Parameters
    ----------
    file_path : Path
        JSONファイルのパス

    Returns
    -------
    dict[str, Any] | None
        読み込んだデータ。失敗時はNone
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def safe_json_save(data: dict[str, Any], file_path: Path) -> bool:
    """データをJSONファイルに安全に保存。

    Parameters
    ----------
    data : dict[str, Any]
        保存するデータ
    file_path : Path
        保存先ファイルのパス

    Returns
    -------
    bool
        保存に成功した場合True
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """複数の辞書をマージ（後の辞書が優先）。

    Parameters
    ----------
    *dicts : dict[str, Any]
        マージする辞書群

    Returns
    -------
    dict[str, Any]
        マージされた辞書
    """
    result: dict[str, Any] = {}
    for d in dicts:
        result.update(d)
    return result


def flatten_list[T](nested_list: list[list[T]]) -> list[T]:
    """ネストしたリストを平坦化。

    Parameters
    ----------
    nested_list : list[list[T]]
        ネストしたリスト

    Returns
    -------
    list[T]
        平坦化されたリスト
    """
    return [item for sublist in nested_list for item in sublist]


@contextmanager
def timer() -> Iterator[Callable[[], float]]:
    """実行時間を測定するコンテキストマネージャー。

    Yields
    ------
    Callable[[], float]
        経過時間を返す関数
    """
    start_time = time.perf_counter()
    
    def get_elapsed() -> float:
        return time.perf_counter() - start_time
    
    yield get_elapsed


def status_to_bool(status: ProcessorStatus) -> bool:
    """ProcessorStatusをbooleanに変換。

    Parameters
    ----------
    status : ProcessorStatus
        変換するステータス

    Returns
    -------
    bool
        successの場合True、それ以外False
    """
    return status == "success"


def ensure_extension(file_path: Path, extension: str) -> Path:
    """ファイルパスに拡張子を確実に付与。

    Parameters
    ----------
    file_path : Path
        対象ファイルパス
    extension : str
        拡張子（ドット付き）

    Returns
    -------
    Path
        拡張子が付与されたパス
    """
    if not extension.startswith("."):
        extension = f".{extension}"
    
    if file_path.suffix.lower() != extension.lower():
        return file_path.with_suffix(extension)
    
    return file_path


def create_unique_filename(file_path: Path) -> Path:
    """ファイル名が重複しない一意なパスを生成。

    Parameters
    ----------
    file_path : Path
        元のファイルパス

    Returns
    -------
    Path
        一意なファイルパス
    """
    if not file_path.exists():
        return file_path
    
    counter = 1
    stem = file_path.stem
    suffix = file_path.suffix
    parent = file_path.parent
    
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1