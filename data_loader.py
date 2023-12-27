import argparse
import data_retriever
import glob
import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

DATASET_DIR = "./datasets/wikimedia"

def set_up_database(conn, cur):
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

    create_table_command = """
    CREATE TABLE IF NOT EXISTS embeddings (
        id bigserial primary key,
        title text,
        url text,
        content text,
        tokens integer,
        embedding vector(384)
    );
    """
    create_index_command = """
    CREATE INDEX IF NOT EXISTS embedding_idx
    ON embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
    """
    cur.execute(create_table_command)
    # Creating this embedding index significantly speeds up queries on very large datasets
    cur.execute(create_index_command)
    conn.commit()

# Chunk the data file, generate embeddings, and insert into the database
def process_file_and_insert(filepath: str, model, cur):
    # Load parquet file into a dataframe
    df = pd.read_parquet(filepath, engine="pyarrow")

    # Split the content each row into chunked documents to generate embeddings
    # and store in the vector database
    for index, row in df.iterrows():
        content = row["text"]
        title = row["title"]
        print(title)
        url = row["url"]
        words = content.split()
        num_words = 512 # limit number of tokens (words) in each document
        overlap = 32 # overlap helps prevent context loss when sentences are split during chunking
        docs = []
        chunks = [words[i:i+num_words] for i in range(0, len(words)-5, num_words-overlap)]
        for chunk in chunks:
            doc = " ".join(chunk)
            # Generate vector embedding using the pretrained model
            embedding = model.encode(doc, normalize_embeddings=True)
            docs.append((title, url, doc, len(chunk), np.array(embedding)))
        
        # Use execute_values to perform batch insertion
        execute_values(cur, "INSERT INTO embeddings (title, url, content, tokens, embedding) VALUES %s", docs)

        # Remove/Comment this if- block to process all dataframe rows (>100K rows) and insert into the DB
        # Leaving this here for now to limit processing on local machine
        if (index == len(df.index)-1 or index == 9):
            break

def execute_main():
    # Set up args parser and retrieve args from command line
    parser = argparse.ArgumentParser(description="""
                                    This script performs the following steps:\n
                                    1) downloads parquet files from HuggingFace to the 'datasets/wikimedia' directory\n
                                    1) loads parquet files from the 'datasets/wikimedia' directory,\n
                                    2) chunks the content of each record,\n
                                    3) generates embeddings for each text chunk, and\n
                                    4) batch inserts new rows into the vector database
                                    """)
    parser.add_argument('dbname', help='Name of Postgres database')
    args = parser.parse_args()

    # Initialize the pretrained model to generate vector embeddings
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Initialize database connection and set up vector database
    conn = psycopg2.connect(dbname=args.dbname)
    cur = conn.cursor()
    set_up_database(conn, cur)
    register_vector(conn)

    # Download the dataset
    data_retriever.download_dataset(DATASET_DIR)

    parquet_files = glob.glob(DATASET_DIR + "/*.parquet")

    for filepath in parquet_files:
        process_file_and_insert(filepath, model, cur)

        conn.commit()

    cur.execute("SELECT COUNT(*) as cnt FROM embeddings;")
    num_records = cur.fetchone()[0]
    print("\nNumber of vector records in table: ", num_records,"\n")
    cur.close()
    conn.close()

if __name__ == "__main__":
    execute_main()
