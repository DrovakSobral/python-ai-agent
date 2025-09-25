import os

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