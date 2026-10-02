import pytest

from main import get_motors_from_inputs


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
        (200, 0),
        (100.01, 0),
        (-200, 0),
        (-100.01, 0),
        (0, 200),
        (0, 100.01),
        (0, -200),
        (0, -100.01),
        (200, -300),
        (-100.01, 100.01),
    ],
)
def test_get_motors_from_inputs_value_error(throttle_input, steering_input):
    with pytest.raises(ValueError):
        get_motors_from_inputs(throttle_input, steering_input)
