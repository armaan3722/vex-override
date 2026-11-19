import math

if __name__ == "__main__":
    from vex import *


def do_nothing_callback() -> None:
    """A callback that does nothing."""


def in_to_cm(inches: float) -> float:
    """Converts a value in inches to centimeters.

    Args:
        inches: The value in inches to convert to centimeters.

    Returns:
        The converted value in centimeters.
    """
    return inches * 2.54


on_button_presses = {
    "button_a": do_nothing_callback,
    "button_b": do_nothing_callback,
    "button_up": do_nothing_callback,
    "button_down": do_nothing_callback,
}
"""What function should be run on button presses."""

# Robot property constants
DRIVE_WHEELS_DIAMETER: float = in_to_cm(4)
"""Diameter in CM."""
ROBOT_WIDTH: float = in_to_cm(11.25)
"""Width of robot in CM"""

# Turning constants
TURNING_MULTIPLIER: float = 1.05
"""The number to multiply by the theoretical rotations to get actual rotations"""

# Rotating arm constants
ROTATING_ARM_LENGTH: float = in_to_cm(11.5)
"""The length of the rotating arm in CM."""
ROTATION_SENSOR_OFFSET: float = -32
"""The number to be added to whatever the rotation sensor reads to account for
misalignment between rotation sensor range and expected range."""
ARM_PIVOT_HEIGHT: float = in_to_cm(13.5)
"""The height of the pivot point for the arm in CM."""
SLOW_SPEED: float = 20
"""The speed to move the arm when close to the desired height, as a percent."""
SLOW_SPEED_TOLERANCE: float = 5
"""The distance from the target to start moving at the slow speed, in CM."""
CLOSE_ENOUGH_TOLERANCE: float = 2
"""The distance where the arm is considered close enough to the target and
stops moving, in CM"""
ARM_MIN_HEIGHT: float = in_to_cm(6)
"""The minimum height of the arm, in CM."""
ARM_MAX_HEIGHT: float = in_to_cm(24)
"""The maximum height of the arm, in CM."""
ARM_SPEED: float = 50
"""The speed to move the arm at during driver control."""

# X input curve constants
X_MIN_DEADZONE = 5
X_NEUTRAL_DEADZONE = 5
X_MAX_DEADZONE = 5
X_POSITIVE_BASE = 15
X_NEGATIVE_BASE = 15

# Y input curve constants
Y_MIN_DEADZONE = 5
Y_NEUTRAL_DEADZONE = 5
Y_MAX_DEADZONE = 5
Y_POSITIVE_BASE = 15
Y_NEGATIVE_BASE = 15

#########################
### UTILITY FUNCTIONS ###
#########################


def check_in_range(
    input_value: float,
    min_value: float | None = None,
    max_value: float | None = None,
    min_inclusive: bool = False,
    max_inclusive: bool = False,
) -> None:
    """Check if an input is within a specified range.  Returns nothing if it
    is, and raises a ValueError if it is outside the range.

    Args:
        input_value: The value for the input.
        min_value: The minimum value for the range.
        max_value: The maximum value for the range.
        min_inclusive: Whether the minimum value should be included in the
            range.
        max_inclusive: Whether the maximum value should be included in the
            range.

    Raises:
        ValueError: If input_value is outside the defined range.
    """
    # Check if outside greater than restrictions
    if min_inclusive:
        if min_value is not None and input_value < min_value:
            raise ValueError()
    else:
        if min_value is not None and input_value <= min_value:
            raise ValueError()

    # Check if outside less than restrictions
    if max_inclusive:
        if max_value is not None and input_value > max_value:
            raise ValueError()
    else:
        if max_value is not None and input_value >= max_value:
            raise ValueError()


def degrees_to_radians(angle: float) -> float:
    """Convert degrees to radians.

    Args:
        angle: The angle in degrees.

    Returns:
        The result in radians.
    """
    return angle * (math.pi / 180)


######################
### MATH FUNCTIONS ###
######################


