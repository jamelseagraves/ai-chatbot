import argparse
import traceback
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Get the top 'n' most similar documents using the KNN <=> operator
def get_top_related_docs(query_embedding, cur, n):
    embedding_array = np.array(query_embedding)
    cur.execute("SELECT content FROM embeddings ORDER BY embedding <=> %s LIMIT %s", (embedding_array, n,))
    return cur.fetchall()

def execute_main():
    # Set up args parser and retrieve args from command line
    parser = argparse.ArgumentParser(description="""
                                    This is a Q & A chatbot.\n
                                    You can ask questions about various topics and receive an answer.
                                    """)
    parser.add_argument('dbname', help='Name of Postgres database')
    args = parser.parse_args()

    conn = psycopg2.connect(dbname=args.dbname)
    register_vector(conn)

    cur = conn.cursor()

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    qa_model = pipeline("question-answering", "distilbert-base-cased-distilled-squad")

    prompt = "You can type 'quit' at anytime to stop.\nPlease ask a question: "

    query = input("Greetings! I am a cool new chatbot. " + prompt)

    while query != "quit":
        if len(query.split()) >= 64:
            print("Sorry, your question must be less than 64 words.\n" + prompt)
            continue
        try:
            embedding = model.encode(query, normalize_embeddings=True)
            top_doc = get_top_related_docs(embedding, cur, 1)
            response = qa_model(question = query, context = top_doc[0][0], max_answer_len = 128, max_seq_len = 512)
            answer = response["answer"].capitalize()
            print("\n" + answer + "\n")
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            break
        
        query = input(prompt)

    print("\n=====================================\n")
    print("Thanks for chatting with me. Goodbye!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    execute_main()
