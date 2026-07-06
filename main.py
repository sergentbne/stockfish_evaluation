from pathlib import Path

import stockfish
import logging
import multiprocessing


BINARY_PATH = Path(".cache/stockfish")

log = logging.Logger(__name__)
log.setLevel(logging.DEBUG)


def main():
    print("Hello from stockfish-evaluation!")
    ensure_stockfish_binary()

    # New Stockfish instance starts at default starting position.
    # No FEN/position set — queries analyze the standard chess startpos.
    fish1 = stockfish.Stockfish(str(BINARY_PATH), depth=20)
    fish2 = stockfish.Stockfish(str(BINARY_PATH), depth=20)

    log.warning(f"{main_loop(fish1, fish2)}, {fish1.get_board_visual()}")


def ensure_stockfish_binary():
    import shutil
    import subprocess
    import tarfile
    from io import BytesIO

    import requests

    if BINARY_PATH.exists():
        return

    BINARY_PATH.parent.mkdir(exist_ok=True)

    try:
        response = requests.get(
            "https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_18.tar.gz",
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download Stockfish source: {e}") from e

    data = response.content
    buffer = BytesIO(data)
    _ = buffer.seek(0)

    try:
        with tarfile.open(fileobj=buffer) as tar:
            tar.extractall(path=BINARY_PATH.parent, filter="data")
    except tarfile.TarError as e:
        raise RuntimeError(f"Failed to extract Stockfish tarball: {e}") from e

    src = BINARY_PATH.parent / "Stockfish-sf_18/src"
    try:
        _ = subprocess.run(
            ["make", "-j", "profile-build"],
            cwd=src,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to compile Stockfish:\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}"
        ) from e

    _ = (src / "stockfish").replace(BINARY_PATH)
    shutil.rmtree(BINARY_PATH.parent / "Stockfish-sf_18", ignore_errors=True)


def main_loop(stockfish1: stockfish.Stockfish, stockfish2: stockfish.Stockfish) -> bool:
    iterable_of_stockfish = (stockfish1, stockfish2)
    is_mate = False
    has_fish1_won: bool | None = None
    moves: list[str | None] = []
    queue_of_uci: multiprocessing.Queue[str] = multiprocessing.Queue()

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
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    import io
    from PIL import Image

    board = chess.Board()
    print("hello")
    while move := queue_of_uci.get(block=True):
        _ = board.push_uci(move)
        svg_string = chess.svg.board(board, size=350)
        svg_buffer = io.BytesIO(svg_string.encode("utf-8"))
        drawing_of_svg = svg2rlg(svg_buffer)
        if drawing_of_svg is None:
            raise Exception("unreachable")
        image_buffer = io.BytesIO()
        _ = renderPM.drawToFile(drawing_of_svg, image_buffer, fmt="png")
        imgcat.imgcat(image_buffer)
    return


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
