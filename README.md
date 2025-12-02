# Heating Load Calculator

This repository contains a Python command line tool for calculating the heating load of a building using a room-by-room approach. The calculation is based on a simplified stationary model of transmission and ventilation heat losses. It is **not** a complete DIN EN 12831 calculation.

The script supports an arbitrary number of rooms and, for each room, an arbitrary number of heat-transferring surfaces (walls, windows, floors, ceilings, doors, etc.).

The Heating Load Calculator is still a work in progress, so please feel free to point out any mistakes or request changes.

---

## Features

- Room-by-room heating load calculation
- Any number of rooms
- Any number of surfaces per room
- Automatic surface area calculation from side lengths
- Transmission heat losses per surface  
  $Q_\text{trans} = A \cdot U \cdot \Delta T$
- Optional ventilation (air exchange) losses per room  
  $Q_\text{vent} = \dot{V} \cdot c_\text{air} \cdot \Delta T$
- Summary report:
  - Transmission, ventilation, and total load per room
  - Total building heating load in W and kW

---

## Requirements

- Python **3.7 or later**

No external libraries are required. The script uses only the Python standard library:

- `dataclasses`
- `typing`

---

## Installation

Clone the repository and change into the project directory:

```bash
git clone https://github.com/<your-account>/<your-repo>.git
cd <your-repo>
```

Ensure that the main script file:

```text
heating_load_calculator.py
```

is present in the project directory.

Verify that Python 3.7 or later is available:

```bash
python --version
# or
python3 --version
```

---

## Usage

Run the script from the command line:

```bash
python heating_load_calculator.py
# or
python3 heating_load_calculator.py
```

The script then starts an interactive dialogue in the terminal.

### Input sequence

1. **Number of rooms**

   The script first prompts:

   ```text
   Number of rooms to calculate:
   ```

   Enter the integer number of rooms to be included in the calculation.

2. **Room data**

   For each room, you will be prompted for:

   - `Room name:`  
     Descriptive name for the room (for example `Living room`, `Bedroom 1`).  
     If left empty, a default such as `Room 1` is used.
   - `Setpoint temperature of this room (°C):`  
     Design indoor temperature for this room.

3. **Surfaces in the room**

   For each room, the script then prompts:

   ```text
   Number of heat-transferring surfaces (walls, windows, floors, ceilings) in this room:
   ```

   For each surface, it asks:

   - `Name (e.g. 'exterior wall north', 'window west'):`  
     Descriptive name for the surface.
   - `Side length 1 (m):`
   - `Side length 2 (m):`  
     The surface area is calculated internally as:
     $$A = L_1 \times L_2$$
     where $L_1$ and $L_2$ are the two side lengths.
   - `U-value (W/m²K):`  
     Thermal transmittance of the surface.
   - `Temperature on the other side of this surface (°C, e.g. outside or adjacent room):`  
     Examples:
     - Design outdoor temperature for exterior elements
     - Temperature of an unheated basement, stairwell, or garage
     - Temperature of an adjacent room

4. **Ventilation (optional)**

   After the surfaces, the script prompts:

   ```text
   Consider ventilation / air exchange losses for this room? [y/n]:
   ```

   If you answer `n`, no ventilation losses are considered for that room and the script proceeds to the next room.

   If you answer `y`, the script guides you through calculating the room volume in one of three ways:

   1. **Rectangular room (L × W × H)**

      ```text
      Is the room square/rectangular and you want to input its dimensions (LxWxH)? [y/n]:
      ```

      If you answer `y`, you are asked for:

      - `Room length (m):`
      - `Room width (m):`
      - `Room height (m):`

      The room volume is then computed as:

      $$V_\text{room} = \text{length} \times \text{width} \times \text{height}$$

      and displayed, for example:

      ```text
      Calculated room volume: 45.0 m³
      ```

   2. **Direct volume input**

      If you answer `n` to the rectangular question, the script asks:

      ```text
      Do you want to input the room volume directly? [y/n]:
      ```

      If you answer `y`, you are prompted for:

      - `Room air volume (m³):`

      and this value is used directly.

   3. **Area × height**

      If you answer `n` again (you do not want rectangular dimensions and do not want to input the volume directly), the script asks for floor area and room height:

      - `Room area  (m²):`
      - `Room height (m):`

      The room volume is then computed as:

      $$V_\text{room} = \text{area} \times \text{height}$$

      and displayed, for example:

      ```text
      Calculated room volume: 45.0 m³
      ```

   After the volume has been determined by one of the three methods above, the script asks:

   - `Air changes per hour (1/h):`  
     Air exchange rate $n$.
   - `Temperature of supply / outside air for ventilation (°C):`  
     Usually the design outdoor temperature or supply air temperature.

   These inputs are used to calculate the ventilation (air exchange) heat losses for the room.

