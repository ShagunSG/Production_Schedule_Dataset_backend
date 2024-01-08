from django.shortcuts import render, HttpResponseRedirect
from collections import deque
import django_pandas as dpd
import pandas as pd
import numpy as np
import threading
import time
from time import sleep
from threading import Lock
from django.contrib import messages
from django.urls import reverse

# Create your views here.
def index(request):
    if request.method == "GET":
        return render(request, 'index.html')
    if request.method == "POST":
        number_of_machines = request.POST.get('num_of_machines')
        number_of_jobs = request.POST.get('num_of_jobs')
        time_per_machine_per_job = request.FILES.get('time_per_job_per_machine')
        sequence_per_job = request.FILES.get('sequence_per_job')
        production_size = request.FILES.get('production_size')
        if not time_per_machine_per_job.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse("home"))
        if not sequence_per_job.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse("home"))
        if not production_size.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse("home"))
        time_job = pd.read_csv(time_per_machine_per_job.file)
        sequence = pd.read_csv(sequence_per_job.file)
        prod_size = pd.read_csv(production_size.file)
        machiningSequence = []
        SequenceLength = []
        for i in range (int(number_of_jobs)):
            buffer = deque()
            j = 1
            k = 1
            while (j<int(number_of_machines)+1):
                if(sequence.iloc[i,j] == k):
                    buffer.append((j-1,time_job.iloc[i,j]))
                    j = 1
                    k += 1
                elif (sequence.iloc[i,j] == '-'):
                    j += 1
                j += 1
            SequenceLength.append(len(buffer))
            machiningSequence.append(buffer)
            # if (bool(prod_size.iloc[i,1]>1)):
            #     l=1
            #     while (l<prod_size.iloc[i,1]):
            #         machiningSequence.append(buffer)
            #         l += 1
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
                # if (i == 0):
                machineID = machiningSequence[i][j][0]
                buffer.append((machineID, completionTime(i, j)))
                    # if (bool(prod_size.iloc[i,1]>1)):
                    #     l=1
                    #     while (l<prod_size.iloc[i,1]):
                    #         buffer.append((machineID, completionTime(i, j)))
                    #         l += 1
                # elif (i > 0):
                #     machineID = machiningSequence[i + prod_size.iloc[i-1,1] - 1][j][0]
                #     cTime = completionTime(i + prod_size.iloc[i-1,1] - 1, j)
                #     buffer.append((machineID, cTime))
                #     if (bool(prod_size.iloc[i,1]>1)):
                #         l=1
                #         while (l<prod_size.iloc[i,1]):
                #             buffer.append((machineID, completionTime(i + prod_size.iloc[i-1,1] - 1, j)))
                #             l += 1
                bufferList.append(buffer)
        print(bufferList)
        entity_id = []
        product_id = []
        start_time = []
        end_time = []
        time_elapsed = []

        sTime = time.time()
        def entity(jobID, buffer):
            while(len(buffer)):
                item = buffer.popleft()
                with lockList[item[0]]:
                    print(f"Entity {item[0] + 1} started consuming item {jobID + 1}")
                    iniTime = time.time() - sTime
                    sleep(item[1]/4)
                    finTime = iniTime + item[1]
                    print(f"Entity {item[0] + 1} finished consuming item {jobID + 1}")
                    end_time.append(finTime)
                    start_time.append(iniTime)
                    TimeElapsed = (finTime-iniTime)
                    print(TimeElapsed)
                    time_elapsed.append(TimeElapsed)
                    product_id.append(jobID + 1)
                    entity_id.append(item[0] + 1)
                    if (bool(prod_size.iloc[i,1]>1)):
                        l=1
                        while (l<prod_size.iloc[i,1]):
                            entity_id.append(item[0] + 1)
                            product_id.append(jobID + 1)
                            iniTime = finTime
                            start_time.append(iniTime)
                            finTime = iniTime + item[1]
                            end_time.append(finTime)
                            finTime += item[1]
                            TimeElapsed = (finTime-iniTime)
                            time_elapsed.append(TimeElapsed)
                            l += 1


        # Create and start consumer threads
        entityThreads = []
        for i in range(int(number_of_jobs)):
            t = threading.Thread(target = entity, args=(i,bufferList[i]))
            entityThreads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in entityThreads:
            t.join()

        list_data = list(zip(product_id,entity_id,start_time,end_time,time_elapsed))
        list_data
        data = pd.DataFrame(list_data, columns = ['Product ID', 'Entity ID', 'Start Time', 'End Time', 'Time Elapsed'])
        data

        csvData = data.to_csv(index=False)
        csvFilePath = 'data.csv'
        with open(csvFilePath, 'w') as file:
            file.write(csvData)
        return render(request, 'index.html')