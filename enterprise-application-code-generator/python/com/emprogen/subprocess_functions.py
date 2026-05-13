#!/usr/bin/env python3
import subprocess
from typing import List


def run_subprocess(arg_list: List[str]) -> None:
    """
    Run a subprocess with the given argument list.

    Args:
        arg_list: List of command-line arguments.
    """
    print(f"Running subprocess:\n    {arg_list}")
    subprocess.run(arg_list, check=True, text=True)


def run_subprocess_capture_output(arg_list: List[str]) -> str:
    """
    Run a subprocess with the given argument list and capture its output.

    Args:
        arg_list: List of command-line arguments.

    Returns:
        The standard output from the subprocess as a string.

    Raises:
        subprocess.CalledProcessError: If the subprocess exits with a non-zero status.
    """
    print(f"Running subprocess:\n    {arg_list}")
    result = subprocess.run(
        arg_list,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return result.stdout


def capture_contextual_command_line_options(command_args: List[str], contextual_command: str) -> List[str]:
    """
    Extracts command line options for a specific contextual command.
    List command_args is defined in run.py and captures command line args passed into script.
    Args:
        command_args: List of command line arguments in the form 'contextualCommand=command1,command2,commandN'.
            Example: 'mvn=-U,-DskipTests java=-Dfile.encoding=UTF-8'
        contextual_command: The command to filter for.

    Returns:
        A list of arguments associated with the contextual_command.
    """
    output = []
    for command_arg in command_args:
        parts = command_arg.split('=', 1)
        if len(parts) != 2:
            print(f"Cannot process command line arg so skipping: {command_arg}")
            continue
        command, args_str = parts
        if command != contextual_command:
            continue
        output.extend(args_str.split(','))
    return output
