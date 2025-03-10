import csv
import psycopg2

class SaveToPostgres:
    DB_CONFIG = {
        "dbname": "ODMiyayi",
        "user": "postgres",
        "password": "12345",
        "host": "localhost",
        "port": "5433"
    }

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(**self.DB_CONFIG)
        self.cursor = self.conn.cursor()
        print("Connected to PostgreSQL successfully!")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")

    def insert_item(self, item):
        sql_query = """
        INSERT INTO movies (title, metascores, userscores, movie_url, rated, genre, release_date, movie_id, release_year)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            userscores = (
                float(item["userscores"]) if item["userscores"] and item["userscores"].replace('.', '', 1).isdigit() else None
            )

            self.cursor.execute(
                sql_query,
                (
                    item["title"],
                    int(item["metascores"]),
                    userscores,
                    item["movie_url"],
                    item["rated"],
                    item["genre"],
                    item["release_date"],
                    item["movie_id"],
                    int(item["release_year"])
                )
            )
            self.conn.commit()
            print(f"Item inserted: {item['title']}")

        except psycopg2.Error as db_err:
            self.conn.rollback()
            print(f"Database error for item {item['title']}: {db_err}")
        except ValueError as ve:
            print(f"Invalid data for item {item['title']}: {ve}")
        except Exception as e:
            self.conn.rollback()
            print(f"Unexpected error for item {item['title']}: {e}")

if __name__ == "__main__":
    csv_file_path = 'cleaned_movies_with_ids.csv'
    movies = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movies.append(row)

    postgres = SaveToPostgres()
    postgres.connect()

    for movie in movies:
        postgres.insert_item(movie)

    postgres.close()