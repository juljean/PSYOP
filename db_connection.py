import psycopg2
import config
import logging
import constants
import psycopg2.extras as extras
from psycopg2.extras import LoggingConnection

# setting debug  to True
logging.basicConfig(level=logging.DEBUG)
#referencing  the logger information
logger = logging.getLogger("loggerinformation")


def execute_values(conn, df, table):
    """
    Custom data insertion from dataframe
    :param conn: PostgreSQL connection object
    :param df: pandas dataframe pointer. DF has same names and order of column names as SQL table
    :param table: str, SQL table name
    :return:
    """
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))

    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("Dataframe is inserted")
    cursor.close()


def select_operation(conn):
    cur = conn.cursor()
    result_dict = {}
    cur.execute(constants.QUERY_SELECT_QUEUE_ENTITIES)
    row = cur.fetchone()
    while row is not None:
        result_dict[row[0]] = row[1]
        row = cur.fetchone()
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()
    conn.close()
    return result_dict


def delete_operation(conn, channel_link):
    cur = conn.cursor()
    cur.execute(constants.QUERY_DELETE_QUEUE_ENTITIES, (channel_link,))
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()
    conn.close()


def connect(df=None, table_name=None, operation_name="insert", channel_link=None):
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host="localhost",
            database="PSYOPanalyzer",
            user="postgres",
            password=config.DB_PASSWORD,
            connection_factory=LoggingConnection)

        # intializing the logging of the PostgreSQL database inserted data
        conn.initialize(logger)

        # create a cursor
        cur = conn.cursor()
        if operation_name == "insert":
            execute_values(conn, df, table_name)
        if operation_name == "select":
            result_dict = select_operation(conn)
            return result_dict
        if operation_name == "delete":
            delete_operation(conn, channel_link)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

