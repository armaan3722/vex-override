import math

from vex import *

DRIVE_WHEELS_DIAMETER: float = 10.16
"""Diameter in CM."""

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
        ValueError: If input_value is outside the definend range.
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
        wheel_diameter: The diameter of the wheels

    Returns:
        The amount of rotations to achieve the desired distance

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
    left_drive_motor.spin_for(FORWARD, rotations, TURNS, speed, PERCENT, False)
    right_drive_motor.spin_for(FORWARD, rotations, TURNS, speed, PERCENT, True)


##############################
### USER CONTROL FUNCTIONS ###
##############################


def control_drive() -> None:
    """Do user control for the drivetrain."""
    # Get amounts to move each motor
    left_motor_speed, right_motor_speed = get_motors_from_inputs(
        controller.axis3.position(), controller.axis1.position()
    )

    # Control left motor
    if left_motor_speed == 0:
        left_drive_motor.stop()
    else:
        left_drive_motor.spin(FORWARD, left_motor_speed, PERCENT)

    # Control right motor
    if right_motor_speed == 0:
        right_drive_motor.stop()
    else:
        right_drive_motor.spin(FORWARD, right_motor_speed, PERCENT)


def control_arm() -> None:
    """Control the arm and claw connected to the arm."""
    if controller.buttonUp.pressing() and not controller.buttonDown.pressing():
        claw_arm_motor.spin(FORWARD, 25, PERCENT)
    elif controller.buttonDown.pressing() and not controller.buttonUp.pressing():
        claw_arm_motor.spin(REVERSE, 25, PERCENT)
    else:
        claw_arm_motor.stop()

    if controller.buttonRight.pressing() and not controller.buttonLeft.pressing():
        claw_motor.spin(FORWARD, 25, PERCENT)
    elif controller.buttonLeft.pressing() and not controller.buttonRight.pressing():
        claw_motor.spin(REVERSE, 25, PERCENT)
    else:
        claw_motor.stop()


def user_control() -> None:
    """Control all functionality required for the user control period."""
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


def start_testing_mode() -> None:
    # Clear both screens
    brain.screen.clear_screen()
    controller.screen.clear_screen()

    # Print testing message
    brain.screen.set_cursor(1, 1)
    controller.screen.set_cursor(1, 1)
    brain.screen.print("Testing mode")
    controller.screen.print("Testing mode")

    wait(2, SECONDS)

    # Print menu information
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print("A to drive\nB for auto")

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
    # Set list of functions
    low_level_functions = [("Drive CM", test_drive_cm)]

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


def test_drive_cm():
    distance = 10
    speed = 50

    while True:
        controller.screen.clear_screen()
        controller.screen.set_cursor(1, 1)
        controller.screen.print("Use up and down to set distance.")
        controller.screen.set_cursor(2, 1)
        controller.screen.print("Press X to start test.")
        controller.screen.set_cursor(3, 1)
        controller.screen.print("Testing " + str(distance) + "cm.")

        while True:
            if (
                controller.buttonX.pressing()
                or controller.buttonUp.pressing()
                or controller.buttonDown.pressing()
            ):
                break

        if controller.buttonUp.pressing():
            distance += 5
        elif controller.buttonDown.pressing():
            distance -= 5
        else:
            break

    while True:
        controller.screen.clear_screen()
        controller.screen.set_cursor(1, 1)
        controller.screen.print("Use up and down to set speed.")
        controller.screen.set_cursor(2, 1)
        controller.screen.print("Press A to start test.")
        controller.screen.set_cursor(3, 1)
        controller.screen.print("Testing " + str(speed) + "%")

        while True:
            if (
                controller.buttonA.pressing()
                or controller.buttonUp.pressing()
                or controller.buttonDown.pressing()
            ):
                break

        if controller.buttonUp.pressing():
            speed += 5
        elif controller.buttonDown.pressing():
            speed -= 5
        else:
            drive_cm(distance, speed)


#####################
### STARTING CODE ###
#####################

if __name__ == "__main__":
    # Create objects
    brain = Brain()
    controller = Controller(PRIMARY)
    right_drive_motor: Motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
    """The drive motor on the right, rotating forward is aligned to forward movement."""
    left_drive_motor: Motor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
    """The drive motor on the left, rotating forward is aligned to forward movement."""
    claw_motor: Motor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)
    """The motor that opens and closes the claw, forward will open claw."""
    claw_arm_motor: Motor = Motor(Ports.PORT8, GearSetting.RATIO_18_1, True)
    """The motor that changes the height of the arm that the claw is on, forward
    will lift the arm up."""

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
