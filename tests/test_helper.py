import pytest

from m2u import helper


@pytest.mark.parametrize('name, expected', [
    ('Cube5', 'Cube'),
    ('Cube_5_4', 'Cube_5_'),
    ('5', ''),
    ('Cube55', 'Cube'),
    ('55', ''),
])
def test_remove_number_suffix(name, expected):
    result = helper.remove_number_suffix(name)
    assert result == expected


def test_remove_number_suffix_no_number():
    """Check that no suffix doesn't cause an exception."""
    name = "Cube"
    result = helper.remove_number_suffix(name)
    assert result == "Cube"
