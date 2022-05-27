"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new instance of the Names class"""
    return Names()

@pytest.fixture
def name_string_list():
    """Return a list of example names"""
    return ["cycle", "NAND", "connected"]

@pytest.fixture
def names_with_items(name_string_list):
    """Return a Names class instance with three items in the names list"""
    new_names = Names()
    [cycle_id, NAND_id, connected_id] = new_names.lookup(name_string_list)
    return new_names

def test_unique_error_codes_raises_exceptions(names_with_items):
    """Test if unique_error_codes raises expected exceptions"""
    with pytest.raises(TypeError):
        names_with_items.unique_error_codes(2.6)
    with pytest.raises(TypeError):
        names_with_items.unique_error_codes("test1")
    with pytest.raises(ValueError):
        names_with_items.unique_error_codes(-5)
    with pytest.raises(ValueError):
        names_with_items.unique_error_codes(0)

def test_query_raises_exceptions(names_with_items):
    """Test if query raises expected exceptions"""
    with pytest.raises(TypeError):
        names_with_items.query(5)
    with pytest.raises(TypeError):
        names_with_items.query(True)

def test_lookup_raises_exceptions(names_with_items):
    """Test if lookup raises expected exceptions"""
    with pytest.raises(TypeError):
        names_with_items.lookup(10)
    with pytest.raises(TypeError):
        names_with_items.lookup("test2")
    with pytest.raises(TypeError):
        names_with_items.lookup([1, 4, 5])
    with pytest.raises(TypeError):
        names_with_items.lookup(["test 3", 10.2, "test4"])

def test_get_name_string_raises_exceptions(names_with_items):
    """Test if get_name_string raises expected exceptions"""
    with pytest.raises(TypeError):
        names_with_items.get_name_string("test5")
    with pytest.raises(TypeError):
        names_with_items.get_name_string(31.5)
    with pytest.raises(ValueError):
        names_with_items.get_name_string(-7)

def test_unique_error_codes(new_names):
    """Test if unique_error_codes returns the expected range and changes the error_code_count correctly"""
    assert new_names.error_code_count == 0
    assert new_names.unique_error_codes(5) == range(0, 5)
    assert new_names.error_code_count == 5
    assert new_names.unique_error_codes(1) == range(5, 6)

@pytest.mark.parametrize("name_string, expected_id", [
    ("cycle", 0),
    ("NAND", 1),
    ("connected", 2),
    ("undefined", None)
])
def test_query(names_with_items, new_names, name_string, expected_id):
    """Test if query returns the expected id"""
    #Name is present
    assert names_with_items.query(name_string) == expected_id
    #Name is absent
    assert new_names.query(name_string) is None

def test_lookup(names_with_items):
    """Test if lookup returns the expected list of name IDs and adds new names correctly"""
    pass


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "cycle"),
    (1, "NAND"),
    (2, "connected"),
    (3, None)
])
def test_get_name_string(names_with_items, new_names, name_id, expected_string):
    """Test if get_name_string returns the expected string"""
    #Name is present
    assert names_with_items.get_name_string(name_id) == expected_string
    #Name is absent
    assert new_names.get_name_string(name_id) is None
