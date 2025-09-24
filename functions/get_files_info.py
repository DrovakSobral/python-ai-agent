import os


def get_files_info(working_directory, directory="."):
    # Get absolute path for the given directory
    full_path = os.path.join(working_directory, directory)
    print(working_directory)
    print(directory)
    print(full_path)
    
    # Make sure directory is a valid directory
    if not os.path.isdir(full_path):
        return f'Error: "{directory}" is not a directory'

    # Make sure the directory is within the working directory
    if not full_path.startswith(working_directory) or directory == "../":
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory\n'
    
    # Get the contents of the directory
    contents_list = os.listdir(full_path)
    return_string = ""
    for item in contents_list:
        item_path = os.path.join(full_path, item)
        item_name = item
        item_size = os.path.getsize(item_path)
        item_is_dir = os.path.isdir(item_path)
        return_string += f" - {item_name}: file_size={item_size} bytes, is_dir={item_is_dir}\n"
    return return_string