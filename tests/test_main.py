import pytest

from main import (
    check_in_range,
    get_height_from_angle,
    get_motors_from_inputs,
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
    "angle, arm_length, pivot_height, angle_offset, expected",
    [
        (0, 12, 15, 0, 27),
        (90, 12, 15, 90, 3),
        (27, 17.5, 14, 18, 26.375)
    ]
)
def test_get_height_from_angle_valid(angle, arm_length, pivot_height, angle_offset, expected):
    assert get_height_from_angle(angle, arm_length, pivot_height, angle_offset) == pytest.approx(expected, abs=0.001, rel=0)

@pytest.mark.parametrize(
    "angle, arm_length, pivot_height, angle_offset",
    [
        (372.56, 0, 12, 54.63),
        (-372.56, -1, 253, 6545.34),
        (123.456789, 152, 0, 52432),
        (61254.43, 65, -1, 43),
    ]
)
def test_get_height_from_angle_value_error(angle, arm_length, pivot_height, angle_offset):
    with pytest.raises(ValueError):
        get_height_from_angle(angle, arm_length, pivot_height, angle_offset)