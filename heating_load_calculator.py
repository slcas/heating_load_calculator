from helpers import yes_no
from room_builder import build_building_interactive
from config_loader import build_building_from_file


def main() -> None:
    print("Heating load calculation (based on DIN EN 12831)")
    if yes_no("Do you want to load the room configuration from a file?"):
        building = build_building_from_file()
    else:
        building = build_building_interactive()

    print()
    building.print_report()


if __name__ == "__main__":
    main()
