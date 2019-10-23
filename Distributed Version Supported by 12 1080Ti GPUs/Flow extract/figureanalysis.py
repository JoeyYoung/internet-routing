file = open("job_td.txt")
line = file.readline()

hour_out = [0, 0, 0, 0, 0, 0, 0, 0, 0]
while line:
    line = str(line)
    l = list(line)
    line = file.readline()

print(l)