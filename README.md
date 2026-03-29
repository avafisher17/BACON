# B.A.C.O.N

The Breadth-first Actor Connection Optimization Network, or B.A.C.O.N, searches a database for the shortest path between a chosen actor and Kevin Bacon.

The program compares three search modes: one comparing strings, one comparing integers from movie and actor ids, and one using a prepopulated graph.



The needed movie database file is included in the repo. Also available is the script to run if you wish to populate your own database using an API Key from [The Movie Database](https://developer.themoviedb.org/docs/getting-started).

## Features

* SQLite Database Integration
* Graph-based actor and movie network
* Set-up file to populate database via API
* Breadth-First Search (BFS) shortest path calculation

## How to Run

1. Install [uv](https://astral.sh/uv)
2. Clone the repo
3. Run "uv sync" to install dependencies
4. Run "uv run python main.py"

\*\*\*NOTE: The first search algorithm can be quite slow - sometimes taking minutes. Rest assured the program is still running and isn't frozen!\*\*\*

## Technologies Used

* Python 3.12.5
* Networkx
* SQLite
* [The Movie Database API](https://developer.themoviedb.org/docs/getting-started)

### Author

Ava Fisher - [@avafisher17](https://github.com/avafisher17)

