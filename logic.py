import multiprocessing
from typing import Any

import stockfish


class _NoopQueue:
    def put(self, item, block=True, timeout=None) -> None:
        pass


def main_loop(
    stockfish1: stockfish.Stockfish,
    stockfish2: stockfish.Stockfish,
    display_moves: bool = True,
) -> list[str]:
    iterable_of_stockfish = (stockfish1, stockfish2)
    is_mate = False
    moves: list[str] = list()

    if display_moves:
        queue_of_uci: multiprocessing.Queue[str | None] | _NoopQueue = multiprocessing.Queue()
        process = multiprocessing.Process(target=display_moves_init, args=(queue_of_uci,))
        process.start()

    else:
        queue_of_uci = _NoopQueue()  # type: ignore[assignment]
        process = None

    while not is_mate:
        if move := stockfish1.get_best_move():
            apply_moves_to_all_fishes([move], iterable_of_stockfish)
            queue_of_uci.put(move)
            moves.append(move)
        else:
            is_mate = True
            queue_of_uci.put(None)
            break

        if move := stockfish2.get_best_move():
            apply_moves_to_all_fishes([move], iterable_of_stockfish)
            queue_of_uci.put(move)
            moves.append(move)
        else:
            is_mate = True
            queue_of_uci.put(None)
            break

    if display_moves:
        process.join()
        process.close()

    return moves


def display_moves_init(queue_of_uci: multiprocessing.Queue[str]):
    import chess
    import chess.svg

    board = chess.Board()
    while move := queue_of_uci.get(block=True):
        _ = board.push_uci(move)
        svg_string = chess.svg.board(board, size=1200)
        image_bytes = svg_to_png(svg_string)
        display_image_to_screen(image_bytes)
    return


def svg_to_png(svg_string: str):

    import cairosvg

    image_bytes = cairosvg.svg2png(bytestring=svg_string)
    assert isinstance(image_bytes, bytes)
    return image_bytes


def display_image_to_screen(image_bytes: bytes):

    import imgcat

    imgcat.imgcat(image_bytes)


def apply_moves_to_all_fishes(
    move: list[str],
    fishes: tuple[
        stockfish.Stockfish,
        stockfish.Stockfish,
    ],
) -> None:
    for fish in fishes:
        fish.make_moves_from_current_position(move)
