from typing import final

from stockfish import Stockfish

from commons import BINARY_PATH
from logic import main_loop

import multiprocessing
import chess
from tqdm import tqdm


def main():
    with multiprocessing.Pool() as pool:
        all_numbers: list[tuple[int, int]] = []
        for i in range(1, 6):
            for y in range(1, 6):
                all_numbers.append((i, y))
        for i in tqdm(
            pool.imap(
                create_results_from_loop_with_depth,
                all_numbers,
            ),
            total=len(all_numbers),
        ):
            print(i)


def create_results_from_loop_with_depth(depths: tuple[int, int]):
    fish1 = Stockfish(str(BINARY_PATH), depth=depths[0])
    fish2 = Stockfish(str(BINARY_PATH), depth=depths[1])
    all_moves = main_loop(fish1, fish2, display_moves=False)
    board = chess.Board()
    for i in all_moves:
        _ = board.push_uci(i)
    outcome_of_game = board.outcome()
    return outcome_of_game


if __name__ == "__main__":
    main()
