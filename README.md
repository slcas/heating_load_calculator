# Heating Load Calculator

This repository contains a Python command line tool for calculating the heating load of a building using a room-by-room approach. The calculation is based on a simplified stationary model of transmission and ventilation heat losses and is intended for estimation and educational purposes. It is **not** a complete DIN EN 12831 calculation.

The script supports an arbitrary number of rooms and, for each room, an arbitrary number of heat-transferring surfaces (walls, windows, floors, ceilings, doors, etc.).

---

## Features

- Room-by-room heating load calculation
- Any number of rooms
- Any number of surfaces per room
- Automatic surface area calculation from side lengths
- Transmission heat losses per surface  
  \( Q_\text{trans} = A \cdot U \cdot \Delta T \)
- Optional ventilation (air exchange) losses per room  
  \( Q_\text{vent} = \dot{V} \cdot c_\text{air} \cdot \Delta T \)
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

Ensure that the main script file (for example):

```text
heating_load.py
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
python heating_load.py
# or
python3 heating_load.py
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
     \[
     A = \text{length\_side\_1} \times \text{length\_side\_2}
     \]
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

   If you answer `y`, you will be prompted for:

   - `Room air volume (m³):`  
     Interior air volume of the room.
   - `Air changes per hour (1/h):`  
     Air exchange rate \( n \).
   - `Temperature of supply / outside air for ventilation (°C):`  
     Usually the design outdoor temperature or supply air temperature.

   If you answer `n`, ventilation losses are not considered for that room.

5. **Report**

   After all rooms have been processed, the script prints a summary report that includes:

   - Transmission, ventilation, and total heating load for each room
   - Total heating load for the entire building

---

## Calculation model

The calculation model is stationary and consists of two main contributions:

1. Transmission heat losses through building elements  
2. Ventilation (air exchange) heat losses

All results are presented in Watt (W), with a conversion to kilowatt (kW) for convenience.

### 1. Transmission heat losses

For each heat-transferring surface (wall, window, floor, ceiling, door, etc.), the transmission heat loss is calculated as:

\[
Q_\text{trans} = A \cdot U \cdot \Delta T
\]

Where:

- \(A\) is the surface area in m². The script computes it from the side lengths as:
  \[
  A = \text{length\_side\_1} \times \text{length\_side\_2}
  \]
- \(U\) is the U-value of the surface in W/(m²K).
- \(\Delta T\) is the temperature difference between the room air and the environment on the other side of the surface:
  \[
  \Delta T = \max(0,\ T_\text{room} - T_\text{other side})
  \]

If the environment temperature is higher than the room temperature, the expression would become negative, but the script uses the maximum with 0 so that the contribution is never negative.

The **transmission heat loss of a room** is the sum of \(Q_\text{trans}\) over all surfaces defined for that room.

### 2. Ventilation (air exchange) heat losses

Ventilation losses are optional and are considered per room if enabled by the user.

First, the volume flow rate \(\dot{V}\) is derived from the room volume and the air change rate:

\[
\dot{V} = V_\text{room} \cdot n
\]

Where:

- \(V_\text{room}\) = room volume in m³  
- \(n\) = air changes per hour in 1/h

The ventilation heat loss is then:

\[
Q_\text{vent} = \dot{V} \cdot c_\text{air} \cdot \Delta T
\]

Where:

- \(\dot{V}\) = volume flow rate in m³/h  
- \(c_\text{air}\) = volumetric heat capacity of air, fixed in the script as:
  \[
  c_\text{air} = 0.34\ \text{Wh/(m³K)}
  \]
- \(\Delta T\) = temperature difference between room air and supply or outdoor air:
  \[
  \Delta T = \max(0,\ T_\text{room} - T_\text{supply})
  \]

The units are consistent:

- \(\dot{V}\) in m³/h  
- \(c_\text{air}\) in Wh/(m³K)  
- \(\Delta T\) in K  

which yields:

\[
Q_\text{vent} [\text{Wh/h}] = [\text{W}]
\]

so the result is in Watt.

### 3. Room and building heating load

For each room, the total heating load is the sum of its transmission and ventilation losses:

\[
Q_\text{room} = Q_\text{trans,room} + Q_\text{vent,room}
\]

For the entire building, the total heating load is the sum over all rooms:

\[
Q_\text{building} = \sum_\text{rooms} Q_\text{room}
\]

The script prints both values in Watt and in kilowatt:

\[
P_\text{kW} = \frac{P_\text{W}}{1000}
\]

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
  - `length_side_1: float`
  - `length_side_2: float`
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

Create a `LICENSE` file in the repository containing the standard MIT License text and reference it from here:

```markdown
This project is licensed under the terms of the MIT License. See the LICENSE file for details.
```
