from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import os

#import assistant

load_dotenv()
router = Router()

bot = Bot(os.getenv("BOT_TOKEN"))

@router.message(Command("start"))
async def command_start(message: Message, state: FSMContext) -> None:
  await message.answer(
f"""  Hello {message.from_user.first_name}! I am Tangem bot. I am here to help you with the any question regarding to the Tangem. There is the functionalities you can do with the bot:
                      
1. Ask any question regarding to the Tangem wallet
2. You can send your question to the support team email in the bot. (you should  tell the bot to send the message to support team and write your question)

If bot could not find the answer, it automatically sends the question to the support team and notifies you about it!
                       
P.S. If bot says that can send your question to the support team. Repeat the question and say to send the message to support team""")



# from openai import OpenAI
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

from functions import  product_response
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@router.message()
async def message_handle(message: Message, state: FSMContext):
  messages = [{"role": "system", "content": """You should analyze the question and classify them.  To classify the questions and comments from users into four distinct categories: Tangem-related questions or negative feedback, inappropriate language or hostility between users, and spam messages (such as repeated questions or get-rich-quick schemes unrelated to Tangem), general conversation between people, follow these guidelines:

1. **Tangem-related Questions or Negative Feedback:**
   - Identify if the content is directly related to Tangem products, services, or customer experiences. Look for specific mentions of Tangem, its products (e.g., Tangem Wallet, Tangem Note), or services.
   - Detect any negative sentiment or criticism about Tangem or its products. This may include complaints, dissatisfaction, or issues users have encountered.
   - It can be any questions or negative comments about cryptocurrency general

2. **Inappropriate Language or Hostility Between Users:**
   - Scout for the use of explicit language, insults, or any form of harassment between users. This can include offensive words, aggressive tones, or demeaning statements.

3. **Spam Messages:**
   - Look for messages that are irrelevant to Tangem and its discussions, such as advertisement links, get-rich-quick schemes, or repeated questions/comments without significant variation.
   - Detect patterns of repetitive posting that contribute to noise rather than meaningful conversation.

4. **General Conversation:**
    - Look for general conversation sentences between users. Replying each other greetings and so on. If it not question and not the spam and bad word then categorize the sentence to this group.
               
Use these criteria to accurately categorize each question or comment. If a message fits multiple categories, prioritize the classification based on the most dominant aspect of its content. Reply 'Product' or 'Bad' or 'Spam' or 'General', regarding to three classes"""}, {"role": "user", "content": message.text}]
  response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,  # auto is default, but we'll be explicit
    )
  response_condition = response.choices[0].message
  print(response_condition)
  print(message.text)
  if response_condition.content == 'Product':
    response_message = await product_response(message.text, message.from_user)
    #response_message = await ask_csvs(message.text)
    #await message.answer(response_message['output'] )
    #print(message.from_user.chat_id)
    await message.reply('your question is related to the product')
    await message.reply(response_message)
  elif response_condition.content == 'Bad':
    await message.answer('Talk in good manner')
  elif response_condition.content == 'Spam':
    await message.answer('your question is not related to the Tangem')
  elif response_condition.content == 'General':
    await message.answer('this is a general sentence')
  # question = message.text

  # response_message = await generate_openai_response(question)

  # await message.answer(str(response_message))

  # user_data = await state.get_data()
  # if user_data.get('not_customer'):
  #   return
  # else:
  #   #await send_email(message.text, message.from_user.username)
  #   #await message.answer("You query has sent to the support team")
  #   user_query = message.text
  #   from_user = message.from_user
  #   print(from_user.username)
  #   assistant_id = assistant.create_assistant()
  #   response = await assistant.process_thread_with_assistant(user_query=user_query, assistant_id=assistant_id, from_user=from_user)
  #   print(response)
  #   await message.answer(response['text'][0])


