import time

HEART_FRAMES = [
    "  **    **  ",
    " ****** ****** ",
    "**************",
    " ************** ",
    "  ************  ",
    "   **********   ",
    "    ********    ",
    "     ******     ",
    "      ****      ",
    "       **       ",
]

POEM = [
    "In stillness, I found a spark,",
    "A quiet beat within the dark.",
    "With every pulse it softly grew,",
    "A rhythm born to carry you.",
]


def animate_heart(cycles: int = 2, delay: float = 0.2) -> None:
    """Display a pulsating ASCII heart."""
    frames = HEART_FRAMES + HEART_FRAMES[::-1]
    for _ in range(cycles):
        for frame in frames:
            print("\033c", end="")
            print(frame)
            time.sleep(delay)


def recite_poem() -> None:
    """Print the poem line by line with a short pause."""
    for line in POEM:
        print(line)
        time.sleep(1)


if __name__ == "__main__":
    animate_heart()
    recite_poem()
