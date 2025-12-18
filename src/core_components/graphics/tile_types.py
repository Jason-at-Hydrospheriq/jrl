import numpy as np

# Tile graphic dtype definition
ascii_graphic = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ], metadata={"__name__": "ascii_graphic"}
)

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=ascii_graphic)
