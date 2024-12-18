# Will be rewrite in the future.

import os
import sys
import subprocess
import argparse
import shutil

def parse_time_limit(tl):
    # Parse the time limit string into seconds.
    if tl.endswith('ms'):
        return float(tl[:-2]) / 1000
    elif tl.endswith('s'):
        return float(tl[:-1])
    else:
        return float(tl) / 1000

def locate_file(file):
    """Locate the file by searching in the current directory and system path."""
    if os.path.isabs(file):
        return file
    if os.path.exists(os.path.join(os.getcwd(), file)):
        return os.path.join(os.getcwd(), file)
    path = shutil.which(file)
    if path:
        return path
    raise FileNotFoundError(f"Cannot locate file: {file}")

def prepare_file(file, make=False):
    """Prepare the file by optionally running `make` and stripping extensions."""
    resolved_file = locate_file(file)
    name, ext = os.path.splitext(resolved_file)
    if make and ext != ".py":
        subprocess.run(["make", name], check=True)
    return resolved_file

def resolve_executable(file):
    """Resolve the appropriate command to execute the given file."""
    resolved_file = locate_file(file)
    if resolved_file.endswith(".py"):
        return [sys.executable, resolved_file]
    return [os.path.splitext(resolved_file)[0]]

def run_command(cmd, input_file=None, output_file=None, time_limit=None):
    """Run a command with optional input/output redirection and timeout."""
    with open(input_file, 'r') if input_file else None as stdin, \
         open(output_file, 'w') if output_file else None as stdout:
        try:
            subprocess.run(cmd, stdin=stdin, stdout=stdout,
                            stderr=subprocess.DEVNULL, timeout=time_limit).check_returncode()
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"ERROR: {e}"
    return "OK"

def compare_files(file1, file2):
    """Compare the contents of two files, ignoring trailing spaces and empty lines."""
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = [line.rstrip() for line in f1]
        lines2 = [line.rstrip() for line in f2]
        return lines1 == lines2

def main():
    parser = argparse.ArgumentParser(description="PAI.py")
    parser.add_argument("src1", help="First program to test")
    parser.add_argument("src2", help="Second program to test")
    parser.add_argument("gen", help="Data generator")
    parser.add_argument("-c", "--checker", help="Output checker")
    parser.add_argument("-t", "--time_limit", help="Time limit for execution")
    parser.add_argument("-m", "--make", action="store_true", help="Make source files")
    parser.add_argument("-g", "--gen_args", help="Arguments for generator")
    args = parser.parse_args()

    # Prepare the source files and generator.
    src1 = resolve_executable(prepare_file(args.src1, args.make))
    src2 = resolve_executable(prepare_file(args.src2, args.make))
    gen_cmd = resolve_executable(args.gen)
    checker_cmd = resolve_executable(args.checker) if args.checker else None

    # Parse the time limit, default to 1 second.
    time_limit = parse_time_limit(args.time_limit) if args.time_limit else 1.0

    # Create temporary directory for files.
    temp_dir = "pai_temp"
    os.makedirs(temp_dir, exist_ok=True)
    input_file = os.path.join(temp_dir, "a.in")
    output1_file = os.path.join(temp_dir, "a.out")
    output2_file = os.path.join(temp_dir, "a.ans")

    iteration = 0
    while True:
        iteration += 1
        print(f"Test case: {iteration}")

        # Run the generator.
        with open(input_file, 'w') as f:
            gen_proc = subprocess.run(gen_cmd + ([args.gen_args] if args.gen_args else []), 
                                      stdout=f, stderr=subprocess.DEVNULL)
            if gen_proc.returncode != 0:
                print(f"ERROR: Generator returned {gen_proc.returncode}")
                break

        # Run src1.
        result1 = run_command(src1, input_file, output1_file, time_limit)
        if result1 != "OK":
            print(f"src1: {result1}")
            break

        # Run src2.
        result2 = run_command(src2, input_file, output2_file, time_limit)
        if result2 != "OK":
            print(f"src2: {result2}")
            break

        # Check outputs using the checker or direct comparison.
        if checker_cmd:
            checker_proc = subprocess.run(checker_cmd + [input_file, output1_file, output2_file], 
                                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if checker_proc.returncode != 0:
                print(f"Checker failed:\n{checker_proc.stderr.decode().strip()}")
                break
        else:
            if not compare_files(output1_file, output2_file):
                print("Outputs differ")
                break

if __name__ == "__main__":
    main()
