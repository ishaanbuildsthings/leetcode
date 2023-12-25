from solution import Solution
from solution import testcases

sol = Solution()

# parses the leetcode copy paste input for input and output, example:
# """Input: s = "1001", k = 3
# Output: 4"""
def parse_input(input_str):
    input_str = ' '.join(input_str.split('\n'))  # Join the lines
    input_part, output_part = input_str.split(' Output: ')
    inputs = input_part.replace('Input: ', '').split(', ')
    input_dict = {}
    for inp in inputs:
        key, value = inp.split(' = ')
        input_dict[key] = eval(value)
    expected_output = eval(output_part)
    return input_dict, expected_output

# finds the only method for our solution class
def find_solution_method(sol):
    for attr_name in dir(sol):
        if callable(getattr(sol, attr_name)) and not attr_name.startswith("__"):
            return getattr(sol, attr_name)
    return None

def run_single_test(arguments):
    sol = Solution()
    solution_method = find_solution_method(sol)
    return solution_method(**arguments)

def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")
RED = '31'
GREEN = '32'

def run_tests():
    for i, testcase in enumerate(testcases):
        arguments, expected = parse_input(testcase)
        result = run_single_test(arguments)

        formatted_arguments = '\n'.join([f"{key} = {value}" for key, value in arguments.items()])

        if result != expected:
            print_colored(f"Testcase #{i + 1} failed with inputs:\n{formatted_arguments}", RED)
            print_colored(f"Got {result}, expected: {expected}", RED)
        else:
            print_colored(f"Test passed for testcase #{i + 1}. Result: {result}", GREEN)
        print("__________")

run_tests()
