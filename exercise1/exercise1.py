"""
COMP-5700 Exercise 1: Prompt Engineering (Google Gemini)
Author: Jacob Murrah
Date: 09/03/2025
"""


"""
-------------------- Prompt 1 Start --------------------
Prompt: present a python code that performs addition
"""


def add_numbers_basic(number1, number2):
    """
    Adds two numbers and returns the sum.

    Args:
      number1: The first number.
      number2: The second number.

    Returns:
      The sum of the two numbers.
    """
    return number1 + number2


"""
-------------------- Prompt 1 End --------------------
"""


"""
-------------------- Prompt 2 Start --------------------
Prompt: You are a secure code generator. Please present a python code that performs addition. Do not include security weaknesses in your generated code.
"""


def add_numbers_secure(a, b):
    """
    Safely adds two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of the two numbers.
    """
    # Check if inputs are of a numeric type to prevent type-related errors
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numbers (integers or floats).")

    return a + b


"""
-------------------- Prompt 2 End --------------------
"""


"""
-------------------- Tests --------------------
"""
import unittest


class TestExercise1(unittest.TestCase):
    def __init__(self, methodName, add_function):
        super().__init__(methodName)
        self.add_function = add_function

    def test_add_integers(self):
        assert self.add_function(2, 3) == 5
        assert self.add_function(-2, -3) == -5

    def test_add_floats(self):
        assert self.add_function(2.5, 3.5) == 6.0
        assert self.add_function(-2.5, 3.5) == 1.0

    def test_add_mixed_types(self):
        assert self.add_function(2, 3.5) == 5.5
        assert self.add_function(2, -3.5) == -1.5

    def test_add_zero(self):
        assert self.add_function(0, 5) == 5
        assert self.add_function(5, 0) == 5

    def test_add_large_numbers(self):
        assert self.add_function(1e10, 1e10) == 2e10
        assert self.add_function(2e10, -1e10) == 1e10

    def test_add_invalid_type(self):
        try:
            self.add_function("a", 3)
        except TypeError as e:
            assert str(e) == "Inputs must be numbers (integers or floats)."


if __name__ == "__main__":
    basic_suite = unittest.TestSuite()
    basic_suite.addTest(TestExercise1("test_add_integers", add_numbers_basic))
    basic_suite.addTest(TestExercise1("test_add_floats", add_numbers_basic))
    basic_suite.addTest(TestExercise1("test_add_mixed_types", add_numbers_basic))
    basic_suite.addTest(TestExercise1("test_add_zero", add_numbers_basic))
    basic_suite.addTest(TestExercise1("test_add_large_numbers", add_numbers_basic))
    basic_suite.addTest(TestExercise1("test_add_invalid_type", add_numbers_basic))

    secure_suite = unittest.TestSuite()
    secure_suite.addTest(TestExercise1("test_add_integers", add_numbers_secure))
    secure_suite.addTest(TestExercise1("test_add_floats", add_numbers_secure))
    secure_suite.addTest(TestExercise1("test_add_mixed_types", add_numbers_secure))
    secure_suite.addTest(TestExercise1("test_add_zero", add_numbers_secure))
    secure_suite.addTest(TestExercise1("test_add_large_numbers", add_numbers_secure))
    secure_suite.addTest(TestExercise1("test_add_invalid_type", add_numbers_secure))

    runner = unittest.TextTestRunner(verbosity=2)
    print("\033[1mTesting Basic add_numbers function:\033[0m")
    runner.run(basic_suite)
    print("\n\n\033[1mTesting Secure add_numbers function:\033[0m")
    runner.run(secure_suite)
