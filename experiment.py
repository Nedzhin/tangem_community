
from langchain_community.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
import os
from dotenv import load_dotenv

# key = os.getenv('OPENAI_API_KEY')
# print(key)
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
load_dotenv()
loader_1 = CSVLoader(file_path='csv_files/convertcsv.csv')
loader_2 = CSVLoader(file_path = 'csv_files/ru-blog.csv')
loader_3 = CSVLoader(file_path = 'csv_files/Tangem_AI_articles_Sheet1.csv')
index_creator = VectorstoreIndexCreator()
docsearch = index_creator.from_loaders([loader_1, loader_2, loader_3])
chain = RetrievalQA.from_chain_type( llm=OpenAI(api_key = os.getenv('OPENAI_API_KEY')), chain_type="stuff", retriever= docsearch.vectorstore.as_retriever(), input_key="question" )

async def ask_csvs(question):
# Pass a query to the chain
  query = question
  response = chain({"question": query})

  return response['result']

#print(response['result'])