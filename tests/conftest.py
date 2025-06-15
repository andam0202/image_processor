"""pytest設定ファイル."""

import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Iterator


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """一時ディレクトリを提供するフィクスチャ。
    
    Yields
    ------
    Path
        一時ディレクトリのパス
    """
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_image_dir(temp_dir: Path) -> Path:
    """サンプル画像ディレクトリを提供するフィクスチャ。
    
    Parameters
    ----------
    temp_dir : Path
        一時ディレクトリ
        
    Returns
    -------
    Path
        サンプル画像が配置されたディレクトリ
    """
    image_dir = temp_dir / "images"
    image_dir.mkdir()
    
    # ダミー画像ファイルを作成
    for i, ext in enumerate([".jpg", ".png", ".webp"], 1):
        dummy_file = image_dir / f"sample_{i}{ext}"
        dummy_file.write_text(f"dummy image content {i}")
    
    return image_dir


@pytest.fixture
def output_dir(temp_dir: Path) -> Path:
    """出力ディレクトリを提供するフィクスチャ。
    
    Parameters
    ----------
    temp_dir : Path
        一時ディレクトリ
        
    Returns
    -------
    Path
        出力用ディレクトリ
    """
    output_path = temp_dir / "output"
    output_path.mkdir()
    return output_path


@pytest.fixture(autouse=True)
def reset_logging() -> Iterator[None]:
    """テスト毎にログ設定をリセット。"""
    import logging
    
    # テスト前の状態を保存
    original_level = logging.root.level
    original_handlers = logging.root.handlers[:]
    
    yield
    
    # テスト後に状態を復元
    logging.root.level = original_level
    logging.root.handlers = original_handlers