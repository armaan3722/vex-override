import pytest

from main import (
    check_in_range,
    get_height_from_angle,
    get_motors_from_inputs,
    get_output_from_input_curve,
    get_rotations_from_angle,
    get_rotations_from_distance,
)

######################
### CHECK IN RANGE ###
######################


@pytest.mark.parametrize(
    "input_value, min_value, max_value, min_inclusive, max_inclusive, raise_error",
    [
        # Exclusive min
        (4.999, 5, None, False, False, True),
        (5, 5, None, False, False, True),
        (5.001, 5, None, False, False, False),
        # Inclusive min
        (4.999, 5, None, True, False, True),
        (5, 5, None, True, False, False),
        (5.001, 5, None, True, False, False),
        # Exclusive max
        (4.999, None, 5, False, False, False),
        (5, None, 5, False, False, True),
        (5.001, None, 5, False, False, True),
        # Inclusive max
        (4.999, None, 5, False, True, False),
        (5, None, 5, False, True, False),
        (5.001, None, 5, False, True, True),
        # Test boundaryless
        (float("inf"), 5, None, False, False, False),
        (float("-inf"), None, 5, False, False, False),
        (float("inf"), None, None, False, False, False),
        (float("-inf"), None, None, False, False, False),
        # Test 2 bounds
        (0, -12, 5.3, True, False, False),
        (-12, -12, 5.3, True, False, False),
        (-12.001, -12, 5.3, True, False, True),
        (5.3, -12, 5.3, True, False, True),
        (5.299, -12, 5.3, True, False, False),
        (-100, -12, 5.3, True, False, True),
        (100, -12, 5.3, True, False, True),
    ],
)
def test_check_in_range(
    input_value, min_value, max_value, min_inclusive, max_inclusive, raise_error
):
    if raise_error:
        with pytest.raises(ValueError):
            check_in_range(
                input_value, min_value, max_value, min_inclusive, max_inclusive
            )
    else:
        check_in_range(input_value, min_value, max_value, min_inclusive, max_inclusive)


##############################
### GET MOTORS FROM INPUTS ###
##############################


@pytest.mark.parametrize(
    "throttle_input, steering_input, expected",
    [
        # Only throttle
        (100, 0, (100, 100)),
        (50, 0, (50, 50)),
        (-100, 0, (-100, -100)),
        (-50, 0, (-50, -50)),
        # Only steering
        (0, 100, (100, -100)),
        (0, 50, (50, -50)),
        (0, -100, (-100, 100)),
        (0, -50, (-50, 50)),
        # No input
        (0, 0, (0, 0)),
        # Positive throttle and steering
        (100, 100, (100, 0)),
        (50, 100, (100, -50)),
        (100, 50, (100, 50)),
        (50, 50, (100, 0)),
        (100, -100, (0, 100)),
        (50, -100, (-50, 100)),
        (100, -50, (50, 100)),
        (50, -50, (0, 100)),
        # Negative throttle and steering
        (-100, 100, (-100, 0)),
        (-50, 100, (-100, 50)),
        (-100, 50, (-100, -50)),
        (-50, 50, (-100, 0)),
        (-100, -100, (0, -100)),
        (-50, -100, (50, -100)),
        (-100, -50, (-50, -100)),
        (-50, -50, (0, -100)),
    ],
)
def test_get_motors_from_inputs_valid(throttle_input, steering_input, expected):
    assert get_motors_from_inputs(throttle_input, steering_input) == expected


@pytest.mark.parametrize(
    "throttle_input, steering_input",
    [
        (101, 0),
        (-101, 0),
        (0, 101),
        (0, -101),
        (101, 101),
        (100, -101),
        (-101, 101),
        (-101, -101),
    ],
)
def test_get_motors_from_inputs_value_error(throttle_input, steering_input):
    with pytest.raises(ValueError):
        get_motors_from_inputs(throttle_input, steering_input)


###################################
### GET ROTATIONS FROM DISTANCE ###
###################################


