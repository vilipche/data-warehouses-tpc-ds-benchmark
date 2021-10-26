import csv
import matplotlib.pyplot as plt
import numpy as np

# TODO we can change the filename to plot only planning or only execution time
RESULT_FILE_PATH = "{}GB_6-times_result/overall_times.csv"
SCALE_FACTORS = [1, 2, 4, 8]
COLORS = ['blue', 'green', 'red', 'yellow']


def get_querynb_to_avgtime():
    # skipping the first time before computing the mean
    querynb_to_times = get_querynb_to_times()
    return {querynb: sum(times[1:]) / len(times[1:]) for querynb, times in querynb_to_times.items()}


def get_querynb_to_times():
    querynb_to_times = dict()

    with open(result_file_path) as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            # skipping rows that have less than 6 values for time
            if '' in row:
                continue

            # querynb is the first number in the row (replace operation for queries like "24_1" or "24_2")
            querynb = row.pop(0).replace("_", ".")

            row = [float(el) for el in row]
            assert len(row) == 6    # 6 execution time
            querynb_to_times[querynb] = row

    return querynb_to_times


def get_completely_executed_queries(scalefactor_to_querynb_to_avgtime):
    """Return the ordered list of the queries that are completely executed with all the scale factors"""
    sets = [set(scalefactor_to_querynb_to_avgtime[scalefactor].keys())
            for scalefactor in scalefactor_to_querynb_to_avgtime.keys()]
    return sorted(list(set.intersection(*sets)), key=float)


if __name__ == '__main__':
    scalefactor_to_querynb_to_avgtime = dict()
    for scalefactor in SCALE_FACTORS:
        result_file_path = RESULT_FILE_PATH.format(scalefactor)
        querynb_to_avgtime = get_querynb_to_avgtime()

        scalefactor_to_querynb_to_avgtime[scalefactor] = querynb_to_avgtime

    querynb_list = get_completely_executed_queries(scalefactor_to_querynb_to_avgtime)
    query_nbs = len(querynb_list)

    fig, ax = plt.subplots(figsize=(50, 4))
    index = np.arange(query_nbs)
    bar_width = 0.2

    for i, scalefactor in enumerate(SCALE_FACTORS):
        avgtime_list = [scalefactor_to_querynb_to_avgtime[scalefactor][querynb] for querynb in querynb_list]

        plt.bar(index + bar_width * i, avgtime_list, bar_width,
                color=COLORS[i],
                label='{}GB'.format(scalefactor))

    plt.bar(index + bar_width * len(SCALE_FACTORS) + 0.1, [300000] * len(avgtime_list), 0, color='black')

    plt.xlabel('Queries')
    plt.ylabel('Avg time')
    #plt.title('Title in progress')
    plt.xticks(index + bar_width * 2, querynb_list)
    ax.xaxis.set_ticks_position('none')
    plt.legend()
    fig.savefig('test.png', bbox_inches='tight', dpi=100)
    plt.show()
