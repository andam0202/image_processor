"""Utils機能のテストモジュール."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch

from image_processor.utils.helpers import (
    chunk_list,
    safe_json_load,
    safe_json_save,
    merge_dicts,
    flatten_list,
    timer,
    status_to_bool,
    ensure_extension,
    create_unique_filename,
)
from image_processor.types import ProcessorStatus


class TestChunkList:
    """chunk_list関数のテストクラス."""

    def test_正常系_通常分割(self) -> None:
        """リストが正しくチャンクに分割されることを確認。"""
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        chunks = list(chunk_list(items, 3))
        
        expected = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]
        assert chunks == expected

    def test_正常系_サイズが等しい場合(self) -> None:
        """リストサイズとチャンクサイズが等しい場合の動作を確認。"""
        items = [1, 2, 3]
        chunks = list(chunk_list(items, 3))
        
        assert chunks == [[1, 2, 3]]

    def test_正常系_チャンクサイズが大きい場合(self) -> None:
        """チャンクサイズがリストより大きい場合の動作を確認。"""
        items = [1, 2, 3]
        chunks = list(chunk_list(items, 5))
        
        assert chunks == [[1, 2, 3]]

    def test_エッジケース_空リスト(self) -> None:
        """空のリストで空の結果が返されることを確認。"""
        items: list[int] = []
        chunks = list(chunk_list(items, 3))
        
        assert chunks == []

    def test_異常系_不正なチャンクサイズ(self) -> None:
        """チャンクサイズが0以下の場合、ValueErrorが発生することを確認。"""
        items = [1, 2, 3]
        
        with pytest.raises(ValueError, match="チャンクサイズは1以上である必要があります"):
            list(chunk_list(items, 0))
        
        with pytest.raises(ValueError, match="チャンクサイズは1以上である必要があります"):
            list(chunk_list(items, -1))


class TestSafeJsonLoad:
    """safe_json_load関数のテストクラス."""

    def test_正常系_有効なJSONファイル(self, temp_dir: Path) -> None:
        """有効なJSONファイルが正しく読み込まれることを確認。"""
        json_file = temp_dir / "test.json"
        test_data = {"key": "value", "number": 42}
        
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(test_data, f)
        
        result = safe_json_load(json_file)
        
        assert result == test_data

    def test_異常系_存在しないファイル(self, temp_dir: Path) -> None:
        """存在しないファイルでNoneが返されることを確認。"""
        non_existent_file = temp_dir / "non_existent.json"
        
        result = safe_json_load(non_existent_file)
        
        assert result is None

    def test_異常系_不正なJSONファイル(self, temp_dir: Path) -> None:
        """不正なJSONファイルでNoneが返されることを確認。"""
        invalid_json_file = temp_dir / "invalid.json"
        invalid_json_file.write_text("{ invalid json }")
        
        result = safe_json_load(invalid_json_file)
        
        assert result is None


class TestSafeJsonSave:
    """safe_json_save関数のテストクラス."""

    def test_正常系_JSON保存成功(self, temp_dir: Path) -> None:
        """JSONデータが正しく保存されることを確認。"""
        json_file = temp_dir / "output.json"
        test_data = {"key": "value", "number": 42}
        
        result = safe_json_save(test_data, json_file)
        
        assert result is True
        assert json_file.exists()
        
        # 保存されたデータを確認
        with json_file.open("r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    def test_正常系_ディレクトリ自動作成(self, temp_dir: Path) -> None:
        """存在しないディレクトリが自動作成されることを確認。"""
        nested_file = temp_dir / "nested" / "dir" / "output.json"
        test_data = {"test": "data"}
        
        result = safe_json_save(test_data, nested_file)
        
        assert result is True
        assert nested_file.exists()
        assert nested_file.parent.exists()


class TestMergeDicts:
    """merge_dicts関数のテストクラス."""

    def test_正常系_辞書マージ(self) -> None:
        """複数の辞書が正しくマージされることを確認。"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        dict3 = {"b": 5, "e": 6}  # "b"は上書きされる
        
        result = merge_dicts(dict1, dict2, dict3)
        
        expected = {"a": 1, "b": 5, "c": 3, "d": 4, "e": 6}
        assert result == expected

    def test_エッジケース_空辞書(self) -> None:
        """空の辞書がマージされることを確認。"""
        dict1 = {"a": 1}
        dict2: dict[str, int] = {}
        dict3 = {"b": 2}
        
        result = merge_dicts(dict1, dict2, dict3)
        
        expected = {"a": 1, "b": 2}
        assert result == expected

    def test_エッジケース_引数なし(self) -> None:
        """引数なしで空の辞書が返されることを確認。"""
        result = merge_dicts()
        
        assert result == {}


