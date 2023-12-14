from django.shortcuts import render
from collections import deque
import django_pandas as pd
import numpy as np
import threading
import time
from time import sleep
from threading import Lock

# Create your views here.
def index(request):
    if request.method == "POST":
        number_of_machines = request.POST.get('num_of_machines')
        number_of_jobs = request.POST.get('num_of_jobs')
        time_per_machine_per_job = request.POST.get('time_per_job_per_machine')
        sequence_per_job = request.POST.get('sequence_per_job')
        production_size = request.POST.get('production_size')
    for i in range (int(number_of_jobs)):
        buffer = deque()
    def completionTime(jobID, sequenceNumber):
        time = np.random.normal(loc=machiningSequence[jobID][sequenceNumber][1],scale=0.0)
        return time
    lockList = []
    bufferList = []
    consumerState = []

    for i in range(int(number_of_machines)):
        lock = Lock()
        lockList.append(lock)
        consumerState.append(0)

    for i in range(int(number_of_jobs)):
        buffer = deque()
        for j in range(int(SequenceLength[i])):
            machineID = machiningSequence[i][j][0]
            cTime = completionTime(i,j)
            buffer.append((machineID, completionTime(i, j)))
            bufferList.append(buffer)
    
    entity_id = []
    product_id = []
    start_time = []
    end_time = []
    time_elapsed = []

    def entity(jobID, buffer):
        while(len(buffer)):
            item = buffer.popleft()
            with lockList[item[0]]:
                print(f"Entity {item[0] + 1} started consuming item {jobID + 1}")
                iniTime = time.time()
                sleep(item[1])
                finTime = iniTime + item[1]
                print(f"Entity {item[0] + 1} finished consuming item {jobID + 1}")
                end_time.append(finTime)
                start_time.append(iniTime)
                TimeElapsed = (finTime-iniTime)
                print(TimeElapsed)
                time_elapsed.append(TimeElapsed)
                product_id.append(jobID + 1)
                entity_id.append(item[0] + 1)


    # Create and start consumer threads
    entityThreads = []
    for i in range(int(number_of_jobs)):
        t = threading.Thread(target = entity, args=(i,bufferList[i]))
        entityThreads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in entityThreads:
        t.join()

    list_data = list(zip(entity_id,product_id,start_time,end_time,time_elapsed))
    list_data
    data = pd.DataFrame(list_data, columns = ['Entity ID', 'Product ID', 'Start Time', 'End Time', 'Time Elapsed'])
    data

    csvData = data.to_csv(index=False)
    csvFilePath = 'data.csv'
    with open(csvFilePath, 'w') as file:
        file.write(csvData)
    return render(request, 'index.html')