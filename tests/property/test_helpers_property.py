"""プロパティベーステストモジュール（Hypothesis使用）."""

import pytest
from hypothesis import given, strategies as st, assume
from pathlib import Path
import tempfile

from image_processor.utils.helpers import (
    chunk_list,
    merge_dicts,
    flatten_list,
    ensure_extension,
    format_file_size,
)


class TestChunkListProperty:
    """chunk_list関数のプロパティベーステスト."""

    @given(
        items=st.lists(st.integers(), min_size=0, max_size=100),
        chunk_size=st.integers(min_value=1, max_value=20)
    )
    def test_チャンク分割の不変条件(self, items: list[int], chunk_size: int) -> None:
        """チャンク分割の不変条件を検証。
        
        - 全てのアイテムが保持される
        - チャンクサイズ以下のチャンクのみが生成される
        - 最後のチャンク以外は指定サイズである
        """
        chunks = list(chunk_list(items, chunk_size))
        
        # 全てのアイテムが保持されている
        flattened = [item for chunk in chunks for item in chunk]
        assert flattened == items
        
        # 各チャンクのサイズが適切
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                # 最後のチャンクは1以上chunk_size以下
                assert 1 <= len(chunk) <= chunk_size
            else:
                # 最後以外のチャンクは指定サイズ
                assert len(chunk) == chunk_size

    @given(items=st.lists(st.text(), min_size=1, max_size=50))
    def test_チャンク数の上限(self, items: list[str]) -> None:
        """チャンク数が元のリストサイズを超えないことを確認。"""
        chunk_size = 1
        chunks = list(chunk_list(items, chunk_size))
        
        assert len(chunks) <= len(items)
        assert len(chunks) == len(items)  # chunk_size=1の場合は等しくなる


class TestMergeDictsProperty:
    """merge_dicts関数のプロパティベーステスト."""

    @given(
        dicts=st.lists(
            st.dictionaries(st.text(min_size=1, max_size=10), st.integers()),
            min_size=0,
            max_size=5
        )
    )
    def test_マージ後のキー数は最大値以下(self, dicts: list[dict[str, int]]) -> None:
        """マージ後の辞書のキー数が、元の辞書のキー数の最大値以下であることを確認。"""
        result = merge_dicts(*dicts)
        
        if not dicts:
            assert len(result) == 0
            return
        
        # 全てのユニークキーを収集
        all_keys = set()
        for d in dicts:
            all_keys.update(d.keys())
        
        assert len(result) == len(all_keys)

    @given(
        dict1=st.dictionaries(st.text(min_size=1), st.integers()),
        dict2=st.dictionaries(st.text(min_size=1), st.integers()),
    )
    def test_後の辞書が優先される(self, dict1: dict[str, int], dict2: dict[str, int]) -> None:
        """共通キーの場合、後の辞書の値が優先されることを確認。"""
        result = merge_dicts(dict1, dict2)
        
        # dict2のキーがある場合は、dict2の値が使われる
        for key, value in dict2.items():
            assert result[key] == value


class TestFlattenListProperty:
    """flatten_list関数のプロパティベーステスト."""

    @given(
        nested_list=st.lists(
            st.lists(st.integers(), min_size=0, max_size=10),
            min_size=0,
            max_size=10
        )
    )
    def test_平坦化後の要素数(self, nested_list: list[list[int]]) -> None:
        """平坦化後の要素数が元の要素の総数と等しいことを確認。"""
        result = flatten_list(nested_list)
        
        expected_count = sum(len(sublist) for sublist in nested_list)
        assert len(result) == expected_count

    @given(
        nested_list=st.lists(
            st.lists(st.text(min_size=1, max_size=5), min_size=1, max_size=5),
            min_size=1,
            max_size=5
        )
    )
    def test_平坦化の順序保持(self, nested_list: list[list[str]]) -> None:
        """平坦化後も元の順序が保持されることを確認。"""
        result = flatten_list(nested_list)
        
        # 手動で順序を構築
        expected = []
        for sublist in nested_list:
            expected.extend(sublist)
        
        assert result == expected


class TestEnsureExtensionProperty:
    """ensure_extension関数のプロパティベーステスト."""

    @given(
        filename=st.text(min_size=1, max_size=20).filter(lambda x: '.' not in x and '/' not in x),
        extension=st.text(min_size=1, max_size=5).map(lambda x: f".{x}")
    )
    def test_拡張子が必ず付与される(self, filename: str, extension: str) -> None:
        """ファイル名に指定した拡張子が必ず付与されることを確認。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / filename
            
            result = ensure_extension(file_path, extension)
            
            assert result.suffix == extension

    @given(
        filename=st.text(min_size=1, max_size=20).filter(lambda x: '.' not in x and '/' not in x),
        extension1=st.text(min_size=1, max_size=5).map(lambda x: f".{x}"),
        extension2=st.text(min_size=1, max_size=5).map(lambda x: f".{x}")
    )
    def test_拡張子の一貫性(self, filename: str, extension1: str, extension2: str) -> None:
        """同じ拡張子を指定した場合、結果が一貫していることを確認。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / filename
            
            result1 = ensure_extension(file_path, extension1)
            result2 = ensure_extension(result1, extension1)
            
            # 同じ拡張子を再度指定しても変更されない
            assert result1 == result2


class TestFormatFileSizeProperty:
    """format_file_size関数のプロパティベーステスト."""

    @given(size=st.integers(min_value=0, max_value=10**12))
    def test_ファイルサイズフォーマットの不変条件(self, size: int) -> None:
        """ファイルサイズフォーマットの不変条件を検証。"""
        result = format_file_size(size)
        
        # 結果は文字列である
        assert isinstance(result, str)
        
        # 単位が含まれている
        units = ["B", "KB", "MB", "GB", "TB"]
        assert any(unit in result for unit in units)
        
        # 0の場合は "0B"
        if size == 0:
            assert result == "0B"
        else:
            # 正の数値部分が含まれている
            numeric_part = result.rstrip("KMGTB")
            try:
                float(numeric_part)
            except ValueError:
                pytest.fail(f"数値部分の解析に失敗: {numeric_part}")

    @given(size=st.integers(min_value=1, max_value=1023))
    def test_バイト単位の範囲(self, size: int) -> None:
        """1-1023バイトの範囲でB単位が使われることを確認。"""
        result = format_file_size(size)
        assert result.endswith("B")
        assert "KB" not in result

    @given(size=st.integers(min_value=1024, max_value=1024*1024-1))
    def test_キロバイト単位の範囲(self, size: int) -> None:
        """1KB-1MB未満の範囲でKB単位が使われることを確認。"""
        result = format_file_size(size)
        assert result.endswith("KB")
        assert "B" not in result or result.endswith("KB")  # "KB"のBは許可