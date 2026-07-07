import stockfish
import logging
import multiprocessing
from commons import BINARY_PATH
from stockfish_handler import ensure_stockfish_binary


log = logging.Logger(__name__)
log.setLevel(logging.DEBUG)


def main():
    ensure_stockfish_binary()

    # New Stockfish instance starts at default starting position.
    # No FEN/position set — queries analyze the standard chess startpos.
    fish1 = stockfish.Stockfish(str(BINARY_PATH), depth=1)
    fish2 = stockfish.Stockfish(str(BINARY_PATH), depth=25)

    _ = main_loop(fish1, fish2)


# log.warning(f"{}, {fish1.get_board_visual()}")


def main_loop(stockfish1: stockfish.Stockfish, stockfish2: stockfish.Stockfish) -> bool:
    iterable_of_stockfish = (stockfish1, stockfish2)
    is_mate = False
    has_fish1_won: bool | None = None
    moves: list[str] = []
    queue_of_uci: multiprocessing.Queue[str | None] = multiprocessing.Queue()

    process = multiprocessing.Process(target=display_moves, args=(queue_of_uci,))
    process.start()
    while not is_mate:
        if move := stockfish1.get_best_move():
            moves.append(move)
            apply_moves_to_all_fishes(moves, iterable_of_stockfish)
            queue_of_uci.put(move)
        else:
            is_mate = True
            queue_of_uci.put(None)
            has_fish1_won = False
            break

        if move := stockfish2.get_best_move():
            moves.append(move)
            apply_moves_to_all_fishes(moves, iterable_of_stockfish)
            queue_of_uci.put(move)
        else:
            is_mate = True
            queue_of_uci.put(None)
            has_fish1_won = True
            break
    if has_fish1_won is None:
        raise Exception("Should be unreachable.")
    process.join()
    return has_fish1_won


def display_moves(queue_of_uci: multiprocessing.Queue[str]):
    import chess
    import chess.svg

    import imgcat

    board = chess.Board()
    while move := queue_of_uci.get(block=True):
        _ = board.push_uci(move)
        svg_string = chess.svg.board(board, size=1200)
        image_buffer = svg_to_png(svg_string)
        imgcat.imgcat(image_buffer.getvalue())

    return


def svg_to_png(svg_string: str):

    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    import io

    svg_buffer = io.BytesIO(svg_string.encode("utf-8"))
    drawing_of_svg = svg2rlg(svg_buffer)
    if drawing_of_svg is None:
        raise Exception("unreachable")
    image_buffer = io.BytesIO()
    _ = renderPM.drawToFile(drawing_of_svg, image_buffer, fmt="png")
    return image_buffer


def apply_moves_to_all_fishes(
    moves: list[str],
    fishes: tuple[
        stockfish.Stockfish,
        stockfish.Stockfish,
    ],
) -> None:
    for fish in fishes:
        fish.make_moves_from_start(moves)


if __name__ == "__main__":
    main()
