import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file


# Function that allows the AI Agent to call other functions
def call_function(function_call: types.FunctionCall, verbose=False):
    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")
    
    # Working directory is a constant for security reasons so as to ensure that the AI Agent doesn't fuck up the machine it is running if it hallucinates
    WORKING_DIRECTORY = "./calculator"
    # Check the function that the agent is calling. If it is a valid one, call it, else we return an error
    match function_call.name:
        case "get_files_info":
            result = get_files_info(working_directory=WORKING_DIRECTORY, **function_call.args)
        case "get_file_content":
            result = get_file_content(working_directory=WORKING_DIRECTORY, **function_call.args)
        case "write_file":
            result = write_file(working_directory=WORKING_DIRECTORY, **function_call.args)
        case "run_python_file":
            result = run_python_file(working_directory=WORKING_DIRECTORY, **function_call.args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={"error": f"Unknown function: {function_call.name}"},
                    )
                ],
            )
    
    # Return the result of the function call
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call.name,
                response={"result": result},
            )
        ],
    )

# Set the system prompt for the AI Agent so it knows how to behave
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.


If the user requests any of list/read/write/execute, you must respond only with a function call using the provided tools. Do not ask for more info if the intent is clear.
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

# Main logic loop
for iteration in range(0,20):
    # Make the API call
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages_list,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt, tools=[available_funcs]
        ),
    )

    # Check the response for the .candidates property and add it to the messages list
    if response.candidates:
        for candidate in response.candidates:
            messages_list.append(candidate.content)


    # Print answer to console as well as details if the verbose arg was given
    if response.function_calls:
        for call in response.function_calls:
            function_call_result = call_function(call, verbose_arg)

            call_response = None
            if function_call_result.parts and function_call_result.parts[0].function_response:
                    call_response = function_call_result.parts[0].function_response.response

            if not call_response:
                raise Exception("function_call_result.parts[0].function_response.response is empty")

            if verbose_arg:
                print(f"-> {call_response}")

            # Append the result of the function call to the message list
            messages_list.append(function_call_result)
        if verbose_arg:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    elif response.text:
        print(f"User prompt: {response.text}")
        if verbose_arg:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        break
print("End of the 20 iterations for the AI Agent")
