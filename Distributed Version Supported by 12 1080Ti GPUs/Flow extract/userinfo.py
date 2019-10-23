# input a tasks list, and retrieve job / files information
import ssl
import json
import jsonpath
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context

file = open("tasks")
file_out = open("jobs.txt", 'a+')
line = file.readline()

line_index = 0
task_index = 0

# loop each task
while line:
    line = str(line)
    line_index += 1
    if (line_index - 1) % 3 != 0:
        line = file.readline()
        continue

    # get the task name
    task_name = line[:len(line) - 1]

    # use request.py to get jobs information for one tasks
    url = 'http://dashb-cms-job.cern.ch/dashboard/request.py/antasktable?taskname=' + task_name
    response = urllib.request.urlopen(url)
    result = response.read()
    jobs_json = json.loads(result.decode('utf-8'))

    # list to store jobs <id, destination, started, finished>
    jobIDs = jsonpath.jsonpath(jobs_json, '$..SchedulerJobId')
    jobDestination = jsonpath.jsonpath(jobs_json, '$..Site')
    jobStarted = jsonpath.jsonpath(jobs_json, '$..started')
    jobFinished = jsonpath.jsonpath(jobs_json, '$..finished')

    for i in range(len(jobIDs)):
        job_info = jobIDs[i] + ' ' + jobDestination[i] + ' ' + jobStarted[i] + ' ' + jobFinished[i] + '\n'
        file_out.write(job_info)
    task_index += 1

    line = file.readline()
    print('grep task ' + str(task_index))

file.close()
file_out.close()
