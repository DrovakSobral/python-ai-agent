import os
from google import genai
from google.genai import types


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file, constrained to the working directory. It overwrites the existing content if the file exists or creates a new file if it doesn't.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path pointing to the file we wish to write to. If the file doesn't exist it will create a new one.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)


def write_file(working_directory, file_path, content):
    # Make sure the file is within the working directory
    abs_working = os.path.abspath(working_directory)
    abs_file = os.path.abspath(os.path.join(abs_working, file_path))
    if not (abs_file.startswith(abs_working + os.sep) or abs_file == abs_working):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory\n'

    # If the file doesn't exist, create it. Else just write over it
    with open(abs_file, "w") as f:
        f.write(content)

    # Return string to provide feedback to the ai agent
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