5. **Report**

   After all rooms have been processed, the script prints a summary report that includes:

   - Transmission, ventilation, and total heating load for each room
   - Total heating load for the entire building



## Configuration from JSON file

In addition to the interactive input, the script can read the complete room configuration from a JSON file. This is useful if you want to:

- Reuse the same building configuration multiple times
- Version control your inputs
- Edit the data in a text editor instead of answering interactive prompts

### How to use JSON input

When you start the script, it first asks:

```text
Do you want to load the room configuration from a file? [y/n]:
```

- If you answer `n`, the script runs in fully interactive mode as described above.
- If you answer `y`, the script asks:

  ```text
  Enter configuration file name (JSON, default: rooms.json, relative to script folder):
  ```

  You can then:

  - Press **Enter** to use the default `rooms.json` file located in the same directory as the script, or
  - Type another file name or relative path (for example `test/haus.json`) that is also located relative to the script folder.

If the file is found and valid, the script constructs the building from the JSON data and directly prints the heating load report. If the file is not found or invalid, an error message is printed and you can try a different file.

### JSON structure

The JSON file must have the following general structure:

```json
{
  "rooms": [
    {
      "name": "Room name",
      "setpoint_temp_c": 21.0,
      "surfaces": [
        {
          "name": "exterior wall north",
          "area_m2": 14.0,
          "u_w_m2k": 0.25,
          "temp_other_side_c": -10.0
        }
      ],
      "ventilation": {
        "mode": "dimensions",
        "length_m": 5.0,
        "width_m": 4.0,
        "height_m": 2.5,
        "air_change_per_hour": 0.5,
        "supply_temp_c": -10.0
      }
    }
  ]
}
```

The semantics correspond to the interactive input:

#### Room fields

Each entry in `rooms` represents one room:

- `name`  
  Room name (string).
- `setpoint_temp_c`  
  Design indoor temperature of the room in °C (float).

#### Surfaces

Each room has a list `surfaces` with one or more heat-transferring elements. For each surface:

- `name`  
  Descriptive name, for example `"exterior wall north"`, `"window west"`.
- `area_m2`  
  Surface area in m² (float).  
  This value corresponds to the product of side lengths you enter in the interactive mode.
- `u_w_m2k`  
  U-value in W/(m²K) (float).
- `temp_other_side_c`  
  Temperature on the other side of the surface in °C (float), for example:
  - Design outdoor temperature for external elements
  - Temperature of an unheated basement or attic
  - Temperature of an adjacent room

From these values the script computes the transmission heat loss in the same way as in interactive mode.

#### Ventilation

The `ventilation` object describes how to determine the room volume and the ventilation parameters. It supports four modes via the `mode` field:

- `"none"`  
  No ventilation calculation for this room.

- `"dimensions"`  
  Volume is computed from length, width, and height:
  ```json
  "ventilation": {
    "mode": "dimensions",
    "length_m": 5.0,
    "width_m": 4.0,
    "height_m": 2.5,
    "air_change_per_hour": 0.5,
    "supply_temp_c": -10.0
  }
  ```

