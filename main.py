import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file

# Set the system prompt for the ai agent so it knows how to behave
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# List of available functions for the AI Agent to use
available_funcs = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)

# Get the prompt from the args list
try:
    user_prompt = sys.argv[1]
except IndexError:
    print("Error: no prompt given!")
    sys.exit(1)

# Check if the verbose arg was given
verbose_arg = False
if len(sys.argv) == 3 and (sys.argv[2] == "--verbose" or sys.argv[2] == "-v"):
    verbose_arg = True

# Load env variables and api key
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# List to store roles and messages for the AI Agent
messages_list = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

# Make the API call
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages_list,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt, tools=[available_funcs]
    ),
)

# Print answer to console as well as details if the verbose arg was given
if response.function_calls:
    for call in response.function_calls:
        print(f"Calling function: {call.name}({call.args})")
else:
    print(f"User prompt: {response.text}")
if verbose_arg:
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