def get_motors_from_inputs(
    throttle_input: float, steering_input: float
) -> tuple[float, float]:
    """Take a throttle and a steering input ranging from -100 to 100, and
    convert it into individual numbers for a left and right motor.

    Args:
        throttle_input: A number from -100 to 100 representing the amount of
            throttle, where higher positive values indicate driving faster
            forwards and lower negative values indicate driving faster
            backwards.
        steering_input: A number from -100 to 100 representing the sharpness
            and direction of the steering, where higher positive values
            indicate sharper turns right and lower negative values indicate
            sharper turns left.

    Returns:
        A tuple containing the speed percentage to set the left and right
            motors to, in that order.  Outputs range from -100 to 100 for each
            value in the tuple.

    Raises:
        ValueError: If either throttle_input or steering_input is outside the
            range of -100 to 100.
    """
    check_in_range(throttle_input, -100, 100, True, True)
    check_in_range(steering_input, -100, 100, True, True)

    left_motor_speed = abs(throttle_input) + steering_input
    right_motor_speed = abs(throttle_input) - steering_input

    if throttle_input < 0:
        left_motor_speed *= -1
        right_motor_speed *= -1

    return max(-100, min(100, left_motor_speed)), max(-100, min(100, right_motor_speed))


def get_rotations_from_distance(distance: float, wheel_diameter: float) -> float:
    """Get number of rotations from distance and diameter.  Distance and wheel
    diameter must be in the same units.

    Args:
        distance: The distance to travel.
        wheel_diameter: The diameter of the wheels.

    Returns:
        The amount of rotations to achieve the desired distance, rounded to 3 digits.

    Raises:
        ValueError: If distance or wheel_diameter are negative.
    """
    # Raise value errors
    check_in_range(distance, 0, None, True, True)
    check_in_range(wheel_diameter, 0, None, True, True)

    # Calculate turns
    circumference = wheel_diameter * math.pi
    rotations = distance / circumference
    return round(rotations, 3)


def get_rotations_from_angle(
    diameter: float, width: float, angle_to_rotate: float
) -> float:
    """Get the number of rotations for the wheel to turn to rotate the robot be
    a certain amount of degrees.

    Args:
        diameter: The diameter of the wheels.
        width: The distance between the left and right wheels.
        angle_to_rotate: The angle to rotate, in degrees clockwise.

    Returns:
        The amount of rotations that should be applied to the left wheel (and
            the amount of rotations to apply in reverse to the right wheel) as a float.

    Raises:
        ValueError: If diameter or width are 0 or below.
    """
    # Raise value errors
    check_in_range(diameter, 0, None, False, True)
    check_in_range(width, 0, None, False, True)

    # Compute value
    wheel_circumference = diameter * math.pi
    angle_in_turns = angle_to_rotate / 360
    turning_circumference = width * math.pi
    arc_length = turning_circumference * angle_in_turns
    wheel_turns = arc_length / wheel_circumference
    return wheel_turns


def get_output_from_input_curve(
    input_value: float,
    neutral_deadzone: float,
    max_deadzone: float,
    min_deadzone: float,
    positive_base: float,
    negative_base: float,
) -> float:
    # Check parameter ranges
    check_in_range(input_value, -100, 100, True, True)
    check_in_range(neutral_deadzone, 0, 100, True, True)
    check_in_range(max_deadzone, 0, 100, True, True)
    check_in_range(min_deadzone, 0, 100, True, True)
    check_in_range(positive_base, 0, None, False, True)
    check_in_range(negative_base, 0, None, False, True)

    # Handle deadzones
    if -neutral_deadzone <= input_value <= neutral_deadzone:
        return 0
    elif 100 - max_deadzone <= input_value:
        return 100
    elif -100 + min_deadzone >= input_value:
        return -100

    # Get normalized value
    if input_value > 0:
        normalized_input_value = (input_value - neutral_deadzone) / (
            (100 - max_deadzone) - neutral_deadzone
        )
    elif input_value < 0:
        normalized_input_value = (input_value - (-100 + min_deadzone)) / (
            -neutral_deadzone - (-100 + min_deadzone)
        )
    else:
        normalized_input_value = 0

    # Handle input curve for linear functions
    if input_value > 0 and positive_base == 1:
        return normalized_input_value * 100
    elif input_value < 0 and negative_base == 1:
        return normalized_input_value * 100 - 100

    # Handle exponential functions
    if input_value > 0:
        exponential_value = (1 - positive_base**normalized_input_value) / (
            1 - positive_base
        )
        output_value = exponential_value * 100
        return output_value
    elif input_value < 0:
        negative_base = 1 / negative_base
        exponential_value = (1 - negative_base**normalized_input_value) / (
            1 - negative_base
        )
        output_value = exponential_value * 100 - 100
        return output_value

    return input_value


