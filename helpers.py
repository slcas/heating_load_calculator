def input_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Please enter a valid number.")


def yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt + " [y/n]: ").strip().lower()
        if answer in ("y", "yes", "j", "ja"):
            return True
        if answer in ("n", "no", "nein"):
            return False
        print("Please answer with 'y' or 'n'.")