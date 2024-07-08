import openai
import time
import tiktoken

# Constants:
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_ENCODING = "cl100k_base"
max_tokens = 400
primer = f"""You are a teacher who wants to show a student how to learn about a certain topic.
You will be given information above the question the student asks, and your task is to help the student understand the topic at hand.
You also want to provide the student with questions about the class or the topic to cover, along with possible routes with which they
can expand their knowledge if necessary. You can only use the information provided in this context, and you cannot use any other information.

If what you are asked about is not in the context provided, you should tell the student that you do not know about the topic, and give them other ways to investigate it."""

# Get the embedding of a data object:
def get_embedding_query(query, model=EMBEDDING_MODEL):
    query = query.replace("\n", " ")

    # Get the embedding, waiting if it fails to avoid the rate limit:
    try:
        res = openai.Embedding.create(input=query, model=model)['data'][0]['embedding']
    except:
        done = False
        while not done:
            time.sleep(5)
            try:
                res = openai.Embedding.create(input=query, model=model)['data'][0]['embedding']
                done = True
            except:
                pass

    return res

# Answer a question using the database:
def answer_question_database(data, query):
    contexts = [item['text'] for item in data]
    data_query = "\n\n----\n\n".join(contexts) + "\n\n----\n\n" + query

    # Make the request:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": primer},
            {"role": "system", "content": data_query}
        ]
    )

    # Get the response:
    response_text = response['choices'][0]['message']['content']
    return response_text

# Answer a question using only the query:
def answer_question_query(query):
    # Make the request:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens=max_tokens * 2,
        messages=[
            {"role": "system", "content": primer},
            {"role": "system", "content": query}
        ]
    )

    # Get the response:
    response_text = response['choices'][0]['message']['content']
    return response_text