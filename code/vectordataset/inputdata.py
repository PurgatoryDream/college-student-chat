import datetime
import openai
import tiktoken
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Constants:
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_ENCODING = "cl100k_base"
max_tokens = 400

# Check the length of a tokenized text:
def checkLength(text):
    tokenizer = tiktoken.get_encoding(EMBEDDING_ENCODING)
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

# Generate the text splitter:
splitter = RecursiveCharacterTextSplitter(
    chunk_size=max_tokens,
    chunk_overlap=20,
    length_function=checkLength,
    separators=["\n\n", "\n", " ", ""]
)

# Put the data from the transcripts into a data object:
def loadDataObject(filename, text, author = "Unknown.", date = datetime.date.today().strftime("%B %d, %Y"), source = "Unknown."):
    textChunks = splitter.split_text(text)
    data = []
    data.extend([{
        'filename': filename,
        'text': chunk,
        'author': author,
        'date': date,
        'source': source
    } for chunk in textChunks])
    return data

# Print the data object:
def printDataObject(data):
    print(f"Filename: {data['filename']}")
    print(f"Text: {data['text']}")
    print(f"Author: {data['author']}")
    print(f"Date: {data['date']}")
    print(f"Source: {data['source']}")
    print("\n")

# Get the embedding of a data object:
def get_embedding_data(data, model=EMBEDDING_MODEL):
    text = data['text']
    text = text.replace("\n", " ")
    filename = ".".join(data["filename"].split(".")[:-1])
    input_text = " || ".join([filename, data["author"], data["date"], data["source"], text])
    
    # Get the embedding, waiting if it fails to avoid the rate limit:
    try:
        res = openai.Embedding.create(input=input_text, model=model)['data'][0]['embedding']
    except:
        done = False
        while not done:
            time.sleep(5)
            try:
                res = openai.Embedding.create(input=input_text, model=model)['data'][0]['embedding']
                done = True
            except:
                pass

    return res