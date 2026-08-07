"""Small LRU block cache used by virtual table models."""

from __future__ import annotations

from collections import OrderedDict

type VirtualTableRows = tuple[tuple[str, ...], ...]


class VirtualTableBlockCache:
    """Cache a bounded number of worksheet row blocks using LRU eviction."""

    def __init__(self, max_blocks: int = 5) -> None:
        if max_blocks < 1:
            raise ValueError("max_blocks must be at least 1")
        self._max_blocks = max_blocks
        self._blocks: OrderedDict[int, VirtualTableRows] = OrderedDict()

    def get(self, block_index: int) -> VirtualTableRows | None:
        rows = self._blocks.get(block_index)
        if rows is not None:
            self._blocks.move_to_end(block_index)
        return rows

    def put(self, block_index: int, rows: VirtualTableRows) -> None:
        self._blocks[block_index] = rows
        self._blocks.move_to_end(block_index)
        while len(self._blocks) > self._max_blocks:
            self._blocks.popitem(last=False)

    def clear(self) -> None:
        self._blocks.clear()

    def __len__(self) -> int:
        return len(self._blocks)


__all__ = ["VirtualTableBlockCache", "VirtualTableRows"]
