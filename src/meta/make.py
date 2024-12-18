import argparse
import subprocess
import os
import sys

def find_executable(exec_name):
    """
    Find the executable file in the following order:
    1. Explicit path provided.
    2. Current working directory.
    3. System PATH.
    """
    if os.path.isfile(exec_name):
        return exec_name
    cwd_exec = os.path.join(os.getcwd(), exec_name)
    if os.path.isfile(cwd_exec):
        return cwd_exec
    system_path_exec = subprocess.run(["which", exec_name], stdout=subprocess.PIPE, text=True).stdout.strip()
    if system_path_exec and os.path.isfile(system_path_exec):
        return system_path_exec
    return None

def run_gen_and_std(std, gen, name, num, options):
    """
    Runs the generator and the standard executable for the given number of times.
    Generates input files and corresponding answer files.
    """
    for i in range(num):
        # Format the index with leading zeros if necessary
        index = f"{i:02d}"
        input_file = f"{name}_{index}.in"
        output_file = f"{name}_{index}.ans"

        # Run the generator
        with open(input_file, 'w') as infile:
            try:
                if gen.endswith('.py'):
                    subprocess.run([sys.executable, gen] + options, stdout=infile, check=True)
                else:
                    subprocess.run([gen] + options, stdout=infile, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running generator: {e}")
                sys.exit(1)

        # Run the standard executable
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            try:
                subprocess.run([std], stdin=infile, stdout=outfile, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running standard executable: {e}")
                sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run generator and standard executable.")
    parser.add_argument("std", help="Path to the standard executable.")
    parser.add_argument("gen", help="Path to the generator (can be a Python script or binary).")
    parser.add_argument("name", help="Prefix for generated file names.")
    parser.add_argument("num", type=int, help="Number of files to generate.")
    parser.add_argument("option", nargs=argparse.REMAINDER, help="Optional arguments to pass to the generator.")

    args = parser.parse_args()

    # Find the standard executable
    std_path = find_executable(args.std)
    if not std_path:
        print(f"Error: Standard executable '{args.std}' not found.")
        sys.exit(1)

    # Find the generator
    gen_path = find_executable(args.gen)
    if not gen_path:
        print(f"Error: Generator '{args.gen}' not found.")
        sys.exit(1)

    # Run generator and standard executable
    run_gen_and_std(std_path, gen_path, args.name, args.num, args.option or [])

if __name__ == "__main__":
    main()
