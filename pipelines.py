import re
import psycopg2
from datetime import datetime

class CleanMoviePipeline:
    def process_item(self, item, spider):
        # Clean title (remove numeric rank but preserve numbers within the movie title)
        item["title"] = self.remove_numbers(item["title"])

        # Ensure metascores is numeric
        item["metascores"] = int(item["metascores"]) if str(item["metascores"]).isdigit() else None

        # Ensure userscores is numeric
        item["userscores"] = float(item["userscores"]) if item["userscores"] != "tbd" else None

        # Convert release date to YYYY-MM-DD
        item["release_date"] = self.convert_date(item["release_date"])
        return item

    def remove_numbers(self, title):
        """
        Remove leading numbers followed by a '.' but keep numbers that are part of the movie title.
        Example:
        "7,940. Goodrich" -> "Goodrich"
        "1. Dekalog (1988)" -> "Dekalog (1988)"
        """
        return re.sub(r'^\d+[.,\s]+', '', title)

    def convert_date(self, date_str):
        """
        Convert a date string to 'YYYY-MM-DD'.
        Handles both 'Sep 5, 1916' and '2024-10-18'.
        """
        try:
            # First, try to parse the 'MMM DD, YYYY' format
            return datetime.strptime(date_str, "%b %d, %Y").date()
        except ValueError:
            try:
                # Fallback to 'YYYY-MM-DD' format
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"Invalid date format: {date_str}")
                return None