- `"volume"`  
  Volume is given directly:
  ```json
  "ventilation": {
    "mode": "volume",
    "volume_m3": 50.0,
    "air_change_per_hour": 0.5,
    "supply_temp_c": -10.0
  }
  ```

- `"area_height"`  
  Volume is computed from floor area and height:
  ```json
  "ventilation": {
    "mode": "area_height",
    "area_m2": 20.0,
    "room_height_m": 2.5,
    "air_change_per_hour": 0.5,
    "supply_temp_c": -10.0
  }
  ```

For all modes except `"none"`, the following fields are required:

- `air_change_per_hour`  
  Air changes per hour \( n \) in 1/h (float).
- `supply_temp_c`  
  Temperature of supply or outdoor air in °C (float).

These values are used to compute the ventilation heat loss exactly as in the interactive mode.

### Minimal example

A minimal JSON file with two rooms might look like this:

```json
{
  "rooms": [
    {
      "name": "Living room",
      "setpoint_temp_c": 21.0,
      "surfaces": [
        {
          "name": "exterior wall north",
          "area_m2": 14.0,
          "u_w_m2k": 0.25,
          "temp_other_side_c": -10.0
        }
      ],
      "ventilation": {
        "mode": "dimensions",
        "length_m": 5.0,
        "width_m": 4.0,
        "height_m": 2.5,
        "air_change_per_hour": 0.5,
        "supply_temp_c": -10.0
      }
    },
    {
      "name": "Bedroom",
      "setpoint_temp_c": 20.0,
      "surfaces": [
        {
          "name": "exterior wall east",
          "area_m2": 12.0,
          "u_w_m2k": 0.25,
          "temp_other_side_c": -10.0
        }
      ],
      "ventilation": {
        "mode": "none"
      }
    }
  ]
}
```

Placing such a file (for example `rooms.json`) next to the script and choosing “load from file” at startup produces the same type of heating load report as the interactive workflow.


---

## Calculation model

The calculation model is stationary and consists of two main contributions:

1. Transmission heat losses through building elements  
2. Ventilation (air exchange) heat losses

All results are presented in Watt (W), with a conversion to kilowatt (kW) for convenience.

### 1. Transmission heat losses

For each heat-transferring surface (wall, window, floor, ceiling, door, etc.), the transmission heat loss is calculated as:

$$Q_\text{trans} = A \cdot U \cdot \Delta T$$

Where:

- $A$ is the surface area in m². The script computes it from the side lengths as:
  $$A = L_1 \times L_2$$
- $U$ is the U-value of the surface in W/(m²K).
- $\Delta T$ is the temperature difference between the room air and the environment on the other side of the surface:
  $$\Delta T = \max(0,\ T_\text{room} - T_\text{other side})$$

If the environment temperature is higher than the room temperature, the expression would become negative, but the script uses the maximum with 0 so that the contribution is never negative.

The **transmission heat loss of a room** is the sum of $Q_\text{trans}$ over all surfaces defined for that room.

### 2. Ventilation (air exchange) heat losses

Ventilation losses are optional and are considered per room if enabled by the user.

First, the volume flow rate $\dot{V}$ is derived from the room volume and the air change rate:

$$\dot{V} = V_\text{room} \cdot n$$

Where:

- $V_\text{room}$ = room volume in m³  
- $n$ = air changes per hour in 1/h

The ventilation heat loss is then:

$$Q_\text{vent} = \dot{V} \cdot c_\text{air} \cdot \Delta T$$

Where:

- $\dot{V}$ = volume flow rate in m³/h  
- $c_\text{air}$ = volumetric heat capacity of air, fixed in the script as:
  $$c_\text{air} = 0.34\ \text{Wh/(m³K)}$$
- $\Delta T$ = temperature difference between room air and supply or outdoor air:
  $$\Delta T = \max(0,\ T_\text{room} - T_\text{supply})$$

The units are consistent:

