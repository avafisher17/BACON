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

try_again = True

# --------------------------------------------------------------------------------------------------------------------

class Timer:
    def __init__(self):
        self.start_time = None
        self.elapsed = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.perf_counter()
            self.running = True

    def stop(self):
        if self.running:
            self.elapsed = time.perf_counter() - self.start_time
            self.running = False

    def reset(self):
        self.start_time = None
        self.elapsed = 0
        self.running = False

    def elapsed_time(self):
        if not self.running:
            return self.elapsed


class Graph:
    def __init__(self):
        self.graph = nx.Graph()
        self.searched_actors = set()
        self.searched_movies = set()
        self.search_queue = deque()
        self.actor_id = None

    def reset_search(self):
        self.graph = nx.Graph()
        self.searched_actors.clear()
        self.searched_movies.clear()
        self.search_queue.clear()
        #retains actor id

    def get_actor_id(self, starting_actor):
        try:
            actor_search_query = "SELECT actor_id FROM actors WHERE actor_name = ?"
            cursor.execute(actor_search_query, (starting_actor,))
            actor_id_results = cursor.fetchone()
            self.actor_id = actor_id_results[0]

        except sqlite3.Error as db_error:
            print("\nUh-oh, there's an error with the database!")
            print(db_error)

    def convert_path(self, path):
        # Convert id numbers in path to names and titles
        converted_path = []
        for i, id_value in enumerate(path):
            if i % 2 == 0:
                cursor.execute("SELECT actor_name FROM actors WHERE actor_id = ?",
                               (id_value,))
                name = cursor.fetchone()[0]
            else:
                cursor.execute("SELECT movie_title FROM movies WHERE movie_id = ?",
                               (id_value,))
                name = cursor.fetchone()[0]
            converted_path.append(name)

        return converted_path

    def get_kb_id_no(self):
        # Fetch actor_id of Kevin Bacon
        kb_search_query = "SELECT actor_id FROM actors WHERE actor_name = 'Kevin Bacon'"
        cursor.execute(kb_search_query)
        kb_search_results = cursor.fetchone()
        kb_id_no = kb_search_results[0]
        return kb_id_no

    def string_search(self, starting_actor):
        self.get_actor_id(starting_actor)
        try:
            self.search_queue.append(starting_actor)
            # Find movies the selected actor has been in
            while self.search_queue:
                current_actor = self.search_queue.popleft()
                actor_search_query = "SELECT movie_title FROM movies JOIN movie_actors ON movies.movie_id = movie_actors.movie_id JOIN actors ON actors.actor_id = movie_actors.actor_id WHERE actors.actor_name = ?;"
                cursor.execute(actor_search_query, (current_actor,))
                actor_search_results = cursor.fetchall()
                self.searched_actors.add(current_actor)
                self.graph.add_node(current_actor, type="actor")

                for (movie,) in actor_search_results:
                    self.graph.add_node(movie, type="movie")
                    self.graph.add_edge(current_actor, movie)

                    # Find co-stars among filmography
                    if movie not in self.searched_movies:
                        movie_search_query = "SELECT actors.actor_name FROM movie_actors JOIN movies ON movie_actors.movie_id = movies.movie_id JOIN actors ON movie_actors.actor_id = actors.actor_id WHERE movies.movie_title = ?;"
                        cursor.execute(movie_search_query, (movie,))
                        movie_search_results = cursor.fetchall()
                        self.searched_movies.add(movie)
                        for (costar,) in movie_search_results:
                            self.graph.add_node(costar, type="actor")
                            self.graph.add_edge(movie, costar)

                            if costar == "Kevin Bacon":
                                path = nx.shortest_path(self.graph, source=starting_actor, target="Kevin Bacon")
                                return path

                            if costar not in self.searched_actors:
                                self.search_queue.append(costar)
                                self.searched_actors.add(costar)

            # If all connections have been exhausted:
            if not self.search_queue:
                print("\nYou won't believe this...")
                print(f"but in our whole database, we couldn't connect {starting_actor} to Kevin Bacon!")
                print(
                    "Maybe our database is too small... or maybe the web of Hollywood isn't as tangled as we're meant to believe.")

                path = None
                return path

        except sqlite3.Error as db_error:
            print("\nUh-oh, there's an error with the database!")
            print(db_error)

    def id_search(self):
        if self.actor_id == None:
            print("Uh-oh, this actor's id number hasn't been assigned!\n")
            path = None
            return path

        try:
            self.search_queue.append(self.actor_id)
            kb_id_no = self.get_kb_id_no()

            # Find movies the selected actor has been in
            while self.search_queue:
                current_actor = self.search_queue.popleft()
                actor_search_query = "SELECT movie_id FROM movie_actors WHERE actor_id = ?"
                cursor.execute(actor_search_query, (current_actor,))
                actor_search_results = cursor.fetchall()
                self.searched_actors.add(current_actor)
                self.graph.add_node(current_actor, type="actor")

                for (movie,) in actor_search_results:
                    self.graph.add_node(movie, type="movie")
                    self.graph.add_edge(current_actor, movie)

                    # Find co-stars among filmography
                    if movie not in self.searched_movies:
                        movie_search_query = "SELECT actor_id FROM movie_actors WHERE movie_id = ?"
                        cursor.execute(movie_search_query, (movie,))
                        movie_search_results = cursor.fetchall()
                        self.searched_movies.add(movie)
                        for (costar,) in movie_search_results:
                            self.graph.add_node(costar, type="actor")
                            self.graph.add_edge(movie, costar)

                            if costar == kb_id_no:
                                path = nx.shortest_path(self.graph, source=self.actor_id, target=kb_id_no)
                                converted_path = self.convert_path(path)
                                return converted_path

                            if costar not in self.searched_actors:
                                self.search_queue.append(costar)
                                self.searched_actors.add(costar)

        except sqlite3.Error as db_error:
            print("\nUh-oh, there's an error with the database!")
            print(db_error)

    def graph_search(self):
        cursor.execute("SELECT actor_id, movie_id FROM movie_actors")
        all_edges = cursor.fetchall()
        for actor_id, movie_id in all_edges:
            self.graph.add_node(actor_id, type="actor")
            self.graph.add_node(movie_id, type="movie")
            self.graph.add_edge(actor_id, movie_id)

        kb_id_no = self.get_kb_id_no()
        for path in nx.all_shortest_paths(self.graph, source=self.actor_id, target=kb_id_no):
            #Tests paths for id no.s that may not be in db; if a node is missing, it goes to the next possible path
            try:
                converted_path = self.convert_path(path)
                return converted_path
            except TypeError:
                continue

    def get_node_count(self):
        actors_created = []
        movies_created = []
        for node, data_type in self.graph.nodes(data=True):
            node_type = data_type.get("type")
            if node_type == "actor":
                actors_created.append(node)
            elif node_type == "movie":
                movies_created.append(node)
        return len(actors_created), len(movies_created)


