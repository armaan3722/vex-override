import math

from vex import *


DRIVE_WHEELS_DIAMETER: float = 10.16
"""Diameter in CM."""


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
    if throttle_input > 100 or throttle_input < -100:
        raise ValueError(
            "The throttle input is out of the required range of -100 - 100 ("
            + str(throttle_input)
            + ")"
        )
    if steering_input > 100 or steering_input < -100:
        raise ValueError(
            "The steering input is out of the required range of -100 - 100 ("
            + str(steering_input)
            + ")"
        )

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
    # Raise errors
    if distance < 0:
        raise ValueError("The distance cannot be negative")

    if wheel_diameter < 0:
        raise ValueError("The wheel diameter cannot be nagetive")

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
    # Raise invalid argument errors
    if distance < 0:
        raise ValueError("The distance cannot be negative")

    if speed < -100 or speed > 100:
        raise ValueError("Speed must be between 100 and -100")

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

def test_drive_cm():
    distance = 10
    speed = 50

    while True:
        controller.screen.clear_screen()
        controller.screen.set_cursor(1, 1)
        controller.screen.print("Use up and down to set distance.")
        controller.screen.set_cursor(2, 1)
        controller.screen.print("Press A to start test.")
        controller.screen.set_cursor(3, 1)
        controller.screen.print("Testing " + str(distance) + "cm.")

        while True:
            if controller.buttonA.pressing() or controller.buttonUp.pressing() or controller.buttonDown.pressing():
                break

        if controller.buttonUp.pressing():
            distance += 5
        elif controller.buttonDown.pressing():
            distance -= 5
        else:
            controller.screen.clear_screen()
            controller.screen.set_cursor(1, 1)
            controller.screen.print("Use up and down to set speed.")
            controller.screen.set_cursor(2, 1)
            controller.screen.print("Press A to start test.")
            controller.screen.set_cursor(3, 1)
            controller.screen.print("Testing " + str(speed) + "%")

            while True:
                if controller.buttonA.pressing() or controller.buttonUp.pressing() or controller.buttonDown.pressing():
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
    elif testing:
        brain.screen.clear_screen()
        brain.screen.print("Currently in testing mode: user control")
        wait(2000)
        brain.screen.clear_screen()
        brain.screen.print("A to drive, B for auto")
        while True:
            if controller.buttonA.pressing() or controller.buttonB.pressing():
                break

        if controller.buttonA.pressing():
            user_control()
        else:
            controller.screen.clear_screen()
            controller.screen.print("A: test low level functions")

            while True:
                if controller.buttonA.pressing():
                    break

            if controller.buttonA.pressing():
                test_drive_cm()