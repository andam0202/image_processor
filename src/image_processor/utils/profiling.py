"""Performance measurement and profiling utilities."""

import time
import cProfile
import pstats
from functools import wraps
from typing import Any, TypeVar, ParamSpec
from collections.abc import Callable
from contextlib import contextmanager
from io import StringIO

P = ParamSpec("P")
T = TypeVar("T")


class Timer:
    """高精度タイマークラス."""

    def __init__(self, description: str = "Operation") -> None:
        """タイマーを初期化。

        Parameters
        ----------
        description : str
            タイマーの説明
        """
        self.description = description
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def __enter__(self) -> "Timer":
        """コンテキストマネージャーの開始."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """コンテキストマネージャーの終了."""
        self.end_time = time.perf_counter()
        print(f"{self.description}: {self.elapsed:.4f}s")

    @property
    def elapsed(self) -> float:
        """経過時間を秒で取得."""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.perf_counter() - self.start_time


def timeit(func: Callable[P, T]) -> Callable[P, T]:
    """関数の実行時間を測定するデコレーター。

    Parameters
    ----------
    func : Callable[P, T]
        測定対象の関数

    Returns
    -------
    Callable[P, T]
        ラップされた関数
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__}: {end_time - start_time:.4f}s")
        return result
    
    return wrapper


def profile(func: Callable[P, T]) -> Callable[P, T]:
    """関数をプロファイリングするデコレーター。

    Parameters
    ----------
    func : Callable[P, T]
        プロファイリング対象の関数

    Returns
    -------
    Callable[P, T]
        ラップされた関数
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
            
            # プロファイル結果を出力
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
            ps.print_stats(10)  # 上位10項目を表示
            print(f"\n--- Profile for {func.__name__} ---")
            print(s.getvalue())
        
        return result
    
    return wrapper


@contextmanager
def profile_context(
    sort_by: str = "cumulative", 
    limit: int = 10,
):
    """プロファイリング用コンテキストマネージャー。

    Parameters
    ----------
    sort_by : str
        ソート基準
    limit : int
        表示する項目数

    Yields
    ------
    cProfile.Profile
        プロファイラーオブジェクト
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        yield profiler
    finally:
        profiler.disable()
        
        # プロファイル結果を出力
        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats(sort_by)
        ps.print_stats(limit)
        print("\n--- Profiling Results ---")
        print(s.getvalue())


class PerformanceMonitor:
    """パフォーマンス監視クラス."""

    def __init__(self) -> None:
        """パフォーマンス監視を初期化."""
        self.measurements: dict[str, list[float]] = {}

    def measure(self, name: str, duration: float) -> None:
        """測定値を記録。

        Parameters
        ----------
        name : str
            測定項目名
        duration : float
            測定時間（秒）
        """
        if name not in self.measurements:
            self.measurements[name] = []
        self.measurements[name].append(duration)

    def get_stats(self, name: str) -> dict[str, float]:
        """統計情報を取得。

        Parameters
        ----------
        name : str
            測定項目名

        Returns
        -------
        dict[str, float]
            統計情報（平均、最小、最大、合計、回数）
        """
        if name not in self.measurements:
            return {}
        
        values = self.measurements[name]
        return {
            "count": len(values),
            "total": sum(values),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def print_summary(self) -> None:
        """すべての測定項目のサマリーを出力."""
        print("\n--- Performance Summary ---")
        for name in sorted(self.measurements.keys()):
            stats = self.get_stats(name)
            print(f"{name}:")
            print(f"  Count: {stats['count']}")
            print(f"  Total: {stats['total']:.4f}s")
            print(f"  Average: {stats['average']:.4f}s")
            print(f"  Min: {stats['min']:.4f}s")
            print(f"  Max: {stats['max']:.4f}s")

    @contextmanager
    def measure_context(self, name: str):
        """測定用コンテキストマネージャー。

        Parameters
        ----------
        name : str
            測定項目名
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.measure(name, duration)