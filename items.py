import scrapy

class MetacriticItem(scrapy.Item):
    # Define the fields for your item
    title = scrapy.Field()           # Movie title
    release_date = scrapy.Field()    # Movie release date
    userscores = scrapy.Field()      # Movie rating
    genre = scrapy.Field()           # Movie genre
    metascores = scrapy.Field()      # Movie metascores
    movie_url = scrapy.Field()       # URL of the movie details page