def print_path(starting_actor, path):
    degrees = (len(path) - 1) / 2
    print(f"\nThis search shows that the actor {starting_actor} can be connected to Kevin Bacon in {int(degrees)} degrees:\n")
    for i in range(0, len(path) - 2, 2):
        actor1 = path[i]
        movie = path[i + 1]
        actor2 = path[i + 2]
        print(f"{actor1} was in {movie} with {actor2}")


def repeat_prompt():
    answer = input("\nDo you want to try again? Y/N ")

    if answer.lower() in ['y', 'yes']:
        global try_again
        try_again = True
    else:
        print("\nThank you for using >>> B . A . C . O . N <<")
        try_again = False


def main():
    terminal_width = shutil.get_terminal_size().columns

    line_1 = "WELCOME"
    line_2 = "to"
    line_3 = ">>> B . A . C . O . N <<<"
    line_4 = "- or -"
    line_5 = "The Breadth-first Actor Connection Optimization Network"

    print("*" * terminal_width)
    lines = [line_1, line_2, line_3, line_4, line_5]
    for line in lines:
        print(f"{line}".center(terminal_width))
    print("*" * terminal_width)

    print("\nThey say it takes 6 or less connections to get from any Hollywood actor to Kevin Bacon")
    print("Using a database of 10,000 English-language movies and more than 175,000 actors,")
    print("\tour goal is to find the optimal search method that returns the path from one celebrity to another\n")
    input("PRESS ANY KEY TO BEGIN\n")
    print("*" * terminal_width)

    print("\nLet's start with our first search - string comparisons!")
    print("Features:")
    print("\t- indexed SQLite database")
    print("\t- database queries with joins")
    print("\t- queries matching actor name")
    print("\n***NOTE: Please be prepared for a search time of up to several minutes")
    print("\t(try 'Dolly Parton' or 'Ice Cube' if you're in a time-crunch!)***")

    while try_again:
        timer = Timer()
        graph = Graph()

        starting_actor = input("\nWhich actor would you like to search for? ")

        # Check to see if the actor is usable/in the database
        name_check_query = "SELECT actor_name FROM actors WHERE actor_name = ?;"
        cursor.execute(name_check_query, (starting_actor,))
        name_check_results = cursor.fetchall()

        if starting_actor == "Kevin Bacon":
            print("\nNice try. Kevin Bacon is Kevin Bacon.")

        elif name_check_results and starting_actor != "Kevin Bacon":
            timer.start()
            print("\nSearching . . .")
            path1 = graph.string_search(starting_actor)
            timer.stop()
            search_1_time = timer.elapsed_time()
            if path1:
                print_path(starting_actor, path1)
                print(f"\nSearch time was {search_1_time:.3f} seconds\n")
                actor_count_1, movie_count_1 = graph.get_node_count()

                input("PRESS ANY KEY TO GO TO THE NEXT SEARCH\n")
                graph.reset_search()
                timer.reset()

                print("*" * terminal_width)

                print("\nThis search is a little different than the last one. It compares integers rather than strings.")
                print("Features:")
                print("\t- indexed SQLite database")
                print("\t- database queries with no joins")
                print("\t- queries matching id numbers")
                print("\n***NOTE: Results may be different from the previous search, simply because some actors have multiple connections to Kevin Bacon.***\n")

                input("PRESS ANY KEY TO BEGIN THE SEARCH\n")

                timer.start()
                print("Searching . . .")
                path2 = graph.id_search()
                timer.stop()
                search_2_time = timer.elapsed_time()
                if path2:

                    print_path(starting_actor, path2)
                    print(f"\nSearch time was {search_2_time:.3f} seconds")
                    actor_count_2, movie_count_2 = graph.get_node_count()

                    input("PRESS ANY KEY TO GO TO THE NEXT SEARCH\n")
                    graph.reset_search()
                    timer.reset()

                    print("Our last search uses a different approach than the other two.")
                    print("Instead of searching as we go, we'll search a prepopulated graph of the entire database.")
                    print("Features:")
                    print("\t- graph prepopulated from indexed SQLite database")
                    print("\t- BFS for matching id numbers")
                    print("\nThis search should look through all possible paths and combinations.\n")

                    input("PRESS ANY KEY TO BEGIN THE SEARCH\n")

                    timer.start()
                    print("Searching . . .")
                    path3 = graph.graph_search()
                    timer.stop()
                    search_3_time = timer.elapsed_time()
                    print_path(starting_actor, path2)
                    print(f"\nSearch time was {search_3_time:.3f} seconds")
                    actor_count_3, movie_count_3 = graph.get_node_count()

                    input("\nPress any key to examine the results of all three searches\n")

                    print("*" * terminal_width)

                    print(f"\nSearch 1 time: {search_1_time:.3f} seconds")
                    print(f"This algorithm searched through {actor_count_1:,} actors and {movie_count_1:,} movies before it found its desired results.\n")

                    print(f"Search 2 time: {search_2_time:.3f} seconds")
                    print(f"This algorithm searched through {actor_count_2:,} actors and {movie_count_2:,} movies before it found its desired results.\n")

                    print(f"Search 3 time: {search_3_time:.3f} seconds")
                    print(f"This algorithm searched through {actor_count_3:,} actors and {movie_count_3:,} movies before it found its desired results.\n")

                    searches = ["the first search comparing strings", "the second search comparing id numbers", "the third search using the prepopulated graph"]
                    search_times = [search_1_time, search_2_time, search_3_time]
                    actor_counts = [actor_count_1, actor_count_2, actor_count_3]
                    movie_counts = [movie_count_1, movie_count_2, movie_count_3]
                    item_counts = []
                    average_time_per_item = []
                    for i in range(len(searches)):
                        items_searched = actor_counts[i] + movie_counts[i]
                        item_counts.append(items_searched)
                        average = search_times[i] / items_searched
                        average_time_per_item.append(average)

                    print(f"> The fastest search algorithm was {searches[search_times.index(min(search_times))]} with {min(search_times):.3f} seconds.")
                    print(f"> The search algorithm that searched the most items was {searches[item_counts.index(max(item_counts))]},")
                    print(f"\twith {max(item_counts):,} movies and actors searched. This means it was the most thorough.")
                    print(f"> A disqualifying factor for {searches[0]} is that name collisions are possible between actors or movies that share names.")
                    print("\tIf you had a first search that appeared inconsistent with the other searches' results, that may be why.")
                    print(f"> The search that had the best average time per item searched was {searches[average_time_per_item.index(min(average_time_per_item))]},")
                    print(f"\tmeaning it offered the best trade-off between speed and breadth.")

                    print(f"\n>>>OVERALL BEST SEARCH: {searches[average_time_per_item.index(min(average_time_per_item))]}<<<\n")

                    repeat_prompt()

                else:
                    repeat_prompt()

            else:
                print("\nYou won't believe this...")
                print(f"but in our whole database, we couldn't connect {starting_actor} to Kevin Bacon!")
                print("Maybe our database is too small... or maybe the web of Hollywood isn't as tangled as we're meant to believe.")

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