import os
import subprocess
from google import genai
from google.genai import types


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs the python file specified to it, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path of the file to be executed, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="An array of strings containing the arguments to be passed to the python file that is going to be executed. If not provided, it defaults to no arguments.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)


def run_python_file(working_directory, file_path, args=None):
    # Make sure the file is within the working directory
    abs_working = os.path.abspath(working_directory)
    abs_file = os.path.abspath(os.path.join(abs_working, file_path))
    if not (abs_file.startswith(abs_working + os.sep) or abs_file == abs_working):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory\n'

    # Check if the file_path points to a real file
    if not os.path.exists(abs_file):
        return f'Error: File "{file_path}" not found.'

    # Check if the file is a python file
    if not abs_file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    # Run the file
    args = [] if args is None else list(args)
    if not args:
        args = ["python3", file_path]
    else:
        if args[0] not in ("python3", "python"):
            args.insert(0, "python3")
        if len(args) == 1 or args[1] != file_path:
            args.insert(1, file_path)
    try:
        completed_process_result = subprocess.run(
            args=args,
            timeout=30,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=abs_working,
        )
    except TimeoutError:
        return "Error: Operation timedout after 30 seconds"
    except Exception as e:
        return f"Error: executing Python file: {e}"

    # Return feedback to ai agent
    if (
        completed_process_result.stdout == None
        and completed_process_result.stderr == None
    ):
        return "No output produced"
    return_string = f"STDOUT: {completed_process_result.stdout}\nSTDERR: {completed_process_result.stderr}\n"
    if completed_process_result.returncode != 0:
        return_string += (
            f"Process exited with code {completed_process_result.returncode}\n"
        )
    return return_string
