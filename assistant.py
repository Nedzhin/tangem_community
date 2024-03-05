import os
import json
import openai
from time import sleep
from dotenv import load_dotenv, dotenv_values, set_key
import io  # Import for in-memory file handling
from datetime import datetime
from aiogram import  Bot
import csv
from message import send_email
from functions import ask_csvs
# Load your OpenAI API key from the .env file

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

bot = Bot(os.getenv("BOT_TOKEN"))

import json

# def read_json_file(filename):
#     with open(filename, 'r') as file:
#         data = json.load(file)
#     return data

# # Function to save a dictionary to a JSON file
# def save_to_json_file(data, filename):
#     with open(filename, 'w') as file:
#         json.dump(data, file, indent=4)

# def csv_to_json(csv_file_path, json_file_path):
#     data = []
#     with open(csv_file_path, 'r') as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#         for row in csv_reader:
#             data.append(row)
    
#     with open(json_file_path, 'w') as json_file:
#         json.dump(data, json_file, indent=4)


async def execute_function(function_name, arguments, from_user):
    """
    Execute a function based on the function name and provided arguments.
    """
    username = from_user
    if function_name == 'send_email':
        try:
            await send_email( arguments['user_question'], username)
            message = "Message have sent to support team"
        except IndexError:
            message = "Could not send message to support team. Can you try again or directly write message to them"
        return {'message': message}
    elif function_name == 'ask_csvs':
        print('entered to there')
        try:
            message = await ask_csvs( arguments['question'])
        except IndexError:
            message = "Could not enter the function and find the answer. Can you try again or directly write message to them"
        return {'message': message}
    else:
        return "Function not recognized"

async def process_thread_with_assistant(user_query, assistant_id, from_user, model="gpt-4-turbo-preview",):
    """
    Process a thread with an assistant and handle the response which includes text and images.

    :param user_query: The user's query.
    :param assistant_id: The ID of the assistant to be used.
    :param model: The model version of the assistant.
    :param from_user: The user ID from whom the query originated.
    :return: A dictionary containing text responses and in-memory file objects.
    """
    response_texts = []  # List to store text responses
    response_files = []  # List to store file IDs
    in_memory_files = []  # List to store in-memory file objects
  
    try:
        print("Creating a thread for the user query...")
        
        
        thread = openai.Client().beta.threads.create()
           
            

     
        
        #print(thread)
        # save_to_json_file(database_file, 'data.json')
        print("Adding the user query as a message to the thread...")
        # print(openai.Client().beta.assistants.retrieve(assistant_id).file_ids)
        # file_id_1 = openai.Client().beta.assistants.retrieve(assistant_id).file_ids[0]
        # file_id_2 = openai.Client().beta.assistants.retrieve(assistant_id).file_ids[1]
        # file_id_3 = openai.Client().beta.assistants.retrieve(assistant_id).file_ids[2]
        # print([file_id_1, file_id_2, file_id_3])

        openai.Client().beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_query
            #file_ids=[file_id_1, file_id_2, file_id_3]
        )
        print("User query added to the thread.")

        print("Creating a run to process the thread with the assistant...")
        run = openai.Client().beta.threads.runs.create(
            thread_id= thread.id,
            assistant_id = assistant_id,
            model=model
        )
        if not run:
            print("waiting....")
            

        print(f"Run created with ID: {run.id}")

        while True:
            print("Checking the status of the run...")
            run_status = openai.Client().beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"Current status of the run: {run_status.status}")
            if run_status.status == 'in_progress':
                await bot.send_chat_action(chat_id=from_user.id, action='typing')

            if run_status.status == "requires_action":
                print("Run requires action. Executing specified function...")
                tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                print(function_name)
                print(arguments)
                function_output = await execute_function(function_name, arguments, from_user.username)
                function_output_str = json.dumps(function_output)

                print("Submitting tool outputs...")
                openai.Client().beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": function_output_str
                    }]
                )
                print("Tool outputs submitted.",function_name, function_output_str)

            elif run_status.status in ["completed", "failed", "cancelled"]:
                print("Fetching messages added by the assistant...")
                messages = openai.Client().beta.threads.messages.list(thread_id=thread.id)
                print(messages)
                print(len(messages.data))
                for message in messages.data:
                    if message.role == "assistant":
                        for content in message.content:
                            if content.type == "text":
                                response_texts.append(content.text.value)
                            elif content.type == "image_file":
                                file_id = content.image_file.file_id
                                response_files.append(file_id)

                print("Messages fetched. Retrieving content for each file ID...")
                for file_id in response_files:
                    try:
                        print(f"Retrieving content for file ID: {file_id}")
                        # Retrieve file content from OpenAI API
                        file_response = openai.Client().files.content(file_id)
                        if hasattr(file_response, 'content'):
                            # If the response has a 'content' attribute, use it as binary content
                            file_content = file_response.content
                        else:
                            # Otherwise, use the response directly
                            file_content = file_response

                        in_memory_file = io.BytesIO(file_content)
                        in_memory_files.append(in_memory_file)
                        print(f"In-memory file object created for file ID: {file_id}")
                    except Exception as e:
                        print(f"Failed to retrieve content for file ID: {file_id}. Error: {e}")

                break
            sleep(1)

        return {"text": response_texts, "in_memory_files": in_memory_files}

    except Exception as e:
        print(f"An error occurred: {e}")
        await bot.send_message(chat_id=from_user.id, text= "Try again! There is some errors")
        return {"text": [], "in_memory_files": []}

