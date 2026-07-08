import logging
import multiprocessing

import stockfish

from commons import BINARY_PATH
from stockfish_downloader import ensure_stockfish_binary
from logic import main_loop

log = logging.Logger(__name__)
log.setLevel(logging.DEBUG)


def main():
    ensure_stockfish_binary()

    # New Stockfish instance starts at default starting position.
    # No FEN/position set — queries analyze the standard chess startpos.
    fish1 = stockfish.Stockfish(str(BINARY_PATH), depth=1)
    fish2 = stockfish.Stockfish(str(BINARY_PATH), depth=2)

    _ = main_loop(fish1, fish2)


# log.warning(f"{}, {fish1.get_board_visual()}")


if __name__ == "__main__":
    main()
