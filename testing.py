import multiprocessing
from pathlib import Path

from matplotlib.image import AxesImage
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from logic import main_loop

MIN_DEPTH = 1
MAX_DEPTH = 20


def main():
    depths = list(range(MIN_DEPTH, MAX_DEPTH + 1))
    depths.reverse()
    n = len(depths)
    score_matrix = np.full((n, n), np.nan)

    with multiprocessing.Pool(processes=5) as pool:
        all_pairs = [(w, b) for w in depths for b in depths]
        results = list(
            tqdm(
                pool.imap(game_result, all_pairs),
                total=len(all_pairs),
                desc="Simulating games",
            ),
        )

    idx = 0
    for w in range(n):
        for b in range(n):
            result = results[idx]
            if result is None:
                score_matrix[b, w] = 0.5
            elif result:
                score_matrix[b, w] = 1.0
            else:
                score_matrix[b, w] = 0.0
            idx += 1

    plot_heatmap(score_matrix, depths)
    plot_aggregate(score_matrix, depths)


def game_result(depths: tuple[int, int]) -> bool | None:
    board = main_loop(depths[0], depths[1], display_moves=False)
    outcome = board.outcome()
    if outcome is None:
        return None
    return outcome.winner


def plot_heatmap(score_matrix: np.ndarray, depths: list[int]):
    path_heatmap = Path("graphs/depth_heatmap.png")
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(
        score_matrix,
        cmap="RdYlGn",
        origin="lower",
        aspect="equal",
        vmin=0,
        vmax=1,
    )
    n = len(depths)
    _ = ax.set_xticks(range(n))
    _ = ax.set_yticks(range(n))
    _ = ax.set_xticklabels(depths)
    _ = ax.set_yticklabels(depths)
    _ = ax.set_xlabel("White Depth")
    _ = ax.set_ylabel("Black Depth")
    _ = ax.set_title("Stockfish Self-Play: White Score by Depth")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(["Black Wins", "Draw", "White Wins"])
    plt.tight_layout()
    path_heatmap.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path_heatmap, dpi=150)
    print("Saved depth_heatmap.png")


def plot_aggregate(score_matrix: np.ndarray, depths: list[int]):
    aggregate_path = Path("graphs/depth_aggregate.png")
    n = len(depths)
    white_win_rates = np.zeros(n)
    black_win_rates = np.zeros(n)
    draw_rates = np.zeros(n)

    for i in range(n):
        row = score_matrix[i, :]
        white_win_rates[i] = np.sum(row == 1.0) / n
        black_win_rates[i] = np.sum(row == 0.0) / n
        draw_rates[i] = np.sum(row == 0.5) / n

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(depths, white_win_rates, "g-o", label="White Wins")
    ax1.plot(depths, draw_rates, "b-o", label="Draws")
    ax1.plot(depths, black_win_rates, "r-o", label="Black Wins")
    ax1.set_xlabel("White Depth (vs all Black depths)")
    ax1.set_ylabel("Rate")
    ax1.set_title("Outcome Rate by White Depth")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    col_white = np.array([np.sum(score_matrix[:, j] == 1.0) / n for j in range(n)])
    col_black = np.array([np.sum(score_matrix[:, j] == 0.0) / n for j in range(n)])
    col_draw = np.array([np.sum(score_matrix[:, j] == 0.5) / n for j in range(n)])

    ax2.plot(depths, col_black, "r-o", label="Black Wins")
    ax2.plot(depths, col_draw, "b-o", label="Draws")
    ax2.plot(depths, col_white, "g-o", label="White Wins")
    ax2.set_xlabel("Black Depth (vs all White depths)")
    ax2.set_ylabel("Rate")
    ax2.set_title("Outcome Rate by Black Depth")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    aggregate_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(aggregate_path, dpi=150)
    print("Saved depth_aggregate.png")


if __name__ == "__main__":
    main()
