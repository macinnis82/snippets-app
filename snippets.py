import logging
import argparse
import sys
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect("dbname='snippets' user='ubuntu' password='thinkful' host='localhost'")
logging.debug("Database connection established")

def put(name, snippet):
  """
    Store a snippet with an associated name.
    Returns the name and the snippet
  """
  logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
  cursor = connection.cursor()
  try:
    command = "insert into snippets values (%s,%s)"
    cursor.execute(command, (name, snippet))
  except psycopg2.IntegrityError as e:
    connection.rollback()
    command = "update snippets set message=%s where keyword=%s"
    cursor.execute(command, (snippet, name))
  connection.commit()
  logging.debug("Snippet stored successfully.")
  return name, snippet

def get(snippet):
  """
    Retrieve the snippet with a given name.
    If there is no such snippet...
    Returns the snippet.
  """
  logging.debug("Retrieving snippet {!r}".format(snippet))
  
  cursor = connection.cursor()
  command = "select keyword, message from snippets where keyword = %s"
  snippet_tuple = (snippet,)
  cursor.execute(command, snippet_tuple)
  row = cursor.fetchone()
  connection.commit()

  logging.debug("Snippet retrieved successfully")

  if row:
    print "keyword = {}".format(row[0])
    print "message = {}".format(row[1])
  else:
    print "No row with this snippet: {}".format(snippet)
    
  return snippet

def delete(name):
  """
    Retrieve the snippet with a given name
    Delete the snippet
  """
  logging.error("FIXME: Unimplemented - delete({!r})".format(name))

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

  # Subparser for the get command
  logging.debug("Constructing get subparser")
  get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
  get_parser.add_argument("snippet", help="The snipper text")

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

if __name__ == "__main__":
  main()