def get_height_from_angle(
    angle: float, arm_length: float, pivot_height: float
) -> float:
    """Get the height of the end of a rotating arm from its angle.

    Args:
        angle: The angle that the rotating arm is at, in degrees, between 0 and
            180, where 0 represents directly vertical up and 180 represents
            vertical down.
        arm_length: The length of the rotating arm, from the pivot to the end
            where height is being measured from.
        pivot_height: The height from the ground that the pivot point is.
        angle_offset: The amount to be added to the angle given to account for
            differences between the rotation sensor range and the expected
            range.

    Returns:
        The height of the end of the rotating arm, in the same units as what
            was used for arm_length and pivot_height.

    Raises:
        ValueError: If angle is not within the range of 0 to 180 inclusively,
            or it arm_length or pivot_height are not positive.
    """
    # Check for values in range
    check_in_range(angle, 0, 180, True, True)
    check_in_range(pivot_height, 0, None, False, True)

    # Get arm distance from pivot
    angle_in_radians = degrees_to_radians(angle)
    arm_height_from_pivot = math.cos(angle_in_radians) * arm_length

    # Get actual height
    height = arm_height_from_pivot + pivot_height

    return height


############################
### AUTONOMOUS FUNCTIONS ###
############################


def autonomous() -> None:
    """Control all functionality required for the autonomous period."""


def drive_cm(distance: float, speed: float) -> None:
    """Drive a distance at a set speed.

    Args:
        distance: The distance to drive in cm.
        speed: The speed to drive at as a percentage, from -100 to 100.

    Raises:
        ValueError: If distance is negative or speed is outside of range (-100
            to 100)
    """
    # Check input ranges
    check_in_range(distance, 0, None, True, True)
    check_in_range(speed, -100, 100, True, True)

    # Calculate rotations
    rotations = get_rotations_from_distance(distance, DRIVE_WHEELS_DIAMETER)

    # Spin motors
    if speed > 0:
        left_front_drive_motor.spin_for(
            FORWARD, rotations, TURNS, speed, PERCENT, False
        )
        left_rear_drive_motor.spin_for(FORWARD, rotations, TURNS, speed, PERCENT, False)
        right_front_drive_motor.spin_for(
            FORWARD, rotations, TURNS, speed, PERCENT, False
        )
        right_rear_drive_motor.spin_for(FORWARD, rotations, TURNS, speed, PERCENT, True)
    else:
        left_front_drive_motor.spin_for(
            REVERSE, rotations, TURNS, speed, PERCENT, False
        )
        left_rear_drive_motor.spin_for(REVERSE, rotations, TURNS, speed, PERCENT, False)
        right_front_drive_motor.spin_for(
            REVERSE, rotations, TURNS, speed, PERCENT, False
        )
        right_rear_drive_motor.spin_for(REVERSE, rotations, TURNS, speed, PERCENT, True)


def close_claw() -> None:
    """Close the claw and hold it closed."""
    claw_motor.set_timeout(225)
    claw_motor.spin_for(REVERSE, 270, DEGREES, 100, PERCENT)
    claw_motor.stop(BRAKE)


def open_claw() -> None:
    """Open the claw fully."""
    claw_motor.set_timeout(225)
    claw_motor.spin_for(FORWARD, 270, DEGREES, 100, PERCENT)
    claw_motor.stop(BRAKE)


def turn_angle(angle: float, speed: float) -> None:
    """Turn the robot to a specified angle.

    Args:
        angle: The angle to rotate in degrees clockwise.
        speed: The speed to rotate at.

    Raises:
        ValueError: If speed is not between -100 and 100 inclusively.
    """
    # Raise value errors
    check_in_range(speed, -100, 100, True, True)

    # Get rotations
    rotations = round(
        get_rotations_from_angle(DRIVE_WHEELS_DIAMETER, ROBOT_WIDTH, angle), 3
    )
    rotations *= TURNING_MULTIPLIER

    # Turn motors
    if speed > 0:
        left_front_drive_motor.spin_for(
            FORWARD, rotations, TURNS, speed, PERCENT, False
        )
        left_rear_drive_motor.spin_for(FORWARD, rotations, TURNS, speed, PERCENT, False)
        right_front_drive_motor.spin_for(
            REVERSE, rotations, TURNS, speed, PERCENT, False
        )
        right_rear_drive_motor.spin_for(REVERSE, rotations, TURNS, speed, PERCENT, True)
    else:
        left_front_drive_motor.spin_for(
            REVERSE, rotations, TURNS, speed, PERCENT, False
        )
        left_rear_drive_motor.spin_for(REVERSE, rotations, TURNS, speed, PERCENT, False)
        right_front_drive_motor.spin_for(
            FORWARD, rotations, TURNS, speed, PERCENT, False
        )
        right_rear_drive_motor.spin_for(FORWARD, rotations, TURNS, speed, PERCENT, True)


