import matplotlib.pyplot as plt
import numpy as np

from src.main import get_output_from_input_curve

# Constants
NEUTRAL_DEADZONE = 5
MAX_DEADZONE = 5
MIN_DEADZONE = 5
POSITIVE_BASE = 15
NEGATIVE_BASE = 15

# Get X and Y values
x_values = np.linspace(-100, 100, 400)
y_values = [
    get_output_from_input_curve(
        x, NEUTRAL_DEADZONE, MAX_DEADZONE, MIN_DEADZONE, POSITIVE_BASE, NEGATIVE_BASE
    )
    for x in x_values
]

# Draw graph
plt.figure(figsize=(8, 8))
plt.plot(x_values, y_values, color="blue")
plt.axhline(linestyle="--", linewidth=0.8, color="black")
plt.axvline(linestyle="--", linewidth=0.8, color="black")
plt.title("Controller input curve")
plt.xlabel("Controller input")
plt.ylabel("Input used")
plt.grid(True, linestyle=":")
plt.show()
