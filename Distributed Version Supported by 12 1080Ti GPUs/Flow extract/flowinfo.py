import collections
import urllib.request
import numpy as np
import ssl
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

ssl._create_default_https_context = ssl._create_unverified_context

transfers = collections.defaultdict(dict)
transfers_num_flow = collections.defaultdict(dict)

file = open("transfer")
line = file.readline()

while line:
    line = str(line)
    if "exported" in line or "assigned" in line:
        line = file.readline()
        continue
    ht = chr(9)
    lines = line.split(ht)
    # basic information,
    source = lines[1]
    destination = lines[3]
    num_files = int(lines[7])
    size_has_unit = lines[8]
    # MB as unit
    size = float(size_has_unit[:len(size_has_unit) - 2])

    if size_has_unit[len(size_has_unit) - 2] == 'T':
        size = size * 1024 * 1024
    elif size_has_unit[len(size_has_unit) - 2] == 'G':
        size = size * 1024

    if transfers.get(source) is None:
        transfers[source][destination] = [num_files, size]
        transfers_num_flow[source][destination] = 1
    else:
        if transfers[source].get(destination) is None:
            transfers[source][destination] = [num_files, size]
            transfers_num_flow[source][destination] = 1
        else:
            transfers[source][destination][0] += num_files
            transfers[source][destination][1] += size
            transfers_num_flow[source][destination] += 1

    line = file.readline()

file.close()
print("Transfer basic information got.")

count = 0

site_id = {}
index = 0
for s in transfers.keys():
    if site_id.get(s) is None:
        site_id[s] = index
        index += 1
    for d in transfers[s].keys():
        if site_id.get(d) is None:
            site_id[d] = index
            index += 1
columns = []
for i in site_id.keys():
    columns.append(i)

matrix = np.zeros([68, 68])
for i in transfers_num_flow.keys():
    for j in transfers_num_flow[i].keys():
        matrix[site_id[i]][site_id[j]] = transfers_num_flow[i][j]

fig, ax = plt.subplots(figsize=(20, 20))
sns.heatmap(pd.DataFrame(matrix, columns=columns, index=columns), annot=True, vmax=10, vmin=0, xticklabels=True,
            yticklabels=True, square=True, cmap="YlGnBu")

ax.set_title('title', fontsize=18)
ax.set_ylabel('destination', fontsize=1)
ax.set_xlabel('source', fontsize=1)  # 横变成y轴，跟矩阵原始的布局情况是一样的

fig.savefig('hh.png')

# for s in transfers.keys():
#     for d in transfers[s].keys():
#         # loop property
#         start_time = '9999-09-09 09:99:99'
#         for p in range(7):
#             url = 'https://cmsweb.cern.ch/phedex/prod/Activity::FileInfo?priority=' + str(
#                 p) + ';to_node=' + s + ';from_node=' + d + ';state=transferring'
#             response = urllib.request.urlopen(url)
#             html = str(response.read())
#             times = html.split("<b>time_assign</b>=")
#             if len(times) > 1:
#                 if times[1][:19] < start_time:
#                     start_time = times[1][:19]
#
#         count += 1
#         print("grep " + str(count) + ":")
#         print(start_time)
#
#         info = s + ' ' + d + ' ' + str(transfers[s][d][0]) + ' ' + str(transfers[s][d][1]) + ' ' + start_time + '\n'
#         file = open('flowtime.txt', 'a+')
#         file.write(info)
#         file.close()