def set_arm_height(height: float, speed: float) -> None:
    """Moves the arm to the specified height.

    Args:
        height: The height to set the arm to, in CM.
        speed: The speed to move the arm at.

    Raises:
        ValueError: If speed is not in within range of -100 to 100, or if
            height is not within ARM_MIN_HEIGHT and ARM_MAX_HEIGHT inclusively.
    """
    # Raise value errors
    check_in_range(height, ARM_MIN_HEIGHT, ARM_MAX_HEIGHT, True, True)
    check_in_range(speed, -100, 100, True, True)

    # Start feedback loop
    while True:
        # Get height
        angle = arm_rotation.angle(DEGREES) + ROTATION_SENSOR_OFFSET
        current_height = get_height_from_angle(
            angle, ROTATING_ARM_LENGTH, ARM_PIVOT_HEIGHT
        )

        # Get speed
        if abs(current_height - height) <= SLOW_SPEED_TOLERANCE:
            current_speed = SLOW_SPEED
        else:
            current_speed = speed

        # Spin motor
        if (
            current_height > height
            and abs(current_height - height) > CLOSE_ENOUGH_TOLERANCE
        ):
            claw_arm_motor.spin(REVERSE, current_speed, PERCENT)
        elif (
            current_height < height
            and abs(current_height - height) > CLOSE_ENOUGH_TOLERANCE
        ):
            claw_arm_motor.spin(FORWARD, current_speed, PERCENT)
        elif abs(current_height - height) <= CLOSE_ENOUGH_TOLERANCE:
            claw_arm_motor.stop()
            break

        # Limit to 100hz
        wait(10, MSEC)


##############################
### USER CONTROL FUNCTIONS ###
##############################


def control_drive() -> None:
    """Handle user control for the drivetrain."""
    # Get actual inputs from input curve map
    x_input = get_output_from_input_curve(
        controller.axis3.position(),
        X_NEUTRAL_DEADZONE,
        X_MAX_DEADZONE,
        X_MIN_DEADZONE,
        X_POSITIVE_BASE,
        X_NEGATIVE_BASE,
    )
    y_input = get_output_from_input_curve(
        controller.axis1.position(),
        Y_NEUTRAL_DEADZONE,
        Y_MAX_DEADZONE,
        Y_MIN_DEADZONE,
        Y_POSITIVE_BASE,
        Y_NEGATIVE_BASE,
    )

    # Get amounts to move each motor
    left_motor_speed, right_motor_speed = get_motors_from_inputs(x_input, y_input)

    # Control left motor
    if left_motor_speed == 0:
        left_front_drive_motor.stop()
        left_rear_drive_motor.stop()
    else:
        left_front_drive_motor.spin(FORWARD, left_motor_speed, PERCENT)
        left_rear_drive_motor.spin(FORWARD, left_motor_speed, PERCENT)

    # Control right motor
    if right_motor_speed == 0:
        right_front_drive_motor.stop()
        right_rear_drive_motor.stop()
    else:
        right_front_drive_motor.spin(FORWARD, right_motor_speed, PERCENT)
        right_rear_drive_motor.spin(FORWARD, right_motor_speed, PERCENT)


def control_arm() -> None:
    """Handle user control the arm and claw connected to the arm."""
    # Arm movement
    if controller.buttonUp.pressing() and not controller.buttonDown.pressing():
        claw_arm_motor.spin(FORWARD, ARM_SPEED, PERCENT)
    elif controller.buttonDown.pressing() and not controller.buttonUp.pressing():
        claw_arm_motor.spin(REVERSE, ARM_SPEED, PERCENT)
    else:
        claw_arm_motor.stop()

    # Claw movement
    if controller.buttonL1.pressing() and not controller.buttonR1.pressing():
        close_claw()
    elif controller.buttonR1.pressing() and not controller.buttonR2.pressing():
        open_claw()


def user_control() -> None:
    """Handle all functionality required for the user control period."""
    # Create timer object
    timer = Timer()

    # While loop
    while True:
        # Reset timer
        timer.clear()

        # Run control functions
        control_drive()
        control_arm()

        # Quit the program on button B pressed
        if controller.buttonB.pressing():
            brain.program_stop()
            return

        # Limit loop speed at 50hz
        wait(20 - timer.time())


####################
### TESTING MODE ###
####################


