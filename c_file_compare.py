import os
import re
import sys
import glob

from colorama import Fore

COMPILED_FILE_PATH = "/tmp/sample_file"
GCC_FLAGS = "-std=c99 -Wall -Werror -pedantic-errors"


def generic_pattern(type_pattern, input_number, hw_number, question_number):
    input_number = input_number or r"\d+"
    return rf"^hw{hw_number}q{question_number}{type_pattern}({input_number})[.]txt$"


def more_generic_patt(type_pattern, input_number, *args):
    input_number = input_number or r"\d+"
    return rf".+({input_number})\.{type_pattern}"


def get_pattern(choice, type_pattern, input_number, *args):
    switch_choice = {
        "1": generic_pattern,
        "2": more_generic_patt
    }

    return switch_choice[choice](type_pattern, input_number, *args)


def get_c_file_pattern():
    return rf"^hw(\d+)q(\d+)[.]c$"


def get_file_names(all_files, needed_pattern):
    res = {file_name: re.search(needed_pattern, os.path.basename(file_name))
           for file_name in all_files
           if re.match(needed_pattern, os.path.basename(file_name))}

    return res


def generate_output_file_name(input_file_name):
    base_name = os.path.basename(input_file_name)
    return os.path.join("/tmp", re.sub('in', 'actual_out', base_name))


# check and display the specific difference between the files
def check_diff(actual_content, expected_content):
    is_equal = True
    line_count = 0
    actual_content_len = len(actual_content)
    expected_content_len = len(expected_content)

    for (actual_line, expected_line) in zip(actual_content, expected_content):
        line_count += 1
        if actual_line != expected_line:
            is_equal = False
            print(
                f"expected line length: {len(expected_line)} actual line length : {len(actual_line)}")
            actual_ascii_chars = [ord(c) for c in actual_line]
            expected_ascii_chars = [ord(c) for c in expected_line]
            print(
                f"actual_ascii_chars: {actual_ascii_chars}\nexpected line length : {expected_ascii_chars}")
            print(f"{Fore.YELLOW}line difference on line {line_count}.\n{Fore.RED}expected: "
                  f"{Fore.WHITE}{expected_line}{Fore.RED}\n{'got:': <9} {Fore.WHITE}{actual_line}{Fore.WHITE}")

    if actual_content_len - line_count:
        is_equal = False
        lines_remaining = actual_content[line_count:]
        print(f"{Fore.YELLOW}extra lines on your output file, lines {line_count}-{actual_content_len}:\n"
              f"{Fore.RED}{''.join(lines_remaining)}{Fore.WHITE}")

    elif expected_content_len - line_count:
        is_equal = False
        lines_remaining = expected_content[line_count:]
        print(f"{Fore.YELLOW}extra lines on expected output file, lines {line_count}-{expected_content_len}:\n"
              f"{Fore.RED}{''.join(lines_remaining)}{Fore.WHITE}")

    return is_equal


# open both files and compare their contents
def test_file_diff(actual_output_file_path, expected_output_file_path):
    with open(actual_output_file_path, 'r') as actual_output:
        with open(expected_output_file_path, 'r') as expected_output:
            actual_content = actual_output.readlines()
            expected_content = expected_output.readlines()

            is_equal = check_diff(actual_content, expected_content)

    return is_equal


def test_single_c_file(all_files_in_folder, c_file_path, the_pattern_mode, *args):
    results = []
    # find and iterate through the test input files
    input_pattern = get_pattern(the_pattern_mode, "in", None, *args)
    input_files_path = get_file_names(all_files_in_folder, input_pattern)
    for input_file, match in input_files_path.items():
        print(f"{Fore.LIGHTBLUE_EX}Checking {os.path.basename(input_file)}{Fore.WHITE}")
        input_num = match.groups()[0]
        # get the corresponding output file
        output_pattern = get_pattern(the_pattern_mode, "out", input_num, *args)
        expected_output_file_path = next(
            iter(get_file_names(all_files_in_folder, output_pattern)))
        # compile the c file you want to check, run it with the input file and put the result in
        # an output file
        os.system(f"gcc {c_file_path} {GCC_FLAGS} -o {COMPILED_FILE_PATH}")
        actual_output_file_path = generate_output_file_name(input_file)
        os.system(
            f"{COMPILED_FILE_PATH} < {input_file} > {actual_output_file_path}")
        os.system(f"rm {COMPILED_FILE_PATH} ")

        # test the difference between the files and append to the results array, for a later print
        results.append(test_file_diff(
            actual_output_file_path, expected_output_file_path))

    # clean up after ourselves
    os.system(f"rm /tmp/hw* 2> /dev/null")

    return results


def get_user_input(config_file=None):
    the_hw_num, the_q_num = None, None
    if config_file:
        with open(text_file_path, "r") as file:
            the_content = [line.replace("\n", "") for line in file.readlines()]
            the_test_folder, the_pattern_mode, the_c_folder, the_c_file, the_gcc_flags, *rest = the_content
            if len(rest) >= 2:
                the_hw_num, the_q_num = rest
    else:
        the_test_folder = input("Enter the folder containing the test's inputs and expected outputs: \n")
        the_pattern_mode = input(f"""Enter tests pattern : 
                                 1 : hw<hw_num>q<question_num><in/out><test_num>.txt, e.g: (hw1q1in1.txt)
                                 2 : <words><test_num>.<in/out>, e.g: (test1.in)\n""")
        if the_pattern_mode == 1:
            the_hw_num = input("Enter the hw number")
            the_q_num = input("Enter the q number")

        the_c_folder = input("Enter the folder containing your C file: \n")
        the_c_file = input("Enter the name of your C file: \n")
        change_flags = input(f"""The default gcc flags are : {GCC_FLAGS}.
            would you like to change them?
            press 1 to change, and any key to continue\n""")

        if change_flags == 1:
            the_gcc_flags = input("Enter your custom flags")
        else:
            the_gcc_flags = GCC_FLAGS

    return the_test_folder, the_pattern_mode, the_c_folder, the_c_file, the_gcc_flags, the_hw_num, the_q_num


if __name__ == '__main__':
    text_file_path = None
    if len(sys.argv) == 2:
        text_file_path = sys.argv[1]

    test_folder, pattern_mode, c_folder, c_file, gcc_flags, hw_num, q_num = get_user_input(text_file_path)

    all_the_files_in_folder = glob.glob(f"{test_folder}*")
    all_the_files_c_folder = glob.glob(f"{c_folder}*")

    if pattern_mode == "1":
        print(test_single_c_file(all_the_files_in_folder, os.path.join(c_folder, c_file), pattern_mode, hw_num, q_num))
    elif pattern_mode == "2":
        print(test_single_c_file(all_the_files_in_folder, os.path.join(c_folder, c_file), pattern_mode))
