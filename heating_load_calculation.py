from dataclasses import dataclass, field
from typing import List, Optional


# Heat capacity of air (Wh / (m³ K))
AIR_HEAT_CAPACITY_WH_PER_M3K = 0.34


@dataclass
class Surface:
    """
    Single heat-transferring surface (wall, window, floor, ceiling, door, etc.).
    """
    name: str
    area_m2: float
    length_side_1: float
    length_side_2: float
    u_w_m2k: float
    delta_t_k: float

    def heat_loss_w(self) -> float:
        """
        Transmission heat loss through this surface in Watt.
        Q = A * U * ΔT
        """
        self.area_m2 = self.length_side_1 * self.length_side_2
        return self.area_m2 * self.u_w_m2k * self.delta_t_k


@dataclass
class Ventilation:
    """
    Ventilation (air exchange) heat loss for one room.
    """
    volume_m3: float
    air_change_per_hour: float
    room_temp_c: float
    supply_temp_c: float
    air_heat_capacity_wh_m3k: float = AIR_HEAT_CAPACITY_WH_PER_M3K

    def heat_loss_w(self) -> float:
        """
        Ventilation heat loss in Watt.
        Q = V_dot * c_air * ΔT,
        with V_dot in m³/h, c_air in Wh/(m³ K), ΔT in K.
        """
        delta_t = max(0.0, self.room_temp_c - self.supply_temp_c)
        v_dot_m3_per_h = self.volume_m3 * self.air_change_per_hour
        return v_dot_m3_per_h * self.air_heat_capacity_wh_m3k * delta_t


@dataclass
class Room:
    """
    One room with its setpoint temperature, surfaces and ventilation.
    """
    name: str
    setpoint_temp_c: float
    surfaces: List[Surface] = field(default_factory=list)
    ventilation: Optional[Ventilation] = None

    @property
    def transmission_loss_w(self) -> float:
        return sum(s.heat_loss_w() for s in self.surfaces)

    @property
    def ventilation_loss_w(self) -> float:
        return self.ventilation.heat_loss_w() if self.ventilation else 0.0

    @property
    def total_heat_load_w(self) -> float:
        return self.transmission_loss_w + self.ventilation_loss_w


@dataclass
class Building:
    """
    A building consisting of an arbitrary number of rooms.
    """
    rooms: List[Room] = field(default_factory=list)

    @property
    def total_heat_load_w(self) -> float:
        return sum(r.total_heat_load_w for r in self.rooms)

    def print_report(self) -> None:
        print("=" * 60)
        print("Heating load report")
        print("=" * 60)
        for room in self.rooms:
            print(f"Room: {room.name}")
            print(f"  Setpoint temperature: {room.setpoint_temp_c:.1f} °C")
            print(f"  Transmission losses: {room.transmission_loss_w:.1f} W")
            print(f"  Ventilation losses : {room.ventilation_loss_w:.1f} W")
            print(
                f"  Total room load    : {room.total_heat_load_w:.1f} W "
                f"({room.total_heat_load_w/1000:.3f} kW)"
            )
            print("-" * 60)
        total_w = self.total_heat_load_w
        print(f"Total building load: {total_w:.1f} W ({total_w/1000:.3f} kW)")
        print("=" * 60)


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


def build_room_from_input(index: int) -> Room:
    print(f"\nEntering data for room {index + 1}")
    name = input("Room name: ").strip() or f"Room {index + 1}"
    setpoint_temp_c = input_float("Setpoint temperature of this room (°C): ")

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
        # area = input_float("    Area (m²): ")
        u_value = input_float("    U-value (W/m²K): ")
        temp_other_side = input_float(
            "    Temperature on the other side of this surface "
            "(°C, e.g. outside or adjacent room): "
        )
        delta_t = max(0.0, setpoint_temp_c - temp_other_side)
        surfaces.append(
            Surface(
                name=s_name,
                length_side_1=side_length_1,
                length_side_2=side_length_2,
                area_m2=area,
                u_w_m2k=u_value,
                delta_t_k=delta_t,
            )
        )

    # Ventilation
    ventilation: Optional[Ventilation] = None
    if yes_no("Consider ventilation / air exchange losses for this room?"):
        volume = input_float("  Room air volume (m³): ")
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
        surfaces=surfaces,
        ventilation=ventilation,
    )


def main() -> None:
    print("Heating load calculation (simplified, based on Bosch example)")
    room_count = int(input_float("Number of rooms to calculate: "))

    rooms: List[Room] = []
    for i in range(room_count):
        rooms.append(build_room_from_input(i))

    building = Building(rooms=rooms)
    print()
    building.print_report()


if __name__ == "__main__":
    main()