# Example usage
def create_assistant():
  #assistant_file_path = 'assistant.json'

  # If there is an assistant.json file, load the assistant
#   if os.path.exists(assistant_file_path):
#     with open(assistant_file_path, 'r') as file:
#       assistant_data = json.load(file)
#       assistant_id = assistant_data['assistant_id']
#       print("Loaded existing assistant ID.")
  env_path = ".env"

    # Load existing environment variables
  env_vars = dotenv_values(env_path)
  assistant_id = env_vars["assistant_id"]
  print(assistant_id)
  if assistant_id != "":
      #assistant_id = os.getenv('assistant_id')
      print("Loaded existing assistant ID.")
      return assistant_id
  else:
    # Create file
    # csv_to_json('csv_files/convertcsv.csv', 'json_files/convertcsv.json')
    # csv_to_json('csv_files/ru-blog.csv', 'json_files/ru-blog.json')
    # csv_to_json('csv_files/Tangem_AI_articles_Sheet1.csv', 'json_files/Tangem_AI_articles_Sheet1.json')

    print("loading the ids of the assistant")
    with open("csv_files/convertcsv.csv", 'rb') as file:
        file = openai.Client().files.create(file=file, purpose='assistants')
        file_id_1 = file.id
    
    with open("csv_files/ru-blog.csv", 'rb') as file:
        file = openai.Client().files.create(file=file, purpose='assistants')
        file_id_2 = file.id
    
    with open("csv_files/Tangem_AI_articles_Sheet1.csv", 'rb') as file:
        file = openai.Client().files.create(file=file, purpose='assistants')
        file_id_3 = file.id

    print([file_id_1, file_id_2, file_id_3])
    # Create the assistant
    assistant = openai.Client().beta.assistants.create(
        instructions= "You are the Tangem community assistant chatbot in crypto wallet questions which have access to the telegram group. You have access to the ask_csvs and send_email functions. You should analyze user's question and should identify which function to call. If user asks the question or statement is about Tangem product then call the ask_csvs function anf retrieve the answer. If you do not get answer for the user question from the ask_csvs function or user asks to send the question to support team then call sen_email function. Answer politely, faster, shortly and understandable way. The answer speed is the main thing.",
        model="gpt-4-turbo-preview",
        tools=[
         {
            "type": "function",
            "function": {
                "name": "ask_csvs",
                "description": "get the answer for the user question in provided csv files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "User's question",
                        },
                    },
                    "required": ["question"],
                },
            },
        },
        {"type": "function",
            "function": {   
                "name": "send_email",
                "description": "sends the not answered question to the support team",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_question": {
                            "type": "string",
                            "description": "Users question to the bot"
                        },
                        "username": {
                            "type": "string",
                            "description": "Telegram username of the user."
                        }
                    },
                    "required": ["user_question"]
                }
            }
        }
        ]

    )
        # Assuming file_ids is defined elsewhere in your code

    # Print the assistant ID or any other details you need
    print(f"Assistant ID: {assistant.id}")

    # Create a assistant.json file to save OpenAI costs
    # with open(assistant_file_path, 'w') as file:
    #   json.dump({'assistant_id': assistant.id}, file)
    
    # Update the specific key-value pair
    env_vars['assistant_id'] = f"{assistant.id}"

    # Write the updated environment variables back to the .env file
    set_key(env_path, 'assistant_id', f"{assistant.id}")
    print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id

# user_query = "Hi"
# assistant_id = create_assistant()
# from_user_id = "nurekendei"
# response = process_thread_with_assistant(user_query, assistant_id, from_user=from_user_id)
# print("Final response:", response)

