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


##############################
### USER CONTROL FUNCTIONS ###
##############################


def control_drive() -> None:
    """Handle user control for the drivetrain."""
    # Get amounts to move each motor
    left_motor_speed, right_motor_speed = get_motors_from_inputs(
        controller.axis3.position(), controller.axis1.position()
    )

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


def do_nothing_callback() -> None:
    pass


def disable_event_listeners() -> None:
    """Disables button event listeners.

    Disables event listeners for buttonA, buttonB, buttonUp, and buttonDown.
    """
    controller.buttonA.pressed(do_nothing_callback)
    controller.buttonB.pressed(do_nothing_callback)
    controller.buttonUp.pressed(do_nothing_callback)
    controller.buttonDown.pressed(do_nothing_callback)


class Selection:
    """A parent class that has functions that all selection types need."""

    test_menu_data = {}  # noqa: RUF012
    """This is the master dictionary with all data saved for test mode menus.
    The keys should be in the following format:

    key = **test_function_name_property_name**

    Where test_function_name is the final function of the menu, and property_name
    is the name of the property to store."""

    def __init__(self, default_value: float, test_function_name, name: str) -> None:
        """Initialize the Selection object.

        Args:
            default_value: The default value to set if menu has not been
                reached yet.
            test_function_name: The name of the function being tested, used to
                generate unique keys for the master dictionary.
            name: The name of display on the screen and to use for the key in
                the master dictionary.
        """
        # Set instance variables
        self.name = name
        self.key = test_function_name + "_" + name

        # Set current value to the correct value
        if self.key in Selection.test_menu_data:
            self.current_value = Selection.test_menu_data[self.key]
        else:
            self.current_value = default_value
            Selection.test_menu_data[self.key] = self.current_value


class NumericalSelect(Selection):
    """Handles creating a numerical selection menu."""

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
        # Call super init
        super().__init__(default_value, test_function_name, name)

        # Create all instance variables.
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.next_function = next_function
        self.previous_function = previous_function

    def add_number(self) -> None:
        """Add step to the current value, but stay below the maximum value."""
        self.current_value += self.step
        self.current_value = min(self.current_value, self.max_value)
        Selection.test_menu_data[self.key] = self.current_value
        self.print_info()

    def subtract_number(self) -> None:
        """Subtract step from the current value, but stay above the minimum
        value.
        """
        self.current_value -= self.step
        self.current_value = max(self.current_value, self.min_value)
        Selection.test_menu_data[self.key] = self.current_value
        self.print_info()

    def next_menu(self) -> None:
        """Move to the next menu."""
        if self.next_function is not None:
            disable_event_listeners()
            self.next_function()

    def previous_menu(self) -> None:
        """Move to the previous menu."""
        if self.previous_function is not None:
            disable_event_listeners()
            self.previous_function()

    def start_event_listeners(self) -> None:
        """Creates event listeners for controller buttons."""
        controller.buttonUp.pressed(self.add_number)
        controller.buttonDown.pressed(self.subtract_number)
        controller.buttonA.pressed(self.next_menu)
        controller.buttonB.pressed(self.previous_menu)

    def print_info(self) -> None:
        """Print all info to the controller screen."""
        # Clear screen
        controller.screen.clear_screen()

        # Print current info
        controller.screen.set_cursor(1, 1)
        controller.screen.print(self.name)
        controller.screen.set_cursor(2, 1)
        controller.screen.print(self.current_value)