@pytest.mark.parametrize(
    "distance, diameter, expected",
    [
        (100, 10, 3.183),
        (0, 15.3, 0),
        (0.01, 0.03, 0.106),
        (1234.56, 6543.21, 0.06),
        (1234, 0.01, 39279.44),
    ],
)
def test_get_rotations_from_distance(distance, diameter, expected):
    assert get_rotations_from_distance(distance, diameter) == expected


@pytest.mark.parametrize("distance, diameter", [(-1, 1), (1, -1), (-1, -1)])
def test_get_rotations_from_distance_value_error(distance, diameter):
    with pytest.raises(ValueError):
        get_rotations_from_distance(distance, diameter)


###############################
### GET ROTATIONS FROM TURN ###
###############################


@pytest.mark.parametrize(
    "diameter, width, angle, expected",
    [
        (3, 12, 45, 0.5),
        (2, 12, 135, 2.25),
        (2.5, 7.5, 215, 1.792),
        (1, 4, 180, 2),
        (8, 8, -360, -1),
    ],
)
def test_get_rotations_from_angle_valid(diameter, width, angle, expected):
    assert get_rotations_from_angle(diameter, width, angle) == pytest.approx(
        expected, abs=0.001, rel=0
    )


@pytest.mark.parametrize(
    "diameter_one, width_one, angle_one, diameter_two, width_two, angle_two, scale_factor",
    [
        (3, 4, 180, 6, 4, 180, 0.5),
        (5, 2, 273.75, 5, 8, 273.75, 4),
        (4, 2, 45, 4, 2, 135, 3),
        (4, 2, 90, 4, 2, -90, -1),
    ],
)
def test_get_rotations_from_angle_scaling(
    diameter_one, width_one, angle_one, diameter_two, width_two, angle_two, scale_factor
):
    assert get_rotations_from_angle(
        diameter_one, width_one, angle_one
    ) * scale_factor == pytest.approx(
        get_rotations_from_angle(diameter_two, width_two, angle_two), abs=0.001, rel=0
    )


@pytest.mark.parametrize(
    "diameter, width, angle",
    [(-1, 5, 45), (0, 5, 45), (5, -1, 45), (5, 0, 45), (-1, -2, 45)],
)
def test_get_rotations_from_angle_value_error(diameter, width, angle):
    with pytest.raises(ValueError):
        get_rotations_from_angle(diameter, width, angle)


#############################
### GET HEIGHT FROM ANGLE ###
#############################


@pytest.mark.parametrize(
    "angle, arm_length, pivot_height, expected",
    [(0, 12, 15, 27), (180, 12, 15, 3), (45, 17.5, 14, 26.375)],
)
def test_get_height_from_angle_valid(angle, arm_length, pivot_height, expected):
    assert get_height_from_angle(angle, arm_length, pivot_height) == pytest.approx(
        expected, abs=0.001, rel=0
    )


@pytest.mark.parametrize(
    "angle, arm_length, pivot_height",
    [
        (372.56, 0, 12),
        (-372.56, -1, 253),
        (123.456789, 152, 0),
        (61254.43, 65, -1),
    ],
)
def test_get_height_from_angle_value_error(angle, arm_length, pivot_height):
    with pytest.raises(ValueError):
        get_height_from_angle(angle, arm_length, pivot_height)


###################################
### GET OUTPUT FROM INPUT CURVE ###
###################################


