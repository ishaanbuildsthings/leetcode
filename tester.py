from solution import Solution
from solution import testcases, expectedResults

sol = Solution()

# parses the leetcode copy paste input: "Input: n = 3, maxDistance = 5, roads = [[0,1,2],[1,2,10],[0,2,10]]"
def parse_input(input_str):
    inputs = input_str.replace('Input: ', '').split(', ')
    input_dict = {}
    for inp in inputs:
        key, value = inp.split(' = ')
        input_dict[key] = eval(value)
    return input_dict

# finds the solution method in the Solution class
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
    for i, (input_str, expected) in enumerate(zip(testcases, expectedResults)):
        arguments = parse_input(input_str)
        result = run_single_test(arguments)

        # print each key-value pair in arguments on a new line
        formatted_arguments = '\n'.join([f"{key} = {value}" for key, value in arguments.items()])

        if result != expected:
            print_colored(f"Testcase #{i + 1} failed with inputs:\n{formatted_arguments}", RED)
            print_colored(f"Got {result}, expected: {expected}", RED)
        else:
            print_colored(f"Test passed for testcase #{i + 1}. Result: {result}", GREEN)
        print("__________")

run_tests()