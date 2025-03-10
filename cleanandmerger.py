#code to clean the titles of the movies
import json
import csv

# Load your JSON data (replace 'iyayi_final.json' with your file name)
with open('iyayi_final.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Function to clean titles and decode Unicode escape sequences
def clean_titles(data):
    for movie in data:
        # Remove numbers and dots before titles
        movie["title"] = movie["title"].split('. ', 1)[-1]
        # Decode Unicode escape sequences
        movie["title"] = movie["title"].encode('utf-8').decode('unicode_escape')
    return data

# Clean the titles
cleaned_data = clean_titles(data)

# Write cleaned data to a CSV file
csv_file_name = 'cleaned_movies.csv'

# Get headers dynamically from the first record
headers = cleaned_data[0].keys()

with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()  # Write the CSV header
    writer.writerows(cleaned_data)  # Write all the cleaned data

print(f"Movies cleaned and saved to '{csv_file_name}'.")


import pandas as pd

def generate_movie_id_from_csv(input_csv, output_csv):
    """
    Read a CSV, merge the release year with the title to create a movie_id,
    and save the updated CSV with proper quoting.

    Args:
    input_csv (str): Path to the input CSV file.
    output_csv (str): Path to save the output CSV file.
"""
    try:
        # Read the input CSV with proper quoting
        df = pd.read_csv(input_csv, quotechar='"')

        # Convert the release_date to datetime and extract the year
        df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year

        # Ensure release_year is an integer, handle missing or invalid dates
        df['release_year'] = df['release_year'].fillna(0).astype(int)

        # Generate the movie_id by appending the year to the title
        df['movie_id'] = df['title'] + df['release_year'].astype(str)

        # Save the updated DataFrame with proper quoting
        df.to_csv(output_csv, index=False, quotechar='"')

        print(f"File saved successfully with movie_id column at {output_csv}")
    except FileNotFoundError:
        print(f"Error: The file {input_csv} was not found.")
    except KeyError as e:
        print(f"Error: Missing column - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Define input and output file paths
    input_file = 'cleaned_movies.csv'  # Replace with your actual input file path
    output_file = 'cleaned_movies_with_ids.csv'  # Output file

    # Call the function to process the file
    generate_movie_id_from_csv(input_file, output_file)

