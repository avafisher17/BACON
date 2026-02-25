import sqlite3
import requests
import time

# Setting Up Database Connection

try:
    sqliteConnection = sqlite3.connect('bacon.db')
    cursor = sqliteConnection.cursor()

    setup_movie_table_query = "CREATE TABLE IF NOT EXISTS movies (movie_id INTEGER PRIMARY KEY, movie_title TEXT NOT NULL, release_year INTEGER)"
    cursor.execute(setup_movie_table_query)
    setup_actor_table_query = "CREATE TABLE IF NOT EXISTS actors (actor_id INTEGER PRIMARY KEY, actor_name TEXT NOT NULL)"
    cursor.execute(setup_actor_table_query)
    setup_join_table_query = "CREATE TABLE IF NOT EXISTS movie_actors (movie_id INTEGER, actor_id INTEGER, PRIMARY KEY(movie_id, actor_id), FOREIGN KEY(movie_id) REFERENCES movies(movie_id), FOREIGN KEY(actor_id) REFERENCES actors(actor_id));"
    cursor.execute(setup_join_table_query)

    # Populating Database with Data from The Movie Database API

    API_key = #API Key Redacted

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_key}"
    }

    TOTAL_PAGES = 500
    for page in range(1, TOTAL_PAGES + 1):
        try:
            url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}"

            movie_data = requests.get(url, headers=headers)
            movie_data.raise_for_status()
            fetched_movie_data = movie_data.json()
            movies = fetched_movie_data.get("results", [])

            for movie in movies:
                movie_id = movie["id"]
                title = movie.get("title")
                release_date = movie.get("release_date", "")
                release_year = int(release_date.split("-")[0]) if release_date else None

                cursor.execute("INSERT OR IGNORE INTO movies (movie_id, movie_title, release_year) VALUES (?, ?, ?)",
                               (movie_id, title, release_year))

            sqliteConnection.commit()
            print(f"Added {len(movies)} movies from page {page} of English-language movies.")

            time.sleep(0.25)

        except requests.RequestException as error:
            print(f"Error fetching page {page} - ", error)

    cursor.execute("SELECT movie_id FROM movies")
    movie_ids = [row[0] for row in cursor.fetchall()]

    for movie_id in movie_ids:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
        try:
            actor_data = requests.get(url, headers=headers)
            actor_data.raise_for_status()
            fetched_actor_data = actor_data.json()
            cast = fetched_actor_data.get("cast", [])

            for actor in cast:
                actor_id = actor["id"]
                actor_name = actor["name"]

                cursor.execute("INSERT OR IGNORE INTO actors (actor_id, actor_name) VALUES (?, ?)", (actor_id, actor_name))
                cursor.execute("INSERT OR IGNORE INTO movie_actors (movie_id, actor_id) VALUES (?, ?)", (movie_id, actor_id))

            sqliteConnection.commit()
            print(f"Cast of movie {movie_id} added to database.")

            time.sleep(0.25)

        except requests.RequestException as error:
            print(f"Error fetching movie {movie_id} credits - ", error)
            continue

    print("\nDatabase fully populated!")
    sqliteConnection.close()

except sqlite3.Error as error:
    print("An error occured - ", error)




