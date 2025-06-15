"""統合テストモジュール - ワークフロー全体のテスト."""

import pytest
from pathlib import Path
import time

from image_processor.core.common import (
    setup_logging,
    get_files_by_extension, 
    validate_directories,
    create_processing_result,
)
from image_processor.utils.helpers import timer, chunk_list
from image_processor.types import ProcessorStatus


class TestImageProcessingWorkflow:
    """画像処理ワークフロー全体の統合テスト."""

    def test_統合_基本ワークフロー(self, temp_dir: Path) -> None:
        """基本的な画像処理ワークフローの統合テスト。"""
        # 1. セットアップ
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        log_file = temp_dir / "process.log"
        
        input_dir.mkdir()
        
        # サンプルファイルを作成
        sample_files = ["image1.jpg", "image2.png", "image3.webp"]
        for filename in sample_files:
            (input_dir / filename).write_text(f"dummy content for {filename}")
        
        # 2. ロギング設定
        setup_logging(log_file)
        
        # 3. ディレクトリ検証
        assert validate_directories(input_dir, output_dir)
        assert output_dir.exists()
        
        # 4. ファイル取得
        image_files = get_files_by_extension(input_dir, [".jpg", ".png", ".webp"])
        assert len(image_files) == 3
        
        # 5. バッチ処理シミュレーション
        results = []
        with timer() as get_elapsed:
            for file_path in image_files:
                # 処理シミュレーション（短時間の処理）
                time.sleep(0.001)
                output_path = output_dir / f"processed_{file_path.name}"
                output_path.write_text(f"processed: {file_path.read_text()}")
                
                result = create_processing_result(
                    status="success",
                    input_path=file_path,
                    output_path=output_path,
                    processing_time=0.001
                )
                results.append(result)
        
        # 6. 結果検証
        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)
        assert all(r["output_path"] and r["output_path"].exists() for r in results)
        
        # 処理時間が記録されている
        processing_time = get_elapsed()
        assert processing_time > 0
        
        # ログファイルが作成されている
        assert log_file.exists()

    def test_統合_大量ファイル処理(self, temp_dir: Path) -> None:
        """大量ファイルのバッチ処理統合テスト。"""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        
        # 多数のファイルを作成
        file_count = 50
        for i in range(file_count):
            (input_dir / f"file_{i:03d}.jpg").write_text(f"content {i}")
        
        # ディレクトリ検証
        assert validate_directories(input_dir, output_dir)
        
        # ファイル取得
        files = get_files_by_extension(input_dir, [".jpg"])
        assert len(files) == file_count
        
        # チャンク処理
        chunk_size = 10
        chunks = list(chunk_list(files, chunk_size))
        expected_chunks = (file_count + chunk_size - 1) // chunk_size
        assert len(chunks) == expected_chunks
        
        # 各チャンクを処理
        all_results = []
        for chunk in chunks:
            chunk_results = []
            for file_path in chunk:
                output_path = output_dir / file_path.name
                output_path.write_text(f"processed: {file_path.read_text()}")
                
                result = create_processing_result(
                    status="success",
                    input_path=file_path,
                    output_path=output_path,
                )
                chunk_results.append(result)
            
            all_results.extend(chunk_results)
        
        # 結果検証
        assert len(all_results) == file_count
        assert all(r["status"] == "success" for r in all_results)
        
        # 出力ファイルが正しく作成されている
        output_files = list(output_dir.glob("*.jpg"))
        assert len(output_files) == file_count

    def test_統合_エラーハンドリング(self, temp_dir: Path) -> None:
        """エラーハンドリングの統合テスト。"""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        
        # 正常ファイルと問題のあるファイルを混在
        files_data = [
            ("normal1.jpg", "normal content 1", True),
            ("normal2.png", "normal content 2", True),
            ("corrupted.jpg", "", False),  # 空ファイル（エラーシミュレーション）
            ("normal3.webp", "normal content 3", True),
        ]
        
        for filename, content, _ in files_data:
            (input_dir / filename).write_text(content)
        
        # ディレクトリ検証
        assert validate_directories(input_dir, output_dir)
        
        # ファイル取得と処理
        files = get_files_by_extension(input_dir, [".jpg", ".png", ".webp"])
        results = []
        
        for file_path in files:
            content = file_path.read_text()
            
            # 空ファイルはエラーとして処理
            if not content.strip():
                result = create_processing_result(
                    status="error",
                    input_path=file_path,
                    error_message="ファイルが空です",
                )
            else:
                output_path = output_dir / file_path.name
                output_path.write_text(f"processed: {content}")
                result = create_processing_result(
                    status="success",
                    input_path=file_path,
                    output_path=output_path,
                )
            
            results.append(result)
        
        # 結果検証
        assert len(results) == 4
        
        success_results = [r for r in results if r["status"] == "success"]
        error_results = [r for r in results if r["status"] == "error"]
        
        assert len(success_results) == 3
        assert len(error_results) == 1
        
        # エラー結果の検証
        error_result = error_results[0]
        assert error_result["input_path"].name == "corrupted.jpg"
        assert error_result["error_message"] == "ファイルが空です"
        assert error_result["output_path"] is None
        
        # 成功した処理の出力ファイルが存在
        for result in success_results:
            assert result["output_path"] is not None
            assert result["output_path"].exists()

    def test_統合_再帰的ファイル検索(self, temp_dir: Path) -> None:
        """再帰的ファイル検索の統合テスト。"""
        # ネストした構造を作成
        base_dir = temp_dir / "nested_structure"
        base_dir.mkdir()
        
        # 複数レベルのディレクトリ構造
        dirs = [
            base_dir,
            base_dir / "level1",
            base_dir / "level1" / "level2",
            base_dir / "another_level1",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True)
        
        # 各レベルにファイルを配置
        files_info = [
            (base_dir / "root.jpg", "root image"),
            (base_dir / "level1" / "level1.png", "level1 image"),
            (base_dir / "level1" / "level2" / "level2.webp", "level2 image"),
            (base_dir / "another_level1" / "another.jpg", "another image"),
        ]
        
        for file_path, content in files_info:
            file_path.write_text(content)
        
        # 非再帰検索
        files_non_recursive = get_files_by_extension(
            base_dir, [".jpg", ".png", ".webp"], recursive=False
        )
        assert len(files_non_recursive) == 1  # root.jpgのみ
        
        # 再帰検索
        files_recursive = get_files_by_extension(
            base_dir, [".jpg", ".png", ".webp"], recursive=True
        )
        assert len(files_recursive) == 4  # 全てのファイル
        
        # 出力ディレクトリ
        output_dir = temp_dir / "output"
        validate_directories(base_dir, output_dir)
        
        # 再帰検索で見つかったファイルを処理
        results = []
        for file_path in files_recursive:
            output_path = output_dir / file_path.name
            output_path.write_text(f"processed: {file_path.read_text()}")
            
            result = create_processing_result(
                status="success",
                input_path=file_path,
                output_path=output_path,
            )
            results.append(result)
        
        # 結果検証
        assert len(results) == 4
        assert all(r["status"] == "success" for r in results)
        
        # 出力ファイル名の確認
        output_names = {r["output_path"].name for r in results}
        expected_names = {"root.jpg", "level1.png", "level2.webp", "another.jpg"}
        assert output_names == expected_names