import json

from pathlib import Path
from typing import Optional, List
from helpers import yes_no
from models import Surface, Ventilation, Room, Building


def _compute_volume_from_vent_config(vent_cfg: dict) -> float:
    """
    Compute room volume from the ventilation configuration dictionary.
    Supported modes: dimensions, volume, area_height.
    """
    mode = vent_cfg.get("mode", "volume")

    if mode == "dimensions":
        length = float(vent_cfg["length_m"])
        width = float(vent_cfg["width_m"])
        height = float(vent_cfg["height_m"])
        return length * width * height

    if mode == "area_height":
        area = float(vent_cfg["area_m2"])
        height = float(vent_cfg["room_height_m"])
        return area * height

    if mode == "volume":
        return float(vent_cfg["volume_m3"])

    if mode == "none":
        raise ValueError("Ventilation mode 'none' does not define a volume.")

    raise ValueError(f"Unknown ventilation mode: {mode!r}")


def load_building_from_json(path: str) -> Building:
    """
    Load building configuration from a JSON file and return a Building object.
    Expected structure (simplified):

    {
      "rooms": [
        {
          "name": "Living room",
          "setpoint_temp_c": 21.0,
          "surfaces": [
            {
              "name": "...",
              "area_m2": 5.0,
              "u_w_m2k": 0.25,
              "temp_other_side_c": -10.0
            }
          ],
          "ventilation": {
            "mode": "dimensions" | "volume" | "area_height" | "none",
            ...
          }
        }
      ]
    }
    """
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    rooms_cfg = data.get("rooms", [])

    rooms: List[Room] = []

    for r_cfg in rooms_cfg:
        name = r_cfg.get("name", "Room")
        setpoint_temp_c = float(r_cfg["setpoint_temp_c"])

        # Surfaces
        surfaces: List[Surface] = []
        for s_cfg in r_cfg.get("surfaces", []):
            s_name = s_cfg.get("name", "Surface")
            area = float(s_cfg["area_m2"])
            u_value = float(s_cfg["u_w_m2k"])
            temp_other_side = float(s_cfg["temp_other_side_c"])
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
        vent_cfg = r_cfg.get("ventilation")
        ventilation: Optional[Ventilation] = None

        if vent_cfg is not None:
            mode = vent_cfg.get("mode", "volume")
            if mode != "none":
                volume = _compute_volume_from_vent_config(vent_cfg)
                ach = float(vent_cfg["air_change_per_hour"])
                supply_temp = float(vent_cfg["supply_temp_c"])

                ventilation = Ventilation(
                    volume_m3=volume,
                    air_change_per_hour=ach,
                    room_temp_c=setpoint_temp_c,
                    supply_temp_c=supply_temp,
                )

        rooms.append(
            Room(
                name=name,
                setpoint_temp_c=setpoint_temp_c,
                surfaces=surfaces,
                ventilation=ventilation,
            )
        )

    return Building(rooms=rooms)


def build_building_from_file() -> Building:
    while True:
        path = input(
            "Enter path to configuration file (JSON, default: rooms.json): "
        ).strip()
        if not path:
            path = "rooms.json"
        try:
            print(f"Loading building configuration from {path!r}...")
            building = load_building_from_json(path)
            return building
        except FileNotFoundError:
            print(f"File {path!r} not found. Please try again.")
        except (ValueError, KeyError) as exc:
            print(f"Error while reading {path!r}: {exc}")
            if not yes_no("Do you want to try a different file?"):
                raise