"""Image Processor 型定義モジュール."""

from typing import TypedDict, Literal
from pathlib import Path

# PEP 695型構文の使用
type ProcessorStatus = Literal["success", "error", "pending"]
type ImageFormat = Literal["png", "jpg", "jpeg", "webp", "dds", "bmp", "tiff"]
type ProcessingMode = Literal["single", "batch", "recursive"]
type BackgroundModel = Literal["u2net", "u2netp", "silueta", "isnet-general-use"]

class ConversionConfig(TypedDict, total=False):
    """画像変換設定の型定義."""
    format: ImageFormat
    quality: int
    remove_background: bool
    background_model: BackgroundModel
    output_dir: Path
    recursive: bool
    preserve_metadata: bool

class ProcessingResult(TypedDict):
    """処理結果の型定義."""
    status: ProcessorStatus
    input_path: Path
    output_path: Path | None
    error_message: str | None
    processing_time: float

class VideoConfig(TypedDict, total=False):
    """動画処理設定の型定義."""
    fps: int
    start_time: float
    end_time: float
    output_format: Literal["mp4", "avi", "mov", "webm"]
    frame_interval: int
    extract_frames: bool