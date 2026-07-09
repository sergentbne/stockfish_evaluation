import multiprocessing

import chess
import stockfish
from commons import BINARY_PATH
from stockfish_downloader import ensure_stockfish_binary


class _NoopQueue:
    def put(self, item, block=True, timeout=None) -> None:
        pass


def main_loop(
    depth_of_stockfish1: int,
    depth_of_stockfish2: int,
    display_moves: bool = True,
) -> chess.Board:
    ensure_stockfish_binary()

    iterable_of_stockfish = (depth_of_stockfish1, depth_of_stockfish2)

    turn = 0  # index of iterable that will get modulo'd with 2
    engine = stockfish.Stockfish(str(BINARY_PATH))
    board = chess.Board()
    board.reset_board()
    process: multiprocessing.Process | None = None
    queue_of_uci: multiprocessing.Queue[str | None] | _NoopQueue = _NoopQueue()
    if display_moves:
        queue_of_uci = multiprocessing.Queue()
        process = multiprocessing.Process(target=display_moves_init, args=(queue_of_uci,))
        process.start()

    else:
        queue_of_uci = _NoopQueue()  # type: ignore[assignment]
        process = None
    while not board.is_game_over():
        engine.set_depth(iterable_of_stockfish[turn])
        turn = (turn + 1) % 2
        move = engine.get_best_move()
        if move is None:
            raise Exception("Unreachable")

        engine.make_moves_from_current_position([move])
        queue_of_uci.put(move)
        _ = board.push_uci(move)

    if display_moves:
        if process is None:
            raise Exception("Unreachable")

        queue_of_uci.put(None)
        process.join()
        process.close()

    return board


def display_moves_init(queue_of_uci: multiprocessing.Queue[str]):
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
