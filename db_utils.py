"""
Code Written by Pat Hall
Last updated: 11.21.23
"""
import data_utils as du
import pandas as pd
import os
import sqlite3 as sql
import psycopg as pg
import re
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient


"""
SQLITE TOOLS
"""

DB_NAME = 'default.sqlite'
DEFAULT_PATH = os.path.join(os.path.dirname(__file__),DB_NAME)

#sets DEFAULT_PATH to desired path. specifically used for sqlite.
def set_DEFAULT_PATH(db_name = None,db_loc = None):
    global DEFAULT_PATH
    pattern = r'\.(sqlite|db)$'

    if db_name == None:
        print(f"Path is set to: {str(DEFAULT_PATH)}")
        return
    
    else:
        while True:
            if re.search(pattern,db_name) == None:
                print("error: db_name must end with '.sqlite' or .db")
                db_name = input("enter a new name for you Database: ")

            else:
                break

        if db_loc is None:
            DEFAULT_PATH = os.path.join(os.path.dirname(__file__),db_name)

        else:
            DEFAULT_PATH = (db_loc + '/' + db_name)

    print(f"Path is set to: {str(DEFAULT_PATH)}")

#connects to sqlite db
def connect_to_sqlite():
    connection = sql.connect(DEFAULT_PATH)
    return connection

#formats list of dictonaries for insertion into a sqlite db
def prepare_dict(list_of_dicts):
    list_of_tuples = [tuple(value for value in record.values()) for record in list_of_dicts] #syntax for this line is adapted from chatGPT
    return list_of_tuples

"""
POSTGRESQL TOOLS
"""

#Creates a a new table using column headers from a csv.
def create_table_columns_from_csv(csv_file_path,schema,new_table_name,delim=';'):
    load_dotenv()
    dbname = os.environ.get('DB_NAME')
    user = os.environ.get("USER")
    password = os.environ.get("PASSWORD")

    # Create a connection + cursor to the PostgreSQL database
    cur,conn = initiate_pg_cursor(dbname,user,password) #connects to db and creates cursor object

    # Path to your large CSV file
    csv_file_path = '/Users/pathall/Library/CloudStorage/OneDrive-TheUniversityofColoradoDenver/GEOG 5050 - Spatial Stats/Final_Project/Data/Staging/airbnb-listings.csv'


    df = pd.read_csv(csv_file_path, sep=delim, nrows=1)  # Read only the first row to get column names
    column_names = df.columns.tolist()
    corrected_column_names = du.replace_spaces_in_list(column_names)

    print(corrected_column_names)
    print(len(corrected_column_names))

    # Generate the SQL table creation statement
    sql_statement = f"CREATE TABLE {schema}.{new_table_name} ({', '.join([f'{col} VARCHAR' for col in corrected_column_names])});"

    # Execute the SQL statement to create the table
    cur.execute(sql_statement)
    conn.commit()
    conn.close()

    print(f'Table "{schema}.{table_name}" has been created in the database.')

#Initiates a connection and cursor for local postgreSQL session
def initiate_pg_cursor(dbname,user,password):

    #could be made more secure by making username and password an environmental variable. 
    #Need more time to figure that one out.
    try:
        connection = pg.connect(f"dbname={dbname} user={user} password={password}")

    except:
        print("error: connection not valid. Try changing connection parameter.")

    cursor = connection.cursor()

    return cursor,connection

"""
MONGODB TOOLS
"""

#adapted from MongoDB documentation.
def get_client():
    load_dotenv()

    db_psswd = os.environ.get('MONGO_PASSWORD')
    db_user = os.environ.get('MONGO_USER')
    db_name = os.environ.get('MONGO_NAME')

    uri = f"mongodb+srv://{db_user}:{db_psswd}@{db_name}.rx0xn5a.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print(f"You successfully connected to {db_name} uri")
        return client
    except Exception as e:
        print(e)