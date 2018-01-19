import requests
from bs4 import BeautifulSoup
import sys
import numpy as np
sys.path.append("picotools/")
from picotools.log_tools.extract import get_all_info_from_content

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
assert(len(watch_list) != 0)
print_method = TABLE
if print_method == GRAPH:
    try:
        import matplotlib.pyplot as plt
    except:
        print "warning: can't import pyplot, change your print_method plz!!"
        exit()

r = requests.get(home)
soup = BeautifulSoup(r.text, 'lxml')

def fetch(s, a):
    index = s.find(a)
    if index == -1:
        return 'None'
    cur_s = s[index + len(a):].strip()
    ret = ""
    for c in cur_s:
        if not c.isdigit():
            break
        ret += c
    return ret

app_list = eval(soup.find_all('script')[7].string.strip().split(appsTable)[1])
app_list = filter(lambda x : x[1] == 'wanghai', app_list)               #all your running

for index, ele in enumerate(app_list):
    app_tag_a = BeautifulSoup(ele[0], 'lxml').a
    app_id = app_tag_a.string
    print str(index) + '): ' + app_id,
    for i in range(1, 3):
        print ele[i], '\t',
    print ' o'

    r2 = requests.get(home_prefix + app_tag_a['href'])
    soup2 = BeautifulSoup(r2.text, 'lxml')
    #  print soup2.find_all('script')[8].string.strip().split(attemptsTable)
    attempt_list = eval(soup2.find_all('script')[8].string.strip().split(attemptsTable)[1])
    latest_attempt = attempt_list[-1]
    latest_attempt_tag_a = BeautifulSoup(latest_attempt[0], 'lxml').a
    print '\t', 'latest attempt id = ' + latest_attempt_tag_a.string

    r3 = requests.get(home_prefix + latest_attempt_tag_a['href'])
    soup3 = BeautifulSoup(r3.text, 'lxml')
    container_list = eval(soup3.find_all('script')[-1].string.strip().split(containersTable)[1])

    logs = None
    for cont_index, container in enumerate(container_list):
        cont_id = BeautifulSoup(container[0], 'lxml').a.string
        if cont_id.split('_')[-1] != '000001':
            cont_url = BeautifulSoup(container[-1], 'lxml').a['href'] + '/stderr' + '/?start=0&&end=1000'
            #  print cont_url
            r4 = requests.get(cont_url)
            #  print r4.content
            soup4 = BeautifulSoup(r4.text, 'lxml')
            #  print soup4.find_all('pre')
            cont_rank = fetch(soup4.find_all('pre')[-1].string, 'rank:')
            if cont_rank == wanted_rank:
                url = BeautifulSoup(container[-1], 'lxml').a['href'] + '/stderr' + '/?start=-1000000'
                logs = BeautifulSoup(requests.get(url).text, 'lxml').find_all('pre')[-1].string
                #  break
        else:
            cont_rank = 'Master'
        print '\t', '\t', str(cont_index), ':', 'container_id = ' + cont_id, 'rank = ' + cont_rank

    try:
        info = get_all_info_from_content(logs.split('\n'), start_info)
    except:
        print 'no rank 0 found'
        continue
    result = []
    for k in watch_list:
        if k in info:
            result.append((k, info[k]))
    #  for k, v in info.iteritems():
    #      if watch_list is not None and k in watch_list:
    #          result.append((k, v))

    try:
        assert(len(result) != 0)
    except:
        print 'no target found'
        continue

    if print_method == TABLE:
        max_width = max(map(len, watch_list))
        row_format = ("{:<" + str(max_width + 2) + "}") * (len(result))
        print '\t', '\t', row_format.format(*[x[0] for x in result])
        for i in range(len(result[0][1])):
            print '\t', '\t', row_format.format(*[x[1][i] for x in result])
        print '-' * 80
        print
    elif print_method == GRAPH:
        plt.figure()
        xl = result[0][1][0]
        xr = result[0][1][-1]
        max_val = -1e60
        min_val = 1e60
        for i in range(1, len(result)):
            assert(xr - xl + 1 == len(result[i][1]))
            plt.plot(np.linspace(xl, xr, xr - xl + 1), result[i][1], label = result[i][0])
            #  if i + 1 == len(result):
            max_val = max(max_val, max(result[i][1]))
            min_val = min(min_val, min(result[i][1]))

        plt.axis([xl, xr, min_val - 0.0001, max_val + 0.0001])
        plt.legend(loc = 'upper right')
        plt.show()

    #  for i in range(len(result)):
    #      print result[i][0] + '\t',
    #  print
    #  for i in range(len(result[0][1])):
    #      print '\t', '\t',
    #      for j in range(len(result)):
    #          print str(result[j][1][i]), '\t',
    #      print
