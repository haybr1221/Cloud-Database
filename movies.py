import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

try: 
    cred = credentials.Certificate("movies.json")
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Error intializing Firebase: {e}")
    exit()

# Set a variable as the database
db = firestore.client()


def view_data(choice=0):
    """
    View the data in the database.

    Parameters: 
        choice: the choice of the user on which view to use. Set to 0 for
            default to allow the use during update/delete statements
    Return: nothing
    """
    if choice == 0:
        # Choose which view to see
        print("\nWhat collection would you like to view?")
        print("     1. Movie")
        print("     2. Actors")
        print("     3. Movies and actors")
        choice = int(input("Select an option from above: "))

    if choice == 1:
        # View movies
        collection = db.collection("movies")
        result = collection.get()
        print()
        print("-" * 10)
        for record in result:
            data = record.to_dict()
            print(f"{data['title']} - {data['year']}")
        print("-" * 10)

    elif choice == 2:
        # View actors
        collection = db.collection("actors")
        result = collection.get()
        print()
        print("-" * 10)
        for record in result:
            data = record.to_dict()
            print(f"{data['name']}")
        print("-" * 10)

    elif choice == 3:
        # View which movies have which actors
        collection = db.collection("movie_has_actor")
        result = collection.get()
        print()

        for record in result:
            # Get the data as a dictionary 
            data = record.to_dict()
            
            # Pull the data to assign it to a print statement
            role = data['role']
            movie_id = data['movieId']
            actor_id = data['actorId']

            # Get the specific movie information to display
            movie_doc = db.collection("movies").document(movie_id).get()

            if movie_doc.exists:
                movie_data = movie_doc.to_dict()
                movie_title = movie_data['title']
                movie_year = movie_data['year']
                print(f"{movie_title} - {movie_year}")
            else:
                print("\nThe movie requested does not exists.")
            
            # Get the specific actor information
            actor_doc = db.collection("actors").document(actor_id).get()

            if actor_doc.exists:
                actor_data = actor_doc.to_dict()
                print(f"   - {actor_data['name']} ({role})")
            else:
                print("\nThe actor requested does not exist.")
    else:
        print("Invalid option.")


def add_new():
    """
    Add new data to the database.

    Parameters: none
    Return: nothing
    """
    print("\nWhat would you like to add?")
    print("     1. New movie")
    print("     2. New actor")
    print("     3. New actor in movie")
    choice = int(input("Select an option from above: "))

    if choice == 1:
        name = input("\nEnter the name of the film: ")
        year = int(input("Enter the year the film was released: "))
        db.collection("movies").document().set({"title" : name, "year": year})
    elif choice == 2:
        name = input("Enter the name of the actor: ")
        db.collection("actors").document().set({"name": name})
    elif choice == 3:
        view_data(1)
        movie_str = input("What movie would you like to add an actor for? ")
        view_data(2)
        actor_str = input("What actor would you like to add? ")
        role = input(f"What was {actor_str}'s role in {movie_str}? ")

        movie_id = get_id("movies", movie_str, "title")
        actor_id = get_id("actors", actor_str, "name")

        db.collection("movie_has_actor").document().set({"movieId": movie_id, "actorId": actor_id, "role": role})


