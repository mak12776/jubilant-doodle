import csv
import random
import sys

from util import Node
from collections import deque, namedtuple

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """

    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    # default = person_id_for_name(input("Name: "))
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def input_person_id() -> int:
    string = input('Name (empty for random name):')
    if not string:
        return random.choice(list(people.keys()))
    return person_id_for_name(string)

def format_movie(movie_id: int) -> str:
    movie = movies[movie_id]
    return f"{movie_id}: {movie['title']}, {movie['year']}"

def format_person(person_id: int) -> str:
    person = people[person_id]
    return f'{person_id}: {person["name"]}, {person["birth"]}'

def shortest_path(source: int, target: int) -> list[tuple[int, int]] | None:
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    print(f'source: {format_person(source)}')
    print(f'target: {format_person(target)}')

    if source == target:
        return []

    queue: deque[Node] = deque()

    for neighbor in neighbors_for_person(source):
        # neighbor = (movie_id, person_id)
        if neighbor[1] == source:
            continue
        elif neighbor[1] == target:
            return [neighbor]
        else:
            queue.append(Node(neighbor[1], None, neighbor[0]))

    while queue:
        node = queue.popleft()
        for neighbor in neighbors_for_person(node.state):
            # neighbor = (movie_id, person_id)
            if neighbor[1] == node.state:
                continue
            elif neighbor[1] == target:

                result = [neighbor, (node.action, node.state)]
                while node.parent is not None:
                    node = node.parent
                    result.append((node.action, node.state))
                result.reverse()

                return result
            else:
                queue.append(Node(neighbor[1], node, neighbor[0]))

    return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id) -> set[tuple[int, int]]:
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
