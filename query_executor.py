import psycopg2
import csv


def open_postgresql_connection(db_params):
    """ Connect to the PostgreSQL database server and return the cursor for executing statements """
    conn = None
    try:
        conn = psycopg2.connect(**db_params)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return conn


def parse_queries_from(query_file_path):
    """ Parse all queries from the query file"""
    with open(query_file_path, 'r') as f:
        content = f.read()
    queries = [query.strip()+";" for query in content.split(";")][:-1]
    return queries


def decorate_query_for_statistics(query):
    """ Decorate the query in order to collects statistics about the statement execution """
    return "EXPLAIN ANALYZE " + query


def parse_execution_time_from_query_result(query_result):
    execution_time_str = query_result[-1][0]
    execution_time_str = execution_time_str.strip("Execution Time: ").strip(" ms")
    return float(execution_time_str)


def write_execution_times(file_path, execution_times):
    with open(file_path, 'a+') as file:
        writer = csv.writer(file)
        writer.writerow(execution_times)


if __name__ == '__main__':
    # TODO change the values of this dict according to the database params
    DB_PARAMS = {
        "host": "localhost",
        "database": "database",
        "user": "username",
        "password": "password",
        "port": "5432"
    }

    QUERIES_FILE_PATH = "query_0.sql"           # TODO set this path to the file containing the queries
    QUERY_NR_OF_EXECUTIONS = 6                  # TODO set this value to the number of times each query will be executed
    TIMES_FILE_PATH = "execution_times.csv"

    queries = parse_queries_from(QUERIES_FILE_PATH)

    connection = open_postgresql_connection(DB_PARAMS)
    cursor = connection.cursor()

    for query in queries:
        query = decorate_query_for_statistics(query)
        execution_times = list()

        for _ in range(QUERY_NR_OF_EXECUTIONS):
            cursor.execute(query)
            execution_time = parse_execution_time_from_query_result(cursor.fetchall())
            execution_times.append(execution_time)

        write_execution_times(TIMES_FILE_PATH, execution_times)

    cursor.close()
    connection.close()
