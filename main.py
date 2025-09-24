import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types


# Get the prompt from the args list
try:
    user_prompt = sys.argv[1]
except IndexError:
    print("Error: no prompt given!")
    sys.exit(1)

# Check if the verbose arg was given
verbose_arg = False
if (len(sys.argv) == 3 and (sys.argv[2] == "--verbose" or sys.argv[2] == "-v")):
    verbose_arg = True

# Load env variables and api key
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# List to store roles and messages for the AI Agent
messages_list = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)])
]

# Make the API call
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages_list,
)

# Print answer to console as well as details if the verbose arg was given
if verbose_arg:
    print(f"User prompt: {response.text}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
else:
    print(response.text)