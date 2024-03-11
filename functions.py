from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents.agent_types import AgentType

from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain.agents import initialize_agent, Tool


from dotenv import load_dotenv
import json
import os

from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
class AskCsvsSchema(BaseModel):
    """AskCsvs tool schema."""

    question: str = Field(..., description="User's question")



class AskCsvs(BaseTool):
    args_schema: Type[BaseModel] = AskCsvsSchema
    name: str = "ask_csvs"
    description: str = "Answer to the Tangem(physical crypto wallet company) companies poduct related questions"

    def _run(self, question: str, **kwargs: Any) -> Any:
        answer = ask_csvs(question)
        return answer
    
    # def _arun(self, question: str):
    #     raise NotImplementedError("This tool does not support async")
    

async def ask_csvs(question):
  print(question)
  print('I have been used yoo')
  load_dotenv()
  llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")
  agent = create_csv_agent(llm, 
                           ['csv_files/convertcsv.csv', 'csv_files/ru-blog.csv', 'csv_files/Tangem_AI_articles_Sheet1.csv'], 
                           verbose = True,
                           agent_type=AgentType.OPENAI_FUNCTIONS,)

  return agent.invoke(question + 'If you can not find answer, just say that there is no nay information related to this question')



from openai import OpenAI
import assistant
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#Function to generate the OpenAi response to the Doctors entered information
async def product_response(user_query: str, from_user:str) -> str:
    print('Entered the product response function')
    print(from_user.username)
    assistant_id = assistant.create_assistant()
    response = await assistant.process_thread_with_assistant(user_query=user_query, assistant_id=assistant_id, from_user=from_user)
    print(response)
    return response['text'][0]


  # llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")
  # tools = [AskCsvs()]
  # open_ai_agent = initialize_agent(tools,
  #                       llm,
  #                       agent=AgentType.OPENAI_FUNCTIONS,
  #                       verbose=True)
  # response_message = open_ai_agent.invoke(question)

  # print(response_message)
  # return response_message['output']

    # messages = [
    #       {"role": "system", "content": "You should analyze the user's question and call the function ask_csvs if the question is related to the Tangem company, about Tangem product, crypto wallet, physical card or negative comment about the product. If it does not relate to the provided themes do not call any function and do not reply"},
    #       {"role": "user", "content": question}
    #             ]

    # tools = [
    #     {
    #         "type": "function",
    #         "function": {
    #             "name": "ask_csvs",
    #             "description": "get the answer for the user question in provided csv files",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "question": {
    #                         "type": "string",
    #                         "description": "User's question",
    #                     },
    #                 },
    #                 "required": ["question"],
    #             },
    #         },
    #     }
    # ]
    
    # response = client.chat.completions.create(
    #     model="gpt-4-turbo-preview",  # or choose another model
    #     messages=messages,
    #     tools= tools,
    #     tool_choice="auto",
    # )
    # response_message = response.choices[0].message
    # tool_calls = response_message.tool_calls
    # print(response_message)

    # if tool_calls:
    #     # Step 3: call the function
        
    #     available_functions = {
    #         "ask_csvs": ask_csvs,
    #     }  
    #     messages.append(response_message)  # extend conversation with assistant's reply
    #     # Step 4: send the info for each function call and function response to the model
    #     for tool_call in tool_calls:
    #         function_name = tool_call.function.name
    #         function_to_call = available_functions[function_name]
    #         print(function_to_call)
    #         function_args = json.loads(tool_call.function.arguments)
    #         print(function_args)
    #         # try:
    #         function_response = await function_to_call("name")(
    #         function_args.get("question")
    #             )
    #         print(function_response)
    #         # except Exception as e:
    #         #     return 'Can you ask again and in more understandable way?'
    #         messages.append(
    #             {
    #                 "tool_call_id": tool_call.id,
    #                 "role": "tool",
    #                 "name": function_name,
    #                 "content": function_response,
    #             }
    #         )  # extend conversation with function response
    #         second_response = client.chat.completions.create(
    #         model="gpt-4-turbo-1106",
    #         messages=messages,
    #         )  # get a new response from the model where it can see the function response
    #         print(str(second_response.choices[0].message.content))
    #         return str(second_response.choices[0].message.content)
    
    # return str(response_message.content)
  