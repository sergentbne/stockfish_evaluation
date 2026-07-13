from stockfish_downloader import ensure_stockfish_binary
from logic import main_loop


def main():
    ensure_stockfish_binary()

    _ = main_loop(28, 3)


if __name__ == "__main__":
    main()