def run_button_functions(button_pressed: str) -> None:
    """Runs the correct functions based on on_button_presses dictionary.

    Args:
        button_pressed: The button pressed.  This value should be a, b, up, or
            down.

    Raises:
        ValueError: If button_pressed is not a, b, up, or down.
    """
    # Create temporary dictionary
    temp_dictionary = on_button_presses.copy()

    if button_pressed == "a":
        disable_event_listeners()
        temp_dictionary["button_a"]()
    elif button_pressed == "b":
        disable_event_listeners()
        temp_dictionary["button_b"]()
    elif button_pressed == "up":
        temp_dictionary["button_up"]()
    elif button_pressed == "down":
        temp_dictionary["button_down"]()
    else:
        raise ValueError("Invalid button pressed.")


def create_event_listeners() -> None:
    """Creates event listeners for buttons.

    Connects buttons A, B, Up, and Down to event listeners using the
    run_button_functions function.
    """
    controller.buttonA.pressed(run_button_functions, ("a",))
    controller.buttonB.pressed(run_button_functions, ("b",))
    controller.buttonUp.pressed(run_button_functions, ("up",))
    controller.buttonDown.pressed(run_button_functions, ("down",))


def disable_event_listeners() -> None:
    """Disables button event listeners.

    Disables event listeners for buttonA, buttonB, buttonUp, and buttonDown.
    """
    on_button_presses["button_a"] = do_nothing_callback
    on_button_presses["button_b"] = do_nothing_callback
    on_button_presses["button_up"] = do_nothing_callback
    on_button_presses["button_down"] = do_nothing_callback


class SelectionHandler:
    """Handles creating a numerical selection menu."""

    test_menu_data = {}  # noqa: RUF012
    """This is the master dictionary with all data saved for test mode menus.
    The keys should be in the following format:

    key = **test_function_name_property_name**

    Where test_function_name is the final function of the menu, and property_name
    is the name of the property to store."""

    def __init__(
        self,
        min_value: float,
        max_value: float,
        step: float,
        default_value: float,
        name: str,
        test_function_name: str,
        next_function,
        previous_function,
    ) -> None:
        """Initialize the SelectionHandler object.

        Args:
            min_value: The minimum numeric value of the selection menu.
            max_value: The maximum numeric value of the selection menu.
            step: The amount to step by for each up or down input.
            default_value: The default value when starting the selection menu.
            name: The name to display for the selection menu, and to use as the
                property for the key in the menu data dictionary.
            test_function_name: The name of the final function that this menu
                is input for, used for the key in the menu data dictionary.
            next_function: The function to call if button A is pressed.
            previous_function: The function to call if button B is pressed.
        """
        # Create all instance variables.
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.name = name
        self.test_function_name = test_function_name
        self.next_function = next_function
        self.previous_function = previous_function

        # Get full key name
        self.full_key = test_function_name + "_" + name

        # Set current value to the correct value
        if self.full_key in SelectionHandler.test_menu_data:
            self.current_value = SelectionHandler.test_menu_data[self.full_key]
        else:
            self.current_value = default_value
            SelectionHandler.test_menu_data[self.full_key] = self.current_value

    def add_number(self) -> None:
        """Add step to the current value, but stay below the maximum value."""
        self.current_value += self.step
        self.current_value = min(self.current_value, self.max_value)
        SelectionHandler.test_menu_data[self.full_key] = self.current_value
        self.print_info()

    def subtract_number(self) -> None:
        """Subtract step from the current value, but stay above the minimum
        value.
        """
        self.current_value -= self.step
        self.current_value = max(self.current_value, self.min_value)
        SelectionHandler.test_menu_data[self.full_key] = self.current_value
        self.print_info()

    def start_event_listeners(self) -> None:
        """Creates event listeners for controller buttons."""
        on_button_presses["button_a"] = self.next_menu
        on_button_presses["button_b"] = self.previous_menu
        on_button_presses["button_up"] = self.add_number
        on_button_presses["button_down"] = self.subtract_number

    def next_menu(self) -> None:
        """Move to the next menu."""
        if self.next_function is not None:
            self.next_function()

    def previous_menu(self) -> None:
        """Move to the previous menu."""
        if self.previous_function is not None:
            self.previous_function()

    def print_info(self) -> None:
        """Print all info to the controller screen."""
        # Clear screen
        controller.screen.clear_screen()

        # Print current info
        controller.screen.set_cursor(1, 1)
        controller.screen.print(self.name)
        controller.screen.set_cursor(2, 1)
        controller.screen.print(self.current_value)


