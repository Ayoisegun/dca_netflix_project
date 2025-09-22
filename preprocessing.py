import pandas as pd
import os
import psycopg2
from psycopg2 import OperationalError
import time

input_path = os.environ["INPUT_PATH"]
output_path = os.environ["OUTPUT_PATH"]

print("Starting preprocessing script...")
print(f"Input path: {input_path}")
print(f"Output path: {output_path}")


def preprocessingdf(input_path, output_path):

    movie_review = pd.read_csv(input_path)
    print("Reading CSV file...")
    original_rows = len(movie_review)
    dupes = movie_review.duplicated().sum()
    movie_review = movie_review.drop_duplicates(subset=['title', 'director', 'release_year'])

    movie_review["date_added"] = pd.to_datetime(movie_review["date_added"], errors= 'coerce')
    today = pd.Timestamp.today().normalize()
    movie_review = movie_review[movie_review['date_added'] <= today]

    real_category = ['G', 'NC-17', 'NR', 'PG', 'PG-13', 'R',
       'TV-14', 'TV-G', 'TV-MA', 'TV-PG', 'TV-Y', 'TV-Y7', 'TV-Y7-FV', 'UR']
    mask = (~movie_review['rating'].isin(real_category)) & (movie_review['duration'].isna())
    movie_review.loc[mask, 'duration'] = movie_review.loc[mask, 'rating']
    movie_review.loc[~movie_review['rating'].isin(real_category), "rating"] = pd.NA
    movie_review = movie_review[movie_review['rating'].isin(real_category)]

    movie_review["type"] = movie_review['type'].astype("string")
    movie_review = movie_review.dropna(subset=["rating"]).reset_index(drop=True)
    movie_review = movie_review.dropna(subset=["title"]).reset_index(drop=True)
    movie_review['director'] = movie_review['director'].fillna('Unknown')
    movie_review['country'] = movie_review['country'].fillna('Unknown')
    movie_review['cast'] = movie_review['cast'].fillna('Unknown')
    movie_review['date_added'] = movie_review['date_added'].fillna(pd.NaT)

    movie_review['title'] = movie_review['title'].str.strip().str.title()
    movie_review['director'] = movie_review['director'].str.strip().str.title()
    movie_review['description'] = movie_review['description'].str.strip().str.lower()
    movie_review['cast'] = movie_review['cast'].str.strip()

    category = {'G': 'children', 'TV-Y':'children', 'TV-Y7': 'children', 'PG' : 'children', 'PG-13' : 'teenage', 'TV-PG': 'teenage', 'TV-14': 'teenage', 'TV-G' : 'children', 'TV-Y7-FV' : 'children', 'TV-14': 'teenage', 'R': 'adult', 'NC-17' : 'adult', 'TV-MA' : 'adult', 'NR' : 'Not Rated', 'UR' : 'Unrated' }
    movie_review['rating_category'] = movie_review['rating'].map(category)

    print("Saving cleaned CSV...")    
    movie_review.to_csv(output_path, index = False)
    print("✅ CSV saved successfully!")


def sql_insertion(output_path):
    print("Starting database insertion...")
    
    conn = None
    for i in range(10):  # Retry 10 times
        try:
            print(f"Connection attempt {i+1}/10...")
            conn = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT')
            )
            print("✅ Database connection successful!")
            break  
        except OperationalError:
            print("✅ Database connection successful!")
            time.sleep(2)  # Wait 2 seconds before retrying
    
    if conn is None:
        raise Exception("Could not connect to PostgreSQL after multiple attempts")

    cur = conn.cursor()

    # Load cleaned CSV
    df = pd.read_csv(output_path)
    cur.execute("TRUNCATE TABLE movies;")

    # Insert rows into table
    for _, row in df.iterrows():
        values = (
            row['show_id'],
            row['type'],              
            row['title'],
            row['director'],
            row['cast'],              
            row['country'],
            row['date_added'],
            row['release_year'],
            row['rating'],
            row['duration'],
            row['listed_in'],
            row['description'],
            row['rating_category']
        )
        
        cur.execute("""
            INSERT INTO movies (show_id, movie_type, title, director, cast_members, country, date_added, release_year, rating, duration, listed_in, description, rating_category)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, values)

    # Commit and close
    conn.commit()
    cur.close()
    conn.close()

    print("✅ Data inserted into database!")


if __name__ == "__main__":
    print("Starting main execution...")
    
    cleaned_file = preprocessingdf(input_path, output_path)
    print(f"✅ Preprocessing complete. Cleaned file: {output_path}")
    
    print("Calling SQL insertion function...")
    sql_insertion(output_path)
    print("All done! Database insertion completed.")