from django.shortcuts import render
from collections import deque
import django_pandas

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
    return render(request, 'index.html')