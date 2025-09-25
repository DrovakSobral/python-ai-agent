import os
from google import genai
from google.genai import types


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of the provided file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be read from, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)


def get_file_content(working_directory, file_path):
    # Check that the file is within the working directory
    abs_working = os.path.abspath(working_directory)
    abs_file = os.path.abspath(os.path.join(abs_working, file_path))
    if not (abs_file.startswith(abs_working + os.sep) or abs_file == abs_working):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory\n'

    # Check to see if the file is a valid file
    if not os.path.isfile(abs_file):
        return f'Error: File not found or is not a regular file: "{file_path}"\n'

    # Read the contents of the file
    MAX_CHARS = 10000
    try:
        with open(abs_file, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            if len(file_content_string) == MAX_CHARS:
                file_content_string += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]\n'
                )
        return file_content_string
    except OSError as e:
        return f"Error: {e}\n"
