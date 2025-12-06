from typing import List, Optional

from models import Surface, Ventilation, Room, Building
from helpers import input_float, yes_no


def ask_room_volume() -> float:
    """
    Interactively obtain the room volume in m³.
    """
    if yes_no("Is the room square/rectangular and you want to input its dimensions (LxWxH)?"):
        print("Please enter the room dimensions:")
        length = input_float("  Room length (m): ")
        width = input_float("  Room width (m): ")
        height = input_float("  Room height (m): ")
        volume = length * width * height
        print(f"  Calculated room volume: {volume:.1f} m³")
        return volume

    if yes_no("Do you want to input the room volume directly?"):
        return input_float("  Room air volume (m³): ")

    # Fallback: area * height
    print("Please enter the area and the height:")
    area_room = input_float("  Room area  (m²): ")
    height_room = input_float("  Room height (m): ")
    volume = area_room * height_room
    print(f"  Calculated room volume: {volume:.1f} m³")
    return volume


def build_room_from_input(index: int) -> Room:
    print(f"\nEntering data for room {index + 1}")
    name = input("Room name: ").strip() or f"Room {index + 1}"
    setpoint_temp_c = input_float("Setpoint temperature of this room (°C): ")
    delta_t_supply_return_k = input_float("Temperature delta between supply and return flow (K): ")

    # Surfaces
    surfaces: List[Surface] = []
    surface_count = int(
        input_float(
            "Number of heat-transferring surfaces "
            "(walls, windows, floors, ceilings) in this room: "
        )
    )
    for i in range(surface_count):
        print(f"\n  Surface {i + 1}")
        s_name = (
            input("    Name (e.g. 'exterior wall north', 'window west'): ").strip()
            or f"Surface {i + 1}"
        )
        side_length_1 = input_float("    Side length 1 (m): ")
        side_length_2 = input_float("    Side length 2 (m): ")
        area = side_length_1 * side_length_2
        u_value = input_float("    U-value (W/m²K)  : ")
        temp_other_side = input_float(
            "    Temperature on the other side of this surface "
            "(°C, e.g. outside or adjacent room): "
        )
        delta_t = max(0.0, setpoint_temp_c - temp_other_side)
        surfaces.append(
            Surface(
                name=s_name,
                area_m2=area,
                u_w_m2k=u_value,
                delta_t_k=delta_t,
            )
        )

    # Ventilation
    ventilation: Optional[Ventilation] = None
    if yes_no("\nConsider ventilation / air exchange losses for this room?"):
        volume = ask_room_volume()
        ach = input_float("  Air changes per hour (1/h): ")
        supply_temp = input_float(
            "  Temperature of supply / outside air for ventilation (°C): "
        )
        ventilation = Ventilation(
            volume_m3=volume,
            air_change_per_hour=ach,
            room_temp_c=setpoint_temp_c,
            supply_temp_c=supply_temp,
        )

    return Room(
        name=name,
        setpoint_temp_c=setpoint_temp_c,
        delta_t_supply_return_k=delta_t_supply_return_k,
        surfaces=surfaces,
        ventilation=ventilation,
    )
    

def build_building_interactive() -> Building:
    room_count = int(input_float("Number of rooms to calculate: "))

    rooms: List[Room] = []
    for i in range(room_count):
        rooms.append(build_room_from_input(i))

    return Building(rooms=rooms)

