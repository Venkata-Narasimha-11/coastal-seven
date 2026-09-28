"""
Practice Program 3: Temperature Converter
Converts between Celsius (C), Fahrenheit (F), and Kelvin (K).
Demonstrates:
- Functions with input validation
- Multiple return/conversions
- Clean conditional logic
"""

def celsius_to_fahrenheit(c: float) -> float:
    return (c * 9 / 5) + 32

def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32) * 5 / 9

def celsius_to_kelvin(c: float) -> float:
    return c + 273.15

def kelvin_to_celsius(k: float) -> float:
    if k < 0:
        raise ValueError("Kelvin cannot be negative (Absolute zero is 0 K).")
    return k - 273.15

def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Universal converter.
    Supported units: 'C', 'F', 'K' (case-insensitive)
    """
    from_unit = from_unit.strip().upper()
    to_unit = to_unit.strip().upper()

    if from_unit == to_unit:
        return round(value, 2)

    # 1. Normalize from source unit to Celsius
    if from_unit == 'C':
        celsius = value
    elif from_unit == 'F':
        celsius = fahrenheit_to_celsius(value)
    elif from_unit == 'K':
        celsius = kelvin_to_celsius(value)
    else:
        raise ValueError(f"Unknown source unit: {from_unit}")

    # 2. Convert Celsius to target unit
    if to_unit == 'C':
        result = celsius
    elif to_unit == 'F':
        result = celsius_to_fahrenheit(celsius)
    elif to_unit == 'K':
        result = celsius_to_kelvin(celsius)
    else:
        raise ValueError(f"Unknown target unit: {to_unit}")

    return round(result, 2)


if __name__ == "__main__":
    print("=== Temperature Converter Examples ===")
    test_cases = [
        (100, 'C', 'F'),   # Boiling point of water: 212 F
        (32, 'F', 'C'),    # Freezing point: 0 C
        (0, 'C', 'K'),     # 273.15 K
        (300, 'K', 'C'),   # ~26.85 C
        (98.6, 'F', 'C'),  # Human body temp: 37 C
    ]

    for val, src, dst in test_cases:
        res = convert_temperature(val, src, dst)
        print(f"{val} deg {src} = {res} deg {dst}")