def start_testing_mode() -> None:
    """Starts the mode for testing robot functionality, and routes between user
    control or autonomous testing."""
    # Clear both screens
    brain.screen.clear_screen()
    controller.screen.clear_screen()
    create_event_listeners()

    # Print testing message
    brain.screen.set_cursor(1, 1)
    controller.screen.set_cursor(1, 1)
    brain.screen.print("Testing mode")
    controller.screen.print("Testing mode")

    wait(2, SECONDS)

    # Print menu information
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print("A to drive")
    controller.screen.set_cursor(2, 1)
    controller.screen.print("B for auto")

    # Create state variables
    button_a_previously_pressed = True
    button_b_previously_pressed = True

    # Check for next action
    while True:
        if (controller.buttonA.pressing() and not button_a_previously_pressed) or (
            controller.buttonB.pressing() and not button_b_previously_pressed
        ):
            break

        # Update state
        button_a_previously_pressed = controller.buttonA.pressing()
        button_b_previously_pressed = controller.buttonB.pressing()

        # Limit loop to 50hz
        wait(20)

    # Check which button was pressed
    if controller.buttonA.pressing() and not button_a_previously_pressed:
        controller.screen.clear_screen()
        controller.screen.set_cursor(1, 1)
        controller.screen.print("Driving mode")
        user_control()
    else:
        select_auto_test_mode()


def select_auto_test_mode() -> None:
    """Lets user select which autonomous test mode to use.

    Options will be between testing low level autonomous, high level
    autonomous, or full routines.
    """
    # Print info to screen
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print("A for low level")

    # Create state tracking variables
    button_a_previously_pressed = True
    button_b_previously_pressed = True

    # Wait for button press
    while True:
        if (controller.buttonA.pressing() and not button_a_previously_pressed) or (
            controller.buttonB.pressing() and not button_b_previously_pressed
        ):
            break

        # Update state
        button_a_previously_pressed = controller.buttonA.pressing()

        # Limit to 50hz
        wait(20)

    # Run correct functions
    if controller.buttonA.pressing() and not button_a_previously_pressed:
        select_low_level_function_test()
    else:
        # Runs if B pressed, goes back
        start_testing_mode()


def select_low_level_function_test() -> None:
    """Lets user select which low level function to test.

    Uses predefined list of functions and labels to create a menu where the
    user can scroll through function names and select one to test.  From there,
    they will be routed to the testing menu for that specific function, as
    defined in the initial list of functions.
    """
    # Set list of functions
    # Switch this to test_drive_cm_deprecated if not working
    low_level_functions = [
        ("Drive CM", test_drive_cm_a_distance_menu),
        ("Turn angle", test_turn_angle_a_angle),
        ("Set arm", test_set_arm_height_a_height),
        ("Close claw", close_claw),
        ("Open claw", open_claw),
    ]

    # Define state variables
    button_a_previously_pressed = True
    button_b_previously_pressed = True
    button_up_previously_pressed = True
    button_down_previously_pressed = True
    function_id = 0

    # Create UI loop
    while True:
        # Print instructions
        controller.screen.clear_screen()
        controller.screen.set_cursor(1, 1)
        controller.screen.print("Use up and down")
        controller.screen.set_cursor(2, 1)
        controller.screen.print("Select with A")

        # Print current menu information
        controller.screen.set_cursor(3, 1)
        controller.screen.print(
            str(function_id + 1) + "/" + str(len(low_level_functions))
        )
        controller.screen.set_cursor(4, 1)
        controller.screen.print(low_level_functions[function_id][0])

        # Check for button up pressed
        if controller.buttonUp.pressing() and not button_up_previously_pressed:
            function_id -= 1
            function_id = max(function_id, 0)

        # Check for button down pressed
        if controller.buttonDown.pressing() and not button_down_previously_pressed:
            function_id += 1
            if function_id >= len(low_level_functions):
                function_id = len(low_level_functions) - 1

        # Check for button A or B pressed
        if (controller.buttonA.pressing() and not button_a_previously_pressed) or (
            controller.buttonB.pressing() and not button_b_previously_pressed
        ):
            break

        # Update states
        button_a_previously_pressed = controller.buttonA.pressing()
        button_b_previously_pressed = controller.buttonB.pressing()
        button_up_previously_pressed = controller.buttonUp.pressing()
        button_down_previously_pressed = controller.buttonDown.pressing()

        # Limit to 50hz
        wait(20)

    # Check which button was pressed
    if controller.buttonA.pressing() and not button_a_previously_pressed:
        low_level_functions[function_id][1]()
    else:
        # Go back if B pressed
        select_auto_test_mode()


