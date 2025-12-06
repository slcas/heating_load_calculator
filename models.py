from dataclasses import dataclass, field
from typing import List, Optional


# Heat capacity of air (Wh / (m³ K))
AIR_HEAT_CAPACITY_WH_PER_M3K = 0.34
# Heat capacity of water (Wh / (kg K))
WATER_HEAT_CAPACITY_WH_PER_KGK = 1.163


@dataclass
class Surface:
    """
    Single heat-transferring surface (wall, window, floor, ceiling, door, etc.).
    """
    name: str
    area_m2: float
    u_w_m2k: float
    delta_t_k: float

    def heat_loss_w(self) -> float:
        """
        Transmission heat loss through this surface in Watt.
        Q = A * U * ΔT
        """
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
    delta_t_supply_return_k: float
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
    
    @property
    def flow_rate_l_h(self) -> float:
        return self.total_heat_load_w / (WATER_HEAT_CAPACITY_WH_PER_KGK * self.delta_t_supply_return_k)


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
        label_width = 30
        value_width = 12
        num_dash_equals = 70

        print("=" * num_dash_equals)
        print("Heating load report")
        print("=" * num_dash_equals)

        for room in self.rooms:
            print(f"Room: {room.name}")
            print(
                f"  {'Setpoint temperature        :':<{label_width}} "
                f"{room.setpoint_temp_c:>{value_width}.1f} °C"
            )
            print(
                f"  {'Delta T supply-return flow  :':<{label_width}} "
                f"{room.delta_t_supply_return_k:>{value_width}.1f} K"
            )
            print(
                f"  {'Transmission losses         :':<{label_width}} "
                f"{room.transmission_loss_w:>{value_width}.1f} W"
            )
            print(
                f"  {'Ventilation losses          :':<{label_width}} "
                f"{room.ventilation_loss_w:>{value_width}.1f} W"
            )
            # For total, align both W and kW columns
            print(
                f"  {'Total room load             :':<{label_width}} "
                f"{room.total_heat_load_w:>{value_width}.1f} W "
            )
            print(
                f"  {'Flow rate                   :':<{label_width}} "
                f"{room.flow_rate_l_h/60:>{value_width}.1f} l/min "
            )
            print("-" * num_dash_equals)

        total_w = self.total_heat_load_w
        print(
            f"{'Total building load           :':<{label_width+2}} "
            f"{total_w:>{value_width}.1f} W "
            f"     ({total_w/1000:>{value_width}.3f} kW)"
        )
        print("=" * num_dash_equals)