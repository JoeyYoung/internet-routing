import collections

now = (4 * 30 + 8) * 24 * 60 + 6 * 60

file = open("flowtime.txt")
line = file.readline()

time_info = {}
index = 0

td_list = []
while line:
    line = str(line)
    lines = line.split(" ")
    data = lines[4]
    time = lines[5][:len(lines[5]) - 1]

    datas = data.split("-")
    times = time.split(":")
    if datas[0] == '9999':
        time_info[index] = 0
        td_list.append(0)
    else:
        start = (int(datas[1]) * 30 + int(datas[2])) * 24 * 60 + int(times[0]) * 60 + int(times[1])
        td = (now - start)/60
        time_info[index] = td
        td_list.append(td)

    index += 1
    line = file.readline()

print(td_list)
file.close()
