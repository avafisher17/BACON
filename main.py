import sqlite3
import shutil
import networkx as nx
from collections import deque
import time

# Setting Up Database Connection

try:
    sqliteConnection = sqlite3.connect('bacon.db')
    cursor = sqliteConnection.cursor()

except sqlite3.Error as error:
    print("Whoops, there's an error connecting to our database!", error)

# Setting Up Global Variables

bacon_graph = nx.Graph()
searched_actors = set()
searched_movies = set()
search_queue = deque()

try_again = True

# --------------------------------------------------------------------------------------------------------------------

def print_path(starting_actor, path):
    degrees = (len(path) - 1) / 2

    print(f"\nThis search shows that the actor {starting_actor} can be connected to Kevin Bacon in {int(degrees)} degrees:")
    for i in range(0, len(path) - 2, 2):
        actor1 = path[i]
        movie = path[i + 1]
        actor2 = path[i + 2]
        print(f"{actor1} was in {movie} with {actor2}")


def repeat_prompt():
    answer = input("\nDo you want to try again? Y/N ")

    if answer.lower() in ['y', 'yes']:
        reset_search()
        global try_again
        try_again = True
    else:
        print("\nThank you for using >>> B . A . C . O . N <<")
        try_again = False


def search_1(starting_actor):
    print("Searching", end=' ')
    try:
        search_queue.append(starting_actor)
        while search_queue:
            print(".", end=' ')
            current_actor = search_queue.popleft()
            actor_search_query = "SELECT movie_title FROM movies JOIN movie_actors ON movies.movie_id = movie_actors.movie_id JOIN actors ON actors.actor_id = movie_actors.actor_id WHERE actors.actor_name = ?;"
            cursor.execute(actor_search_query, (current_actor,))
            actor_search_results = cursor.fetchall()
            searched_actors.add(current_actor)
            bacon_graph.add_node(current_actor, type="actor")

            for (movie,) in actor_search_results:
                bacon_graph.add_node(movie, type="movie")
                bacon_graph.add_edge(current_actor, movie)

                if movie not in searched_movies:
                    movie_search_query = "SELECT actors.actor_name FROM movie_actors JOIN movies ON movie_actors.movie_id = movies.movie_id JOIN actors ON movie_actors.actor_id = actors.actor_id WHERE movies.movie_title = ?;"
                    cursor.execute(movie_search_query, (movie,))
                    movie_search_results = cursor.fetchall()
                    searched_movies.add(movie)
                    for (costar,) in movie_search_results:
                        bacon_graph.add_node(costar, type="actor")
                        bacon_graph.add_edge(movie, costar)

                        if costar == "Kevin Bacon":
                            path = nx.shortest_path(bacon_graph, source=starting_actor, target="Kevin Bacon")
                            print_path(starting_actor, path)
                            return

                        if costar not in searched_actors:
                            search_queue.append(costar)
                            searched_actors.add(costar)

        if not search_queue:
            search_stop = time.perf_counter()
            print("\nYou won't believe this...")
            print(f"but in our whole database, we couldn't connect {starting_actor} to Kevin Bacon!")
            print(
                "Maybe our database is too small... or maybe the web of Hollywood isn't as tangled as we're meant to believe.")

    except sqlite3.Error as db_error:
        print("\nUh-oh, there's an error with the database!", db_error)


def search_2(starting_actor):
    print("Searching. . .\n")
    try:
        actor_search_query = "SELECT actor_id FROM actors WHERE actor_name = ?"
        cursor.execute(actor_search_query, (starting_actor,))
        actor_id = cursor.fetchone()
        search_queue.append(actor_id[0])

        kb_search_query = "SELECT actor_id FROM actors WHERE actor_name = 'Kevin Bacon'"
        cursor.execute(kb_search_query)
        kb_search_results = cursor.fetchone()
        kb_id_no = kb_search_results[0]

        while search_queue:
            current_actor = search_queue.popleft()
            actor_search_query = "SELECT movie_id FROM movie_actors WHERE actor_id = ?"
            cursor.execute(actor_search_query, (current_actor,))
            actor_search_results = cursor.fetchall()
            searched_actors.add(current_actor)
            bacon_graph.add_node(current_actor, type="actor")

            for (movie,) in actor_search_results:
                bacon_graph.add_node(movie, type="movie")
                bacon_graph.add_edge(current_actor, movie)

                if movie not in searched_movies:
                    movie_search_query = "SELECT actor_id FROM movie_actors WHERE movie_id = ?"
                    cursor.execute(movie_search_query, (movie,))
                    movie_search_results = cursor.fetchall()
                    searched_movies.add(movie)
                    for (costar,) in movie_search_results:
                        bacon_graph.add_node(costar, type="actor")
                        bacon_graph.add_edge(movie, costar)

                        if costar == kb_id_no:
                            starting_actor_id = actor_id[0]
                            path = nx.shortest_path(bacon_graph, source = starting_actor_id, target = kb_id_no)

                            converted_path = []
                            for i, id_value in enumerate(path):
                                if i % 2 == 0:
                                    cursor.execute("SELECT actor_name FROM actors WHERE actor_id = ?", (id_value,))
                                    name = cursor.fetchone()[0]
                                else:
                                    cursor.execute("SELECT movie_title FROM movies WHERE movie_id = ?", (id_value,))
                                    name = cursor.fetchone()[0]
                                converted_path.append(name)

                            print_path(starting_actor, converted_path)
                            return

                        if costar not in searched_actors:
                            search_queue.append(costar)
                            searched_actors.add(costar)

    except sqlite3.Error as db_error:
        print("\nUh-oh, there's an error with the database!", db_error)


