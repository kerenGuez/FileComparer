import os
import re
import sys
import glob

import ipdb
from colorama import Fore


TEST_FOLDER = "/home/keren.guez/ex0/ex0/part2/"
# TEST_FOLDER = r"/mnt/c/Users/keren/Downloads/websiteTests/toPublish/"
# TEST_FOLDER = "/mnt/c/Users/keren/Downloads/hw1_more_tests/"
# C_FILE_PATH = "/mnt/c/Users/keren/Pictures/Documents/Technion/introduction_to_cs/h3/hw3q1.c"
# C_FOLDER_PATH = "/mnt/c/Users/keren/Pictures/Documents/Technion/introduction_to_cs/hw3/alonHW/"
C_FOLDER_PATH = "/home/keren.guez/ex0/ex0/part2/"
COMPILED_FILE_PATH = "/tmp/sample_file"
GCC_FLAGS = "-std=c99 -Wall -Werror -pedantic-errors"


def generic_pattern(type_pattern, hw_number, question_number, input_number=None):
    input_number = input_number or r"\d+"
    return rf"^hw{hw_number}q{question_number}{type_pattern}({input_number})[.]txt$"


def more_generic_patt(type_pattern, input_number=None):
    input_number = input_number or r"\d+"
    return rf".+({input_number})\.{type_pattern}"


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


def test_single_c_file(all_files_in_folder, hw_number, question_number, c_file_path, more_generic=None):
    results = []
    # find and iterate through the test input files
    input_pattern = generic_pattern(
        "in", hw_number, question_number) if not more_generic else more_generic_patt("in")
    input_files_path = get_file_names(all_files_in_folder, input_pattern)
    for input_file, match in input_files_path.items():
        print(f"{Fore.LIGHTBLUE_EX}Checking {os.path.basename(input_file)}{Fore.WHITE}")
        input_num = match.groups()[0]
        # get the corresponding output file
        output_pattern = generic_pattern("out", hw_number, question_number, input_num) \
            if not more_generic else more_generic_patt("out", input_num)
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


def test_c_files(all_files_in_folder, all_files_c_folder, hw_number=None, question_number=None):
    results = []

    c_file_pattern = get_c_file_pattern()
    c_file_paths = get_file_names(all_files_c_folder, c_file_pattern)
    if not hw_number or not question_number:
        for c_file, match in c_file_paths.items():
            hw_number, question_number = match.groups()
            test_single_c_file(all_files_in_folder,
                               hw_number, question_number, c_file)
    else:
        test_single_c_file(all_files_in_folder, hw_number,
                           question_number, all_files_c_folder)

    return len(results) and all(results)


if __name__ == '__main__':
    all_the_files_in_folder = glob.glob(f"{TEST_FOLDER}*")
    all_the_files_c_folder = glob.glob(f"{C_FOLDER_PATH}*")

    if len(sys.argv) == 3:
        _, the_hw_number, the_question_number = sys.argv
    # print(test_c_files(all_the_files_in_folder, all_the_files_c_folder, the_hw_number, the_question_number))
    # print(test_c_files(all_the_files_in_folder, all_the_files_c_folder))

    print(test_single_c_file(all_the_files_in_folder, 1,
          1, os.path.join(C_FOLDER_PATH, "mtm_buggy.c"), "yes"))
