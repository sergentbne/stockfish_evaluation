import stockfish
import requests
import os
from pathlib import Path
import tarfile
from io import BytesIO

import subprocess

PATH = Path(".cache/stockfish")


def main():
    print("Hello from stockfish-evaluation!")
    get_stockfish_if_not_there()
    fish = stockfish.Stockfish(PATH.as_posix(), depth=20)

    print(fish.get_top_moves(3))
    best_wrapper = list()
    best = fish.get_best_move()
    if best is None:
        return
    best_wrapper.append(best)
    print(fish.get_board_visual())
    fish.make_moves_from_current_position(best_wrapper)
    print(fish.get_board_visual())


def get_stockfish_if_not_there():
    if os.path.exists(PATH):
        return

    PATH.parent.mkdir(exist_ok=True)
    data = requests.get(
        "https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_18.tar.gz"
    ).content
    buffer = BytesIO(data)
    buffer.seek(0)
    with tarfile.open(fileobj=buffer) as tar:
        tar.extractall(path=PATH.parent)

    current_dir = Path(os.curdir).absolute()

    os.chdir(".cache/Stockfish-sf_18/src")
    subprocess.run(
        ["make", "-j", "profile-build"],
        check=True,
        capture_output=True,
    )
    os.replace("stockfish", current_dir / PATH)
    os.chdir(current_dir)

    return


if __name__ == "__main__":
    main()
