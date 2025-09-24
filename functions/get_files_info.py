import os


def get_files_info(working_directory, directory="."):
    # Get absolute path for the given directory
    abs_working = os.path.abspath(working_directory)
    abs_target = os.path.abspath(os.path.join(abs_working, directory))
    
    # Make sure the directory is within the working directory
    if not (abs_target.startswith(abs_working + os.sep) or abs_target == abs_working):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory\n'
    
    # Make sure directory is a valid directory
    if not os.path.isdir(abs_target):
        return f'Error: "{directory}" is not a directory\n'

    # Get the contents of the directory
    contents_list = os.listdir(abs_target)
    return_string = ""
    for item in contents_list:
        item_path = os.path.join(abs_target, item)
        item_name = item
        item_size = os.path.getsize(item_path)
        item_is_dir = os.path.isdir(item_path)
        return_string += f" - {item_name}: file_size={item_size} bytes, is_dir={item_is_dir}\n"
    return return_string