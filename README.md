# B.A.C.O.N

The Bidirectional Actor Connection Optimization Network, or B.A.C.O.N, searches a database for the shortest path between a chosen actor and Kevin Bacon.

The program compares two search modes: one comparing strings, and the other comparing integers from movie and actor ids.

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



\*\*\*NOTE: The first search algorithm can be quite slow - sometimes taking minutes.\*\*\*

\*\*\*Rest assured the program is still running and isn't frozen!\*\*\*

## Technologies Used

* Python 3.12.5
* Networkx
* SQLite
* The Movie Database API

### Author

Ava Fisher - [@avafisher17](https://github.com/avafisher17)

