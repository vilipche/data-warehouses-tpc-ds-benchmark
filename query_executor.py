import psycopg2
import csv
from os.path import join


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


def parse_times_from_query_result(query_result):
    planning_time_str = query_result[-2][0]
    planning_time_str = planning_time_str.strip("Planning time: ").strip(" ms")
    planning_time = float(planning_time_str)

    execution_time_str = query_result[-1][0]
    execution_time_str = execution_time_str.strip("Execution Time: ").strip(" ms")
    execution_time = float(execution_time_str)

    overall_time = planning_time + execution_time

    return planning_time, execution_time, overall_time


def write_execution_times(file_path, times_list):
    with open(file_path, 'a+') as file:
        writer = csv.writer(file)
        writer.writerow(times_list)


if __name__ == '__main__':
    # TODO change the values of this dict according to the database params
    DB_PARAMS = {
        "host": "localhost",
        "database": "database",
        "user": "username", #TODO don't commit
        "password": "password",
        "port": "5432"
    }

    SCALE_FACTOR = 1                            # TODO set this scale factor to 1, 2, 4 or 8
    QUERY_DIRECTORY = f"queries/queries_{SCALE_FACTOR}"
    QUERIES_FILE_PATH = join(QUERY_DIRECTORY, "queries.sql")
    QUERY_NR_OF_EXECUTIONS = 6                  # TODO set this value to the number of times each query will be executed
    PLN_TIME_CSV_PATH = join(QUERY_DIRECTORY, "planning_times.csv")
    EXC_TIME_CSV_PATH = join(QUERY_DIRECTORY, "execution_times.csv")
    OVR_TIME_CSV_PATH = join(QUERY_DIRECTORY, "overall_times.csv")

    queries = parse_queries_from(QUERIES_FILE_PATH)

    connection = open_postgresql_connection(DB_PARAMS)
    cursor = connection.cursor()

    for query in queries:
        query = decorate_query_for_statistics(query)
        planning_times = list()
        execution_times = list()
        overall_times = list()

        for _ in range(QUERY_NR_OF_EXECUTIONS):
            cursor.execute(query)
            planning_time, execution_time, overall_time = parse_times_from_query_result(cursor.fetchall())
            planning_times.append(planning_time)
            execution_times.append(execution_time)
            overall_times.append(overall_time)

        write_execution_times(PLN_TIME_CSV_PATH, planning_times)
        write_execution_times(EXC_TIME_CSV_PATH, execution_times)
        write_execution_times(OVR_TIME_CSV_PATH, overall_times)

    cursor.close()
    connection.close()