def reset_search():
    global bacon_graph, searched_actors, searched_movies, search_queue
    bacon_graph = nx.Graph()
    searched_actors = set()
    searched_movies = set()
    search_queue = deque()


def main():
    terminal_width = shutil.get_terminal_size().columns

    line_1 = "WELCOME"
    line_2 = "to"
    line_3 = ">>> B . A . C . O . N <<<"
    line_4 = "- or -"
    line_5 = "The Bidirectional Actor Connection Optimization Network"

    print("*" * terminal_width)
    lines = [line_1, line_2, line_3, line_4, line_5]
    for line in lines:
        print(f"{line}".center(terminal_width))
    print("*" * terminal_width)

    print("\nConventional wisdom holds that it takes 6 or less connections to get from any Hollywood actor to Kevin Bacon")
    print("Using a database of 10,000 English-language movies and more than 175,000 actors,")
    print("\tour goal is to find the optimal search method that returns the path from one celebrity to our target\n")
    print("*" * terminal_width)

    print("Let's start with our first search!")
    print("Features:")
    print("\t- indexed SQLite database")
    print("\t- database queries with joins")
    print("\t- queries matching actor name")

    while try_again:
        starting_actor = input("\nWhich actor would you like to search for? ")

        name_check_query = "SELECT actor_name FROM actors WHERE actor_name = ?;"
        cursor.execute(name_check_query, (starting_actor,))
        name_check_results = cursor.fetchall()

        if starting_actor == "Kevin Bacon":
            print("Nice try. Kevin Bacon is Kevin Bacon.")

        elif name_check_results and starting_actor != "Kevin Bacon":
            search_no = 1
            search_start = time.perf_counter()
            search_1(starting_actor)
            search_stop = time.perf_counter()
            search_1_time = search_stop - search_start
            print(f"Search time was {search_1_time:.1f} seconds\n")

            print("*" * terminal_width)

            print("\nNow onto our second search.")
            print("Features:")
            print("\t- indexed SQLite database")
            print("\t- database queries with no joins")
            print("\t- queries matching id numbers")

            reset_search()
            search_start = time.perf_counter()
            search_2(starting_actor)
            search_stop = time.perf_counter()
            search_2_time = search_stop - search_start
            print(f"Search time was {search_2_time:.1f} seconds\n")
            print("***NOTE: This search may have returned different results than the first, simply because actors may have multiple paths to Kevin Bacon***\n")

            print("*" * terminal_width)

            print(f"Search 1 time: {search_1_time:.1f} seconds")
            print(f"Search 2 time: {search_2_time:.1f} seconds")

            if search_2_time > search_1_time:
                print("\nIt seems that Search 1 was faster than Search 2")
                print("That is... honestly unexpected.")
                print("The string comparisons from Search 1 should have required more time than simply comparing integers in the actor and movie ids...")
                print("But technology can just be funny sometimes.")
                repeat_prompt()

            if search_2_time == search_1_time:
                print("\nMy advice to you? Buy a lottery ticket.")
                print("Because you, Dear User, appear to be one of the luckiest people on the planet.")
                print("You have been graced with nearly impossible odds...")
                print("Let's hope such prosperity doesn't end once the program closes!")

            if search_2_time < search_1_time:
                print("\nJust as I suspected!")
                print("Swapping out name strings for movie and actor ids really made a difference in the search speed.")
                print("Honestly, most of the time came from matching up ids with their proper names.")
                print("Clearly storing information as integers is the right way to go when searching!")

                repeat_prompt()

        else:
            print("\nHmm, looks like that actor isn't in our database!")
            print("\nSome tips if you want to try again:")
            print("\t- Check the spelling and capitalization of the name you entered")
            print("\t- Choose an actor who's been in movies recently")
            print("\t- Choose an actor active in Hollywood (or at least in the English-speaking sphere)")
            print("\t- Write, produce, and direct a movie starring the actor of your choice so it can be included in our dataset!")

            repeat_prompt()


if __name__ == "__main__":
    main()