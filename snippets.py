import logging
import argparse
import sys
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect("dbname='snippets' user='ubuntu' password='thinkful' host='localhost'")
logging.debug("Database connection established")

def put(name, snippet, hide=False):
  """
    Store a snippet with an associated name.
    Returns the name and the snippet
  """
  logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
  
  with connection, connection.cursor() as cursor:
    try:
      cursor.execute("insert into snippets values (%s,%s,%s)", (name, snippet, hide))
    except psycopg2.IntegrityError:
      connection.rollback()
      cursor.execute("update snippets set message=%s, hidden=%s where keyword=%s", (snippet, name, hide))
      connection.commit()
  
  logging.debug("Snippet stored successfully.")
  return name, snippet

def get(snippet):
  """
    Retrieve the snippet with a given name.
    If there is no such snippet...
    Returns the snippet.
  """
  logging.info("Retrieving snippet {!r}".format(snippet))
  
  with connection, connection.cursor() as cursor:
    cursor.execute("select message from snippets where keyword=%s", (snippet,))
    row = cursor.fetchone()

  if row: return row[0]
  else: print "No row with this snippet: {}".format(snippet)
  
  logging.debug("Snippet retrieved successfully")

def delete(name):
  """
    Retrieve the snippet with a given name
    Delete the snippet
  """
  logging.info("Deleting record from database.")
  
  with connection, connection.cursor() as cursor:
    cursor.execute("delete from snippets where keyword=%s", (name,))
    
  logging.debug("Record deleted from database.")
  return name
  
def catalog():
  """
    Retrieve all the keywords in the snippets db
  """
  logging.info("Retrieving all the keywords.")

  with connection, connection.cursor() as cursor:
    cursor.execute("select keyword from snippets where hidden=False order by keyword ASC")
    rows = cursor.fetchall()
  
    for row in rows: 
      print row[0]
    
  logging.debug("All keywords retrieved successfully")
  
def search(string):
  """
  """
  logging.info("Searching a snippet")
  
  with connection, connection.cursor() as cursor:
    cursor.execute("select * from snippets where message like '%%' ||%s|| '%% and hidden=False'", (string,))
    rows = cursor.fetchall()
    
    for row in rows:
      print row[0]
      
  logging.debug("Searching complete")

def main():
  """Main function"""
  logging.info("Constructing parser")
  parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

  subparsers = parser.add_subparsers(dest="command", help="Available commands")

  # Subparser for the put command
  logging.debug("Constructing put subparser")
  put_parser = subparsers.add_parser("put", help="Store a snippet")
  put_parser.add_argument("name", help="The name of the snippet")
  put_parser.add_argument("snippet", help="The snippet text")
  put_parser.add_argument("--hide", help="Sets the hidden column to True", action="store_true")

  # Subparser for the get command
  logging.debug("Constructing get subparser")
  get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
  get_parser.add_argument("snippet", help="The snippet text")
  
  # Subparser for the catalog command
  logging.debug("Constructing catalog subparser")
  subparsers.add_parser("catalog", help="Retrieves all keywords in snippets")
  
  # Subparser for the search command
  logging.debug("Constructing search subparser")
  search_parser = subparsers.add_parser("search", help="Searches the database for specified string")
  search_parser.add_argument("string", help="The string that will be used to search the database")
  
  # Subparser for the delete command
  logging.debug("Constructing put subparser")
  delete_parser = subparsers.add_parser("delete", help="Delete a snippet")
  delete_parser.add_argument("name", help="The name of the snippet")

  arguments = parser.parse_args(sys.argv[1:])

  # Convert parsed arguments from Namespace to dictionary
  arguments = vars(arguments)
  command = arguments.pop("command")
  
  if command == "put":
    name, snippet = put(**arguments)
    print("Stored {!r} as {!r}".format(snippet, name))
  elif command == "get":
    snippet = get(**arguments)
    print("Retrieved snippet: {!r}".format(snippet))
  elif command == 'catalog':
    catalog()
    print("Query finished successfully")
  elif command == 'search':
    search(**arguments)
    print("Search complete for string: {!r}".format(sys.argv[2]))
  elif command == 'delete':
    delete(**arguments)
    print("Deleted snippet: {!r}".format(sys.argv[2]))

if __name__ == "__main__":
  main()