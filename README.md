# get_hdfs_log
how to get your logs from web

home_prefix = 'http://xxxxxxxx:8088'
home = 'http://xxxxxx:8088/cluster/apps/RUNNING'
appsTable = 'appsTableData='
attemptsTable = 'attemptsTableData='
containersTable = 'containersTableData='

TABLE = 1
GRAPH = 2

wanted_rank = 0     #look appattempt_xxxxxx_000001
start_info = 'Accumulator[JSON]'
watch_list = ['progressive_auc', 'progressive_logloss', 'validation_auc']    #depend on your log


app_list = filter(lambda x : x[1] == 'wanghai', app_list)               #all your running

python monitor.py
