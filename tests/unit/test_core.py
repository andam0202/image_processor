"""Core機能のテストモジュール."""

import pytest
import logging
from pathlib import Path
from unittest.mock import patch

from image_processor.core.common import (
    setup_logging,
    create_directory,
    get_files_by_extension,
    validate_directories,
    remove_file_safely,
    create_processing_result,
    format_file_size,
)
from image_processor.types import ProcessorStatus


class TestSetupLogging:
    """setup_logging関数のテストクラス."""

    def test_正常系_コンソールのみ(self) -> None:
        """コンソール出力のみの設定が正しく動作することを確認。"""
        setup_logging()
        
        logger = logging.getLogger("test")
        assert logger.level <= logging.INFO

    def test_正常系_ファイル出力あり(self, temp_dir: Path) -> None:
        """ファイル出力ありの設定が正しく動作することを確認。"""
        log_file = temp_dir / "test.log"
        setup_logging(log_file)
        
        logger = logging.getLogger("test")
        logger.info("テストメッセージ")
        
        assert log_file.exists()
        assert "テストメッセージ" in log_file.read_text(encoding="utf-8")


class TestCreateDirectory:
    """create_directory関数のテストクラス."""

    def test_正常系_新規ディレクトリ作成(self, temp_dir: Path) -> None:
        """新しいディレクトリが正しく作成されることを確認。"""
        new_dir = temp_dir / "new_directory"
        assert not new_dir.exists()
        
        create_directory(new_dir)
        
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_正常系_既存ディレクトリ(self, temp_dir: Path) -> None:
        """既存ディレクトリに対してエラーが発生しないことを確認。"""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()
        
        # エラーが発生しないことを確認
        create_directory(existing_dir)
        assert existing_dir.exists()

    def test_正常系_階層ディレクトリ作成(self, temp_dir: Path) -> None:
        """階層化されたディレクトリが正しく作成されることを確認。"""
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        
        create_directory(nested_dir)
        
        assert nested_dir.exists()
        assert nested_dir.is_dir()


class TestGetFilesByExtension:
    """get_files_by_extension関数のテストクラス."""

    def test_正常系_拡張子フィルタリング(self, sample_image_dir: Path) -> None:
        """指定拡張子のファイルが正しく取得されることを確認。"""
        files = get_files_by_extension(sample_image_dir, [".jpg", ".png"])
        
        assert len(files) == 2
        assert all(f.suffix in [".jpg", ".png"] for f in files)

    def test_正常系_大文字小文字混在(self, temp_dir: Path) -> None:
        """大文字小文字の拡張子が正しく取得されることを確認。"""
        test_dir = temp_dir / "mixed_case"
        test_dir.mkdir()
        
        # 大文字小文字の混在ファイルを作成
        (test_dir / "file1.jpg").touch()
        (test_dir / "file2.JPG").touch()
        (test_dir / "file3.png").touch()
        
        files = get_files_by_extension(test_dir, [".jpg"])
        
        assert len(files) == 2
        assert all(f.suffix.lower() == ".jpg" for f in files)

    def test_正常系_再帰検索(self, temp_dir: Path) -> None:
        """再帰検索が正しく動作することを確認。"""
        # ネストした構造を作成
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()
        
        (temp_dir / "root.jpg").touch()
        (sub_dir / "nested.jpg").touch()
        
        # 非再帰検索
        files_non_recursive = get_files_by_extension(temp_dir, [".jpg"], recursive=False)
        assert len(files_non_recursive) == 1
        
        # 再帰検索
        files_recursive = get_files_by_extension(temp_dir, [".jpg"], recursive=True)
        assert len(files_recursive) == 2

    def test_異常系_存在しないディレクトリ(self, temp_dir: Path) -> None:
        """存在しないディレクトリに対してFileNotFoundErrorが発生することを確認。"""
        non_existent_dir = temp_dir / "non_existent"
        
        with pytest.raises(FileNotFoundError):
            get_files_by_extension(non_existent_dir, [".jpg"])

    def test_エッジケース_空ディレクトリ(self, temp_dir: Path) -> None:
        """空のディレクトリで空のリストが返されることを確認。"""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        files = get_files_by_extension(empty_dir, [".jpg"])
        
        assert files == []


class TestValidateDirectories:
    """validate_directories関数のテストクラス."""

    def test_正常系_有効なディレクトリ(self, temp_dir: Path) -> None:
        """有効な入力・出力ディレクトリでTrueが返されることを確認。"""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        
        result = validate_directories(input_dir, output_dir)
        
        assert result is True
        assert output_dir.exists()

    def test_異常系_存在しない入力ディレクトリ(self, temp_dir: Path) -> None:
        """存在しない入力ディレクトリでFalseが返されることを確認。"""
        input_dir = temp_dir / "non_existent"
        output_dir = temp_dir / "output"
        
        result = validate_directories(input_dir, output_dir)
        
        assert result is False


class TestRemoveFileSafely:
    """remove_file_safely関数のテストクラス."""

    def test_正常系_ファイル削除成功(self, temp_dir: Path) -> None:
        """ファイルの削除が正常に行われることを確認。"""
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("test content")
        
        result = remove_file_safely(test_file)
        
        assert result is True
        assert not test_file.exists()

    def test_異常系_存在しないファイル(self, temp_dir: Path) -> None:
        """存在しないファイルの削除でFalseが返されることを確認。"""
        non_existent_file = temp_dir / "non_existent.txt"
        
        result = remove_file_safely(non_existent_file)
        
        assert result is False


class TestCreateProcessingResult:
    """create_processing_result関数のテストクラス."""

    def test_正常系_成功結果(self, temp_dir: Path) -> None:
        """成功した処理結果が正しく作成されることを確認。"""
        input_path = temp_dir / "input.jpg"
        output_path = temp_dir / "output.png"
        
        result = create_processing_result(
            status="success",
            input_path=input_path,
            output_path=output_path,
            processing_time=1.5,
        )
        
        assert result["status"] == "success"
        assert result["input_path"] == input_path
        assert result["output_path"] == output_path
        assert result["error_message"] is None
        assert result["processing_time"] == 1.5

    def test_正常系_エラー結果(self, temp_dir: Path) -> None:
        """エラーが発生した処理結果が正しく作成されることを確認。"""
        input_path = temp_dir / "input.jpg"
        error_msg = "処理中にエラーが発生しました"
        
        result = create_processing_result(
            status="error",
            input_path=input_path,
            error_message=error_msg,
            processing_time=0.5,
        )
        
        assert result["status"] == "error"
        assert result["input_path"] == input_path
        assert result["output_path"] is None
        assert result["error_message"] == error_msg
        assert result["processing_time"] == 0.5


class TestFormatFileSize:
    """format_file_size関数のテストクラス."""

    def test_正常系_バイト単位(self) -> None:
        """バイト単位の表示が正しいことを確認。"""
        assert format_file_size(0) == "0B"
        assert format_file_size(512) == "512.0B"

    def test_正常系_キロバイト単位(self) -> None:
        """キロバイト単位の表示が正しいことを確認。"""
        assert format_file_size(1024) == "1.0KB"
        assert format_file_size(1536) == "1.5KB"

    def test_正常系_メガバイト単位(self) -> None:
        """メガバイト単位の表示が正しいことを確認。"""
        assert format_file_size(1024 * 1024) == "1.0MB"
        assert format_file_size(1024 * 1024 * 2.5) == "2.5MB"

    def test_正常系_ギガバイト単位(self) -> None:
        """ギガバイト単位の表示が正しいことを確認。"""
        assert format_file_size(1024 * 1024 * 1024) == "1.0GB"