- $\dot{V}$ in m³/h  
- $c_\text{air}$ in Wh/(m³K)  
- $\Delta T$ in K  

which yields:

$$Q_\text{vent} [\text{Wh/h}] = [\text{W}]$$

so the result is in Watt.

### 3. Room and building heating load

For each room, the total heating load is the sum of its transmission and ventilation losses:

$$Q_\text{room} = Q_\text{trans,room} + Q_\text{vent,room}$$

For the entire building, the total heating load is the sum over all rooms:

$$Q_\text{building} = \sum_\text{rooms} Q_\text{room}$$

The script prints both values in Watt and in kilowatt:

$$P_\text{kW} = \frac{P_\text{W}}{1000}$$

---

## Example output

A typical output of the script may look as follows (example values):

```text
============================================================
Heating load report
============================================================
Room: Living room
  Setpoint temperature: 21.0 °C
  Transmission losses: 1234.5 W
  Ventilation losses :  345.6 W
  Total room load    : 1580.1 W (1.580 kW)
------------------------------------------------------------
Room: Bedroom
  Setpoint temperature: 20.0 °C
  Transmission losses:  900.0 W
  Ventilation losses :  200.0 W
  Total room load    : 1100.0 W (1.100 kW)
------------------------------------------------------------
Total building load: 2680.1 W (2.680 kW)
============================================================
```

The actual numerical values depend on the input geometry, U-values, temperatures, and ventilation parameters.

---

## Code structure

The script is structured into several data classes and helper functions.

### Data classes

- `Surface`  
  Represents a single heat-transferring surface. Fields:
  - `name: str`
  - `area_m2: float`
  - `u_w_m2k: float`
  - `delta_t_k: float`  
  Method:
  - `heat_loss_w()`  
    Recomputes `area_m2` from side lengths and returns the transmission heat loss in Watt.

- `Ventilation`  
  Represents the ventilation behaviour of a room. Fields:
  - `volume_m3: float`
  - `air_change_per_hour: float`
  - `room_temp_c: float`
  - `supply_temp_c: float`
  - `air_heat_capacity_wh_m3k: float` (default `0.34`)  
  Method:
  - `heat_loss_w()`  
    Computes the ventilation heat loss in Watt.

- `Room`  
  Represents a room. Fields:
  - `name: str`
  - `setpoint_temp_c: float`
  - `surfaces: List[Surface]`
  - `ventilation: Optional[Ventilation]`  
  Properties:
  - `transmission_loss_w`
  - `ventilation_loss_w`
  - `total_heat_load_w`

- `Building`  
  Represents the building as a collection of rooms. Fields:
  - `rooms: List[Room]`  
  Properties and methods:
  - `total_heat_load_w`
  - `print_report()` to generate the console report

### Helper functions

- `input_float(prompt: str) -> float`  
  Reads a floating-point value from standard input with validation.
- `yes_no(prompt: str) -> bool`  
  Reads a yes/no answer (`y/n`, `yes/no`, `ja/nein`).
- `build_room_from_input(index: int) -> Room`  
  Collects all relevant data for a single room interactively and returns a `Room`.
- `main()`  
  Entry point, orchestrates reading input, building the data model, and printing the report.

---

## Limitations and disclaimer

- The tool implements a **simplified** stationary heating load model.
- It does **not** implement DIN EN 12831 or other official standards in full detail.
- It does not account for:
  - Internal heat gains (appliances, occupants)
  - Solar gains
  - Dynamic effects (thermal mass, time-dependent behaviour)
  - Detailed multi-layer building component structures
  - Standardised climate data or official design temperatures

For design, approval, contractual, or warranty-related purposes, a complete heating load calculation according to the applicable standards and local regulations, performed by a qualified professional, is required.

Use this tool at your own responsibility. No liability is assumed for decisions based on the results produced by this script.

---

## License

This project is licensed under the terms of the **MIT License**.  
See the [LICENSE](./LICENSE) file in this repository for the full license text.
