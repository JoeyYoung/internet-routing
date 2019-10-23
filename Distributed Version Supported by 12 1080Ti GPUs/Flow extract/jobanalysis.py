import collections

file = open("jobinfo.txt")
line = file.readline()

"""
    "destination" : [num, [ST, FT, TD], ...]
"""

destinations = collections.defaultdict(list)

# TODO, 1. every destination has how many jobs
# TODO, 2. each job persist how many times
# TODO, 3. within every hour has how many jobs start/finished
while line:
    line = str(line)
    lines = line.split(" ")

    dest = lines[1]
    if dest == "unknown":
        line = file.readline()
        continue

    if destinations.get(dest) is None:
        destinations[dest] = [1]
    else:
        destinations[dest][0] += 1

    # 00-00 00:00:00
    # take min as unit to compute difference
    start_date = lines[2]
    start_min = lines[3]
    finish_date = lines[4]
    finish_min = lines[5]

    start_time_part1 = (int(start_date.split("-")[1]) * 30 + int(start_date.split("-")[0])) * 24 * 60
    start_time_part2 = int(start_min.split(":")[0]) * 60 + int(start_min.split(":")[1])
    start_time = start_time_part1 + start_time_part2

    finish_time_part1 = (int(finish_date.split("-")[1]) * 30 + int(finish_date.split("-")[0])) * 24 * 60
    finish_time_part2 = int(finish_min.split(":")[0]) * 60 + int(finish_min.split(":")[1])
    finish_time = finish_time_part1 + finish_time_part2

    td = finish_time - start_time

    # TODO, consider 01-01 00:00:00, still not finished
    if finish_date == "01-01" and finish_min == "00:00:00":
        print("hello")
        finish_time = 0
        td = start_time

    time_info = [start_time, finish_time, td]
    destinations[dest].append(time_info)

    line = file.readline()

file.close()
file_dest = open("job_dest.txt", 'w')
file_num = open("job_num.txt", 'w')
file_start = open("job_start.txt", 'w')
file_finish = open("job_finish.txt", 'w')
file_td = open("job_td.txt", 'w')

dests = []
nums = []
starts = []
finishs = []
tds = []
for i in destinations.keys():
    dests.append(i)
    nums.append(destinations[i][0])
    for j in range(1, len(destinations[i])):
        starts.append(destinations[i][j][0])
        finishs.append(destinations[i][j][1])
        tds.append(destinations[i][j][2])

file_dest.write(str(dests))
file_num.write(str(nums))
file_start.write(str(starts))
file_finish.write(str(finishs))
file_td.write(str(tds))

file_dest.close()
file_num.close()
file_start.close()
file_finish.close()
file_td.close()