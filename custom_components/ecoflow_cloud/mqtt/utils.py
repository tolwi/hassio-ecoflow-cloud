from collections import OrderedDict
from typing import Callable


class LimitedSizeOrderedDict(OrderedDict):
    def __init__(self, maxlen=20):
        """Initialize a new DedupStore."""
        super().__init__()
        self.maxlen = maxlen

    def append(self, key, val, on_delete: Callable = None):
        self[key] = val
        self.move_to_end(key)
        if len(self) > self.maxlen:
            # Removes the first record which should also be the oldest
            itm = self.popitem(last=False)
            if on_delete:
                on_delete(itm)
