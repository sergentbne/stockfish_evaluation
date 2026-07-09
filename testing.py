from logic import main_loop

import multiprocessing


def main():
    with multiprocessing.Pool(processes=5) as pool:
        all_numbers: list[tuple[int, int]] = []
        for i in range(1, 6):
            for y in range(1, 6):
                all_numbers.append((i, y))
        maps = (
            pool.map(
                create_results_from_loop_with_depths,
                all_numbers,
            ),
        )
        print(maps)


def create_results_from_loop_with_depths(depths: tuple[int, int]):
    board = main_loop(depths[0], depths[1], display_moves=False)
    outcome_of_game = board.outcome()
    return outcome_of_game


if __name__ == "__main__":
    main()
