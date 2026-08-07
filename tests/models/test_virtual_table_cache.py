import pytest

from app.models.virtual_table_cache import VirtualTableBlockCache


def test_cache_rejects_invalid_capacity() -> None:
    with pytest.raises(ValueError, match="max_blocks"):
        VirtualTableBlockCache(0)


def test_cache_get_put_clear_and_len() -> None:
    cache = VirtualTableBlockCache(max_blocks=2)
    rows = (("A",),)

    assert cache.get(1) is None
    cache.put(1, rows)

    assert cache.get(1) == rows
    assert len(cache) == 1

    cache.clear()
    assert len(cache) == 0


def test_cache_evicts_least_recently_used_block() -> None:
    cache = VirtualTableBlockCache(max_blocks=2)
    cache.put(1, (("1",),))
    cache.put(2, (("2",),))

    assert cache.get(1) == (("1",),)

    cache.put(3, (("3",),))

    assert cache.get(2) is None
    assert cache.get(1) == (("1",),)
    assert cache.get(3) == (("3",),)