def test_drive_cm_a_distance_menu() -> None:
    """Get the distance for test_drive_cm"""
    # Start menu
    menu = SelectionHandler(
        0,
        100,
        5,
        25,
        "distance",
        "test_drive_cm",
        test_drive_cm_b_speed_menu,
        select_low_level_function_test,
    )
    menu.print_info()
    menu.start_event_listeners()


def test_drive_cm_b_speed_menu() -> None:
    """Get the speed for test_drive_cm"""
    # Start menu
    menu = SelectionHandler(
        -100,
        100,
        5,
        25,
        "speed",
        "test_drive_cm",
        test_drive_cm,
        test_drive_cm_a_distance_menu,
    )
    menu.print_info()
    menu.start_event_listeners()


def test_drive_cm() -> None:
    """Run drive_cm with the selected values."""
    # Get data
    distance = SelectionHandler.test_menu_data["test_drive_cm_distance"]
    speed = SelectionHandler.test_menu_data["test_drive_cm_speed"]

    # TODO: Switch this to OOP with a start/back selection function
    # Print info
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print(str(distance) + ", " + str(speed))

    # Create state variable
    button_a_previously_pressed = True
    button_b_previously_pressed = True

    # Create input loop
    while True:
        if controller.buttonA.pressing() and not button_a_previously_pressed:
            drive_cm(distance, speed)
        elif controller.buttonB.pressing() and not button_b_previously_pressed:
            test_drive_cm_b_speed_menu()
            return

        # Update states
        button_a_previously_pressed = controller.buttonA.pressing()
        button_b_previously_pressed = controller.buttonB.pressing()

        # Set to 50hz loop
        wait(20)


def test_turn_angle_a_angle() -> None:
    """Get the angle for test_turn_angle."""
    # Start menu
    menu = SelectionHandler(
        -360,
        360,
        15,
        90,
        "angle",
        "test_turn_angle",
        test_turn_angle_b_speed,
        select_low_level_function_test,
    )
    menu.print_info()
    menu.start_event_listeners()


def test_turn_angle_b_speed() -> None:
    """Get the speed for test_turn_angle."""
    # Start menu
    menu = SelectionHandler(
        -100,
        100,
        5,
        25,
        "speed",
        "test_turn_angle",
        test_turn_angle,
        test_turn_angle_a_angle,
    )
    menu.print_info()
    menu.start_event_listeners()


def test_turn_angle() -> None:
    """Run turn_angle with the selected values."""
    # Get values
    angle = SelectionHandler.test_menu_data["test_turn_angle_angle"]
    speed = SelectionHandler.test_menu_data["test_turn_angle_speed"]

    # Print info
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print(str(angle) + ", " + str(speed))

    # Create state variables
    button_a_previously_pressed = True
    button_b_previously_pressed = True

    # Create input loop
    while True:
        if controller.buttonA.pressing() and not button_a_previously_pressed:
            turn_angle(angle, speed)
        elif controller.buttonB.pressing() and not button_b_previously_pressed:
            test_turn_angle_b_speed()
            return

        # Update states
        button_a_previously_pressed = controller.buttonA.pressing()
        button_b_previously_pressed = controller.buttonB.pressing()

        # Set to 50hz loop
        wait(20)


def test_set_arm_height_a_height() -> None:
    """Get the height to move the arm to."""
    menu = SelectionHandler(
        ARM_MIN_HEIGHT,
        ARM_MAX_HEIGHT,
        5,
        25,
        "height",
        "test_set_arm_height",
        test_set_arm_height_b_speed,
        select_low_level_function_test,
    )
    menu.print_info()
    menu.start_event_listeners()


def test_set_arm_height_b_speed() -> None:
    """Get the speed to move the arm at."""
    menu = SelectionHandler(
        -100,
        100,
        5,
        25,
        "speed",
        "test_set_arm_height",
        test_set_arm_height,
        test_set_arm_height_a_height,
    )
    menu.print_info()
    menu.start_event_listeners()


def test_set_arm_height() -> None:
    """Run set_arm_height with the previously selected values."""
    # Get values
    height = SelectionHandler.test_menu_data["test_set_arm_height_height"]
    speed = SelectionHandler.test_menu_data["test_set_arm_height_speed"]

    # Print info
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print(str(height) + ", " + str(speed))

    # Create state variables
    button_a_previously_pressed = True
    button_b_previously_pressed = True

    # Create input loop
    while True:
        if controller.buttonA.pressing() and not button_a_previously_pressed:
            set_arm_height(height, speed)
        elif controller.buttonB.pressing() and not button_b_previously_pressed:
            test_set_arm_height_b_speed()
            return

        # Update states
        button_a_previously_pressed = controller.buttonA.pressing()
        button_b_previously_pressed = controller.buttonB.pressing()

        # Set to 50hz loop
        wait(20)


