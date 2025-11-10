"""
COMP-5700 Workshop 13: Simple White-box Fuzzing
Author: Jacob Murrah
Date: 11/14/2025
"""


def multiply(v1, v2):
    return v1 * v2


def simpleFuzzer():
    errors = [
        ("a", "b"),  # Both string (error #1)
        (5, None),  # None second operand (error #2)
        (None, 5),  # None first operand (error #3)
        (None, None),  # Both None (error #4)
        ([1, 2], [3, 4]),  # Both list (error #5)
        ({"a": 1}, 2),  # Dict first operand (error #6)
        (2, {"a": 1}),  # Dict second operand (error #7)
        ({1, 2}, 3),  # Set first operand (error #8)
        (3, {1, 2}),  # Set second operand (error #9)
        ((1, 2), (3, 4)),  # Both tuple (error #10)
    ]

    output_filename = "crash_messages.txt"
    with open(output_filename, "w") as f:
        for i, error in enumerate(errors):
            try:
                result = multiply(error[0], error[1])
                message = f"multiply({error[0]}, {error[1]}) = {result}"
            except Exception as e:
                message = f"multiply({error[0]}, {error[1]}) raised an exception: {e}"
            f.write(f"Error {i+1}: {message}\n")

    print(f"Fuzzing complete. Results written to {output_filename}")


if __name__ == "__main__":
    simpleFuzzer()