def update():
    """
    Update existing data in the database.

    Parameters: none
    Return: nothing
    """
    print("\nWhat would you like to update?")
    print("     1. Movies")
    print("     2. Actors")
    print("     3. An actor's role in a movie")
    choice = int(input("Select an option from above: "))

    if choice == 1:
        # Display the data for the user to see
        view_data(1)

        # Set the collection
        collection = db.collection("movies")

        # Ask the user what they would like to update
        update_doc = input("Which movie would you like to update? ")

        # Find which movie they would like to update
        query = collection.where(filter=FieldFilter("title", "==", update_doc))
        query_results = query.get()

        if query_results:
            doc_id = query_results[0].id

        # TODO: make this optional, if enter is pressed assume it is the same
        new_title = input("\nEnter the new film title: ")
        new_year = int(input("Enter the new release year: "))

        collection.document(doc_id).set({"title": new_title, "year": new_year})
        print("\nMovie updated successfully.")

    elif choice == 2:
        # Display the data for the user to see
        view_data(2)

        # Set the collection to make updating easier
        collection = db.collection("actors")

        # Ask the user what they would like to update
        update_doc = input("\nWhich actor would you like to update? ")
        query = collection.where(filter=FieldFilter("name", "==", update_doc))
        query_results = query.get()

        for doc in query_results:
            unique_id = doc.id

        new_name = input(("\nEnter the new name: "))

        collection.document(unique_id).set({"name": new_name})
        print("\nActor updated successfully.")

    elif choice == 3:
        # Display the data for the user to see
        view_data(3)

        # Set the collection to make updating easier
        collection = db.collection("movie_has_actor")

        # Ask the user what they would like to update
        movie_str = input("\nWhat movie would you like to update an actor's role in? ")
        actor_str = input(f"What actor from {movie_str} would you like to update? ")

        movie_id = get_id("movies", movie_str, "title")
        actor_id = get_id("actors", actor_str, "name")

        query = get_query(actor_id, movie_id)

        if query:
            unique_id = query[0].id

        # TODO: make this optional
        new_role = input(("\nEnter the new role: "))

        collection.document(unique_id).set({"actorId": actor_id, "movieId": movie_id, "role": new_role})
        print("\nRole successfully updated.")


def delete():
    """
    Delete data from the database

    Parameters: none
    Returns: nothing
    """
    print("\nWhat would you like to delete?")
    print("     1. A movie")
    print("     2. An actor")
    print("     3. An actor from a movie")
    choice = int(input("Select an option from above: "))

    if choice == 1:
        # Display the data for the user to see
        view_data(1)

        # Set the collection to make deleting easier
        collection = db.collection("movies")

        # Ask the user what they would like to delete
        movie = input("\nWhich movie would you like to delete? ")
        query = collection.where(filter=FieldFilter("title", "==", movie)).get()

    elif choice == 2:
        # Display the data for the user to see
        view_data(2)

        # Set the collection to make deleting easier
        collection = db.collection("actors")

        # Ask the user what they would like to delete
        actor = input("\nWhich actor would you like to delete? ")
        query = collection.where(filter=FieldFilter("name", "==", actor)).get()
    
    elif choice == 3:
        # Display the data for the user to see
        view_data(3)

        # Set the collection to make deleting easier
        collection = db.collection("movie_has_actor")

        movie_str = input("\nWhat movie would you like to remove an actor from? ")
        actor_str = input("What actor would you like to remove? ")

        movie_id = get_id("movies", movie_str, "title")
        actor_id = get_id("actors", actor_str, "name")

        query = get_query(actor_id, movie_id)
        
    if query:
        unique_id = query[0].id

    collection.document(unique_id).delete()
    print("\nSuccessfully deleted.")


def get_id(collection, string, field):
    """
    Search for the ID when a string is used for the user

    Parameters:
        collection: the collection to use
        string: the text to search for within the collection
        field: the field to match with the string
    Returns:
        the id for the requested item
    """
    query = db.collection(f"{collection}").where(f"{field}", "==", string).get()

    if query:
        id = query[0].id
        return id
    else:
        print(f"{string} is not in the database.")


def get_query(actor_id, movie_id):
    """
    Get the query request for the movie_has_actor table

    Parameters:
        actor_id: the id of the actor
        movie_id: the id of the movie
    Returns:
        query
    """
    collection = db.collection("move_has_actor")
    return collection.where(filter=FieldFilter("actorId", "==", actor_id)).where(filter=FieldFilter("movieId", "==", movie_id)).get()


def main():
    """
    The main function of the program.
    """
    while True: 
        print("\nWhat would you like to do?")
        print("     1. View data")
        print("     2. Add new data")
        print("     3. Update data")
        print("     4. Remove data")
        print("     5. Exit")
        choice = int(input("Select an option from above: "))

        if choice == 1:
            view_data()
        elif choice == 2:
            add_new()
        elif choice == 3:
            update()
        elif choice == 4:
            delete()
        elif choice == 5:
            break
        else:
            print("Not a valid option")


if __name__ == '__main__':
    main()