@pytest.mark.parametrize(
    "input_value, neutral_deadzone, max_deadzone, min_deadzone, positive_base, negative_base, expected",
    [
        # Neutral deadzone
        (0, 5, 5, 5, 10, 10, 0),
        (5, 5, 5, 5, 10, 10, 0),
        (-5, 5, 5, 5, 10, 10, 0),
        (-12, 12, 5, 5, 10, 10, 0),
        (0, 0, 5, 5, 10, 10, 0),
        # Max deadzone
        (100, 5, 5, 5, 10, 10, 100),
        (95, 5, 5, 5, 10, 10, 100),
        (88, 5, 12, 5, 10, 10, 100),
        (100, 5, 0, 5, 10, 10, 100),
        # Min deadzone
        (-100, 5, 5, 5, 10, 10, -100),
        (-95, 5, 5, 5, 10, 10, -100),
        (-88, 5, 5, 12, 10, 10, -100),
        (-100, 5, 5, 0, 10, 10, -100),
        # Positive curve
        (25, 0, 0, 0, 1, 10, 25),
        (50, 0, 0, 0, 1, 10, 50),
        (75, 0, 0, 0, 1, 10, 75),
        (25, 5, 5, 5, 1, 10, 22.222),
        (50, 5, 5, 5, 1, 10, 50),
        (75, 5, 5, 5, 1, 10, 77.778),
        (25, 5, 5, 5, 10, 10, 7.423),
        (50, 5, 5, 5, 10, 10, 24.025),
        (75, 5, 5, 5, 10, 10, 55.498),
        (25, 5, 5, 5, 0.2, 10, 37.586),
        (50, 5, 5, 5, 0.2, 10, 69.098),
        (75, 5, 5, 5, 0.2, 10, 89.251),
        # Negative curve
        (-25, 0, 0, 0, 10, 1, -25),
        (-50, 0, 0, 0, 10, 1, -50),
        (-75, 0, 0, 0, 10, 1, -75),
        (-25, 5, 5, 5, 10, 1, -22.222),
        (-50, 5, 5, 5, 10, 1, -50),
        (-75, 5, 5, 5, 10, 1, -77.778),
        (-25, 5, 5, 5, 10, 10, -7.423),
        (-50, 5, 5, 5, 10, 10, -24.025),
        (-75, 5, 5, 5, 10, 10, -55.498),
        (-25, 5, 5, 5, 10, 0.2, -37.586),
        (-50, 5, 5, 5, 10, 0.2, -69.098),
        (-75, 5, 5, 5, 10, 0.2, -89.251),
    ],
)
def test_get_output_from_input_curve_valid(
    input_value,
    neutral_deadzone,
    max_deadzone,
    min_deadzone,
    positive_base,
    negative_base,
    expected,
):
    assert get_output_from_input_curve(
        input_value,
        neutral_deadzone,
        max_deadzone,
        min_deadzone,
        positive_base,
        negative_base,
    ) == pytest.approx(expected, abs=0.001, rel=0)


@pytest.mark.parametrize(
    "input_value, neutral_deadzone, max_deadzone, min_deadzone, positive_base, negative_base, raise_error",
    [
        # Input value
        (-101, 1, 2, 3, 4, 5, True),
        (-100, 1, 2, 3, 4, 5, False),
        (0, 1, 2, 3, 4, 5, False),
        (100, 1, 2, 3, 4, 5, False),
        (101, 1, 2, 3, 4, 5, True),
        # Neutral deadzone
        (1, -1, 2, 3, 4, 5, True),
        (1, 0, 2, 3, 4, 5, False),
        (1, 1, 2, 3, 4, 5, False),
        # Max deadzone
        (1, 2, -1, 3, 4, 5, True),
        (1, 2, 0, 3, 4, 5, False),
        (1, 2, 1, 2, 3, 4, False),
        # Min deadzone
        (1, 2, 3, -1, 4, 5, True),
        (1, 2, 3, 0, 4, 5, False),
        (1, 2, 3, 1, 4, 5, False),
        # Positive base
        (1, 2, 3, 4, -1, 5, True),
        (1, 2, 3, 4, 0, 5, True),
        (1, 2, 3, 4, 0.5, 5, False),
        # Negative base
        (1, 2, 3, 4, 5, -1, True),
        (1, 2, 3, 4, 5, 0, True),
        (1, 2, 3, 4, 5, 0.5, False),
    ],
)
def test_get_output_from_input_curve_value_error(
    input_value,
    neutral_deadzone,
    max_deadzone,
    min_deadzone,
    positive_base,
    negative_base,
    raise_error,
):
    if raise_error:
        with pytest.raises(ValueError):
            get_output_from_input_curve(
                input_value,
                neutral_deadzone,
                max_deadzone,
                min_deadzone,
                positive_base,
                negative_base,
            )
    else:
        get_output_from_input_curve(
            input_value,
            neutral_deadzone,
            max_deadzone,
            min_deadzone,
            positive_base,
            negative_base,
        )