class ListSelect(Selection):
    """Handles creating a list selection menu."""

    def __init__(
        self,
        list_of_choices,
        list_of_functions,
        default_value,
        name,
        test_function_name,
        previous_function,
    ) -> None:
        """Initialize the ListSelect object."""
        # Call super method
        super().__init__(default_value, test_function_name, name)

        # Assign instance variables
        self.list_of_choices = list_of_choices
        self.list_of_functions = list_of_functions
        self.previous_function = previous_function

    def next_option(self) -> None:
        """Move to the next option."""
        self.current_value += 1
        if self.current_value >= len(self.list_of_choices):
            self.current_value = len(self.list_of_choices) - 1
        Selection.test_menu_data[self.key] = self.current_value
        self.print_info()

    def previous_option(self) -> None:
        """Move to the previous option."""
        self.current_value -= 1
        self.current_value = max(self.current_value, 0)
        Selection.test_menu_data[self.key] = self.current_value
        self.print_info()

    def next_menu(self):
        """Move to the next menu."""
        if self.list_of_functions[self.current_value] is not None:
            disable_event_listeners()
            self.list_of_functions[self.current_value]()

    def previous_menu(self):
        """Move to the previous menu."""
        if self.previous_function is not None:
            disable_event_listeners()
            self.previous_function()

    def start_event_listeners(self) -> None:
        """Start the event listeners."""
        controller.buttonUp.pressed(self.next_option)
        controller.buttonDown.pressed(self.previous_option)

    def print_info(self):
        """Print all info to the controller screen."""
        # Clear screen
        controller.screen.clear_screen()

        # Print info
        controller.screen.set_cursor(1, 1)
        controller.screen.print(self.name)
        controller.screen.set_cursor(2, 1)
        controller.screen.print(self.list_of_choices[self.current_value])
        controller.screen.set_cursor(3, 1)
        controller.screen.print(
            str(self.current_value + 1) + "/" + str(len(self.list_of_choices))
        )


def start_testing_mode() -> None:
    """Starts the mode for testing robot functionality, and routes between user
    control or autonomous testing."""
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
    # Define lists
    list_of_choices = [
        "Low level"
    ]
    list_of_functions = [
        select_low_level_function_test
    ]

    # Create object and start event listeners
    menu = ListSelect(list_of_choices, list_of_functions, 0, "auto_mode", "start_testing_mode", start_testing_mode)
    menu.print_info()
    menu.start_event_listeners()

def select_low_level_function_test() -> None:
    """Lets user select which low level function to test.

    Uses predefined list of functions and labels to create a menu where the
    user can scroll through function names and select one to test.  From there,
    they will be routed to the testing menu for that specific function, as
    defined in the initial list of functions.
    """
    # Define variables
    list_of_choices = ["Drive CM"]
    list_of_functions = [test_drive_cm_a_distance_menu]

    # Create object and start event listeners
    menu = ListSelect(
        list_of_choices,
        list_of_functions,
        0,
        "low_level_test",
        "start_testing_mode",
        select_auto_test_mode,
    )
    menu.print_info()
    menu.start_event_listeners()


def test_drive_cm_a_distance_menu() -> None:
    """Get the distance for test_drive_cm"""
    # Start menu
    menu = NumericalSelect(
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
    menu = NumericalSelect(
        -100, 100, 5, 25, "speed", "test_drive_cm", None, test_drive_cm_a_distance_menu
    )
    menu.print_info()
    menu.start_event_listeners()


def test_drive_cm() -> None:
    """Run drive_cm with the selected values."""
    # Get data
    distance = Selection.test_menu_data["test_drive_cm_distance"]
    speed = Selection.test_menu_data["test_drive_cm_speed"]

    # TODO: Switch this to OOP with a start/back selection function
    # Print info
    controller.screen.clear_screen()
    controller.screen.set_cursor(1, 1)
    controller.screen.print(distance + ", " + speed)

    # Create state variable
    button_a_previously_pressed = True
    button_b_previously_pressed = True

    # Create input loop
    while True:
        if controller.buttonA.pressing() and not button_a_previously_pressed:
            drive_cm(distance, speed)
        elif controller.buttonB.pressing() and not button_b_previously_pressed:
            test_drive_cm_b_speed_menu()

        # Update states
        button_a_previously_pressed = controller.buttonA.pressing()
        button_b_previously_pressed = controller.buttonB.pressing()

        # Set to 50hz loop
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
