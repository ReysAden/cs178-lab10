import boto3
from boto3.dynamodb.conditions import Key

# -------------------------------------------------------
# Configuration — update REGION if your table is elsewhere
# -------------------------------------------------------
REGION = "us-east-1"
TABLE_NAME = "Books"

def get_table():
    """Return a reference to the DynamoDB Books table."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    return dynamodb.Table(TABLE_NAME)


def print_book(book):
    title = book.get("Title", "Unknown Title")
    author = book.get("Author", "Unknown Author")
    pages = book.get("Pages", "Unknown Pages")

    print(f"  Title : {title}")
    print(f"  Author: {author}")
    print(f"  Pages : {pages}")
    print()


def get_book_by_title():
    title = input("Enter a book title to search for: ")
    table = get_table()
    
    
    response = table.scan(
        FilterExpression=Key("Title").eq(title)
    )
    items = response.get("Items", [])
    
    if not items:
        print(f"No book found with title '{title}'.")
        return
    
    print(f"Book found:\n")
    print_book(items[0])

def print_all_books():
    """Scan the entire Books table and print each item."""
    table = get_table()
    
    # scan() retrieves ALL items in the table.
    # For large tables you'd use query() instead — but for our small
    # dataset, scan() is fine.
    response = table.scan()
    items = response.get("Items", [])
    
    if not items:
        print("No books found. Make sure your DynamoDB table has data.")
        return
    
    print(f"Found {len(items)} book(s):\n")
    for book in items:
        print_book(book)


def create_book():
    """
    Prompt user for Book Title, Author, Pages.
    Create a new item in the Books table with those attributes.
    """
    title = input("Enter book title: ")
    author = input("Enter book author: ")
    pages = input("Enter book pages: ")
    item = {
        "Title": title,
        "Author": author,
        "Pages": pages,
        "Ratings": []
    }
    table = get_table()
    table.put_item(Item=item)


def update_book_rating():
    """
    Prompt user for a Book Title and a new rating.
    Add that rating to the book's Ratings list in the database.
    """
    title = input("Enter book title to update: ")
    new_rating = input("Enter new rating: ")
    try:
        table = get_table()
        response = table.get_item(Key={"Title": title})
        book = response.get("Item")
        
        if not book:
            print(f"Book '{title}' not found.")
            return
        
        ratings = book.get("Ratings", [])
        ratings.append(new_rating)
        
        table.update_item(
            Key={"Title": title},
            UpdateExpression="SET Ratings = :r",
            ExpressionAttributeValues={":r": ratings}
        )
        print(f"Added rating {new_rating} to book '{title}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


def delete_book():
    """
    Prompt user for a Book Title.
    Delete that item from the database.
    """
    title = input("Enter book title to delete: ")
    try:
        table = get_table()
        response = table.get_item(Key={"Title": title})
        book = response.get("Item")
        
        if not book:
            print(f"Book '{title}' not found.")
            return
        
        table.delete_item(Key={"Title": title})
        print(f"Deleted book '{title}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


def query_book():
    """
    Prompt user for a Book Title.
    Print out the average of all ratings in the book's Ratings list.
    """
    title = input("Enter book title to query: ")
    try:
        table = get_table()
        response = table.get_item(Key={"Title": title})
        book = response.get("Item")
        
        if not book:
            print(f"Book '{title}' not found.")
            return
        
        ratings = book.get("Ratings", [])
        if not ratings:
            print(f"No ratings found for book '{title}'.")
            return
        
        average_rating = sum(map(float, ratings)) / len(ratings)
        print(f"Average rating for '{title}': {average_rating:.2f}")
    except Exception as e:
        print(f"An error occurred: {e}")


def print_menu():
    print("----------------------------")
    print("Press C: to CREATE a new book")
    print("Press R: to READ all books")
    print("Press U: to UPDATE a book (add a review)")
    print("Press D: to DELETE a book")
    print("Press Q: to QUERY a book's average rating")
    print("Press X: to EXIT application")
    print("----------------------------")


def main():
    input_char = ""
    while input_char.upper() != "X":
        print_menu()
        input_char = input("Choice: ")
        if input_char.upper() == "C":
            create_book()
        elif input_char.upper() == "R":
            print("printing all books...")
            print_all_books()
        elif input_char.upper() == "U":
            update_book_rating()
        elif input_char.upper() == "D":
            delete_book()
        elif input_char.upper() == "Q":
            query_book()
        elif input_char.upper() == "X":
            print("exiting...")
        else:
            print("Not a valid option. Try again.")


if __name__ == "__main__":
    main()