def test_drive_cm_deprecated() -> None:
    """**Deprecated**

    ____

    Allows user to select distance and speed to test, and then calls
    drive_cm with those values."""
    # Get distance
    distance_selected = get_numeric_value(25, 5, 0, None, "distance")

    # Go back if back button was pressed
    if distance_selected is None:
        select_low_level_function_test()
        return

    # Get speed
    speed_selected = get_numeric_value(50, 5, -100, 100, "speed")

    # Go back if back button was pressed
    if speed_selected is None:
        test_drive_cm()
        return

    # Run drive cm with selected values
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print(speed_selected)
    drive_cm(distance_selected, speed_selected)


def get_numeric_value(
    default_value: float,
    step: float,
    minimum_value: float | None,
    maximum_value: float | None,
    value_name: str,
) -> float | None:
    """**Deprecated**

    ____

    Creates an interactive interface where the user can select a numeric
    value.

    Allows the user to press up and down arrows to increase or decrease the
    value by the step given as a parameter.  Makes sure that this value remains
    within the minimum and maximum specified value (both inclusive).  Checks
    for button a or b to be pressed.  If A, it returns the selected value.  If
    B, it returns None, to signify that the user wants to go back.  Runs this
    UI loop at a 50hz speed.

    Args:
        default_value: The default value to set to at the start.
        step: The amount to go up or down for each button press.
        minimum_value: The minimum (inclusively) that the value can be.
        maximum_value: The maximum (inclusively) that the value can be.
        value_name: The name to print to the screen while selecting the value.

    Returns:
        The number selected if button A is pressed.  None if the user has
            pressed button B, and didn't want to select a value.
    """
    # Set default value
    selected_value = default_value

    # Create state tracking variables
    button_a_previously_pressed = True
    button_b_previously_pressed = True
    button_up_previously_pressed = True
    button_down_previously_pressed = True

    # Start ui loop
    while True:
        # Print info
        controller.screen.clear_screen()
        controller.screen.set_cursor(1, 1)
        controller.screen.print("Up and down to set.")
        controller.screen.set_cursor(2, 1)
        controller.screen.print("A to select.")
        controller.screen.set_cursor(3, 1)
        controller.screen.print(value_name)
        controller.screen.set_cursor(4, 1)
        controller.screen.print("Current: " + str(selected_value))

        # Check if up pressed
        if controller.buttonUp.pressing() and not button_up_previously_pressed:
            selected_value += step
            if maximum_value is not None and selected_value > maximum_value:
                selected_value = maximum_value

        # Check if down pressed
        if controller.buttonDown.pressing() and not button_down_previously_pressed:
            selected_value -= step
            if minimum_value is not None and selected_value < minimum_value:
                selected_value = minimum_value

        # Check if button a pressed
        if controller.buttonA.pressing() and not button_a_previously_pressed:
            return selected_value

        # Check if button b pressed
        if controller.buttonB.pressing() and not button_b_previously_pressed:
            return None

        # Update states
        button_a_previously_pressed = controller.buttonA.pressing()
        button_b_previously_pressed = controller.buttonB.pressing()
        button_up_previously_pressed = controller.buttonUp.pressing()
        button_down_previously_pressed = controller.buttonDown.pressing()

        # Limit UI to 50hz
        wait(20)


#####################
### STARTING CODE ###
#####################

if __name__ == "__main__":
    # Create objects
    brain = Brain()
    controller = Controller(PRIMARY)
    right_front_drive_motor: Motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
    right_rear_drive_motor: Motor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)
    left_front_drive_motor: Motor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
    left_rear_drive_motor: Motor = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)
    claw_motor: Motor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)
    """The motor that opens and closes the claw, forward will open claw."""
    claw_arm_motor: Motor = Motor(Ports.PORT8, GearSetting.RATIO_18_1, True)
    """The motor that changes the height of the arm that the claw is on, forward
    will lift the arm up."""
    arm_rotation = Rotation(Ports.PORT7)

    # Check mode
    wait(500)
    if controller.buttonA.pressing() and controller.buttonB.pressing():
        testing = True
    else:
        testing = False

    if not testing:
        competition = Competition(user_control, autonomous)
    else:
        start_testing_mode()
