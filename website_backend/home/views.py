from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from collections import deque
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
        productionSize = 0
        for i in range (int(number_of_jobs)):
            productionSize += prod_size.iloc[i,1]
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
                else:
                    j += 1
            SequenceLength.append(len(buffer))
            machiningSequence.append(buffer)
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
            bufferList_i = []
            buffer = deque()
            l = 1
            for j in range(SequenceLength[i]):
                machineID = machiningSequence[i][j][0]
                buffer.append((i+1, machineID, completionTime(i, j)))
            bufferList_i.append(buffer)
            while(l<prod_size.iloc[i,1]):
                buffer_cp = buffer.copy()
                bufferList_i.append(buffer_cp)
                l += 1
            bufferList.append(bufferList_i)
        entity_id = []
        job_id = []
        product_id=[]
        start_time = []
        end_time = []
        time_elapsed = []

        global finTime
        finTime = 0

        # Consumer thread function
        def entity(buffer, jobID):
            global finTime
            while(len(buffer)):
                item = buffer.popleft()
                # print(item, "\n")
                with lockList[item[1]]:
                    iniTime = finTime
                    sleep(item[2])
                    finTime = iniTime + item[2]
                    end_time.append(finTime)
                    start_time.append(iniTime)
                    TimeElapsed = (finTime-iniTime)
                    time_elapsed.append(TimeElapsed)
                    product_id.append(item[0])
                    job_id.append(jobID)
                    entity_id.append(item[1] + 1)

        # Create and start consumer threads
        entityThreads = []
        for i in range(int(number_of_jobs)):
            for j in range(prod_size.iloc[i,1]):
                print(j, "BufferList: ", bufferList[i][j], "\n")
                t = threading.Thread(target = entity, args=(bufferList[i][j], j+1))
                entityThreads.append(t)
                t.start()

        # Wait for all threads to finish
        for t in entityThreads:
            t.join()

        list_data = list(zip(product_id, job_id, entity_id,start_time,end_time,time_elapsed))
        data = pd.DataFrame(list_data, columns = ['Product ID', 'Job ID', 'Entity ID', 'Start Time', 'End Time', 'Time Elapsed'])

        csvData = data.to_csv(index=False)
        csvFilePath = 'data.csv'
        with open(csvFilePath, 'w') as file:
            file.write(csvData)
        # return render(request, 'index.html')
        response = HttpResponse(csvData, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"'
        return response