class TestFlattenList:
    """flatten_list関数のテストクラス."""

    def test_正常系_ネストリスト平坦化(self) -> None:
        """ネストしたリストが正しく平坦化されることを確認。"""
        nested_list = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
        
        result = flatten_list(nested_list)
        
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert result == expected

    def test_エッジケース_空のサブリスト(self) -> None:
        """空のサブリストを含む場合の動作を確認。"""
        nested_list = [[1, 2], [], [3, 4]]
        
        result = flatten_list(nested_list)
        
        expected = [1, 2, 3, 4]
        assert result == expected

    def test_エッジケース_全て空のリスト(self) -> None:
        """全て空のサブリストの場合の動作を確認。"""
        nested_list: list[list[int]] = [[], [], []]
        
        result = flatten_list(nested_list)
        
        assert result == []


class TestTimer:
    """timer関数のテストクラス."""

    def test_正常系_時間測定(self) -> None:
        """時間測定が正しく動作することを確認。"""
        import time
        
        with timer() as get_elapsed:
            time.sleep(0.01)  # 10ms待機
            elapsed = get_elapsed()
        
        # 10ms以上経過していることを確認（多少の誤差を許容）
        assert elapsed >= 0.01
        assert elapsed < 0.1  # 100ms未満であることを確認


class TestStatusToBool:
    """status_to_bool関数のテストクラス."""

    def test_正常系_success(self) -> None:
        """successステータスでTrueが返されることを確認。"""
        status: ProcessorStatus = "success"
        assert status_to_bool(status) is True

    def test_正常系_error(self) -> None:
        """errorステータスでFalseが返されることを確認。"""
        status: ProcessorStatus = "error"
        assert status_to_bool(status) is False

    def test_正常系_pending(self) -> None:
        """pendingステータスでFalseが返されることを確認。"""
        status: ProcessorStatus = "pending"
        assert status_to_bool(status) is False


class TestEnsureExtension:
    """ensure_extension関数のテストクラス."""

    def test_正常系_拡張子追加(self, temp_dir: Path) -> None:
        """拡張子が正しく追加されることを確認。"""
        file_path = temp_dir / "test"
        
        result = ensure_extension(file_path, ".txt")
        
        assert result == temp_dir / "test.txt"

    def test_正常系_既存拡張子保持(self, temp_dir: Path) -> None:
        """既に正しい拡張子がある場合は変更されないことを確認。"""
        file_path = temp_dir / "test.txt"
        
        result = ensure_extension(file_path, ".txt")
        
        assert result == file_path

    def test_正常系_拡張子変更(self, temp_dir: Path) -> None:
        """異なる拡張子の場合は変更されることを確認。"""
        file_path = temp_dir / "test.jpg"
        
        result = ensure_extension(file_path, ".png")
        
        assert result == temp_dir / "test.png"

    def test_正常系_ドットなし拡張子(self, temp_dir: Path) -> None:
        """ドットなしの拡張子でも正しく処理されることを確認。"""
        file_path = temp_dir / "test"
        
        result = ensure_extension(file_path, "txt")
        
        assert result == temp_dir / "test.txt"


class TestCreateUniqueFilename:
    """create_unique_filename関数のテストクラス."""

    def test_正常系_ファイル存在しない場合(self, temp_dir: Path) -> None:
        """ファイルが存在しない場合は元のパスが返されることを確認。"""
        file_path = temp_dir / "test.txt"
        
        result = create_unique_filename(file_path)
        
        assert result == file_path

    def test_正常系_重複ファイル存在(self, temp_dir: Path) -> None:
        """重複ファイルが存在する場合は一意な名前が生成されることを確認。"""
        file_path = temp_dir / "test.txt"
        file_path.touch()  # ファイルを作成
        
        result = create_unique_filename(file_path)
        
        assert result == temp_dir / "test_1.txt"
        assert not result.exists()

    def test_正常系_複数重複ファイル存在(self, temp_dir: Path) -> None:
        """複数の重複ファイルが存在する場合の動作を確認。"""
        file_path = temp_dir / "test.txt"
        file_path.touch()
        (temp_dir / "test_1.txt").touch()
        (temp_dir / "test_2.txt").touch()
        
        result = create_unique_filename(file_path)
        
        assert result == temp_dir / "test_3.txt"
        assert not result.exists()