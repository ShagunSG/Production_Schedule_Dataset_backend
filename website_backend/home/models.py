from django.db import models

# Create your models here.
class Home (models.Model):
    num_of_machines = models.BigIntegerField()
    num_of_jobs = models.BigIntegerField()
    time_per_job_per_machine = models.FileField()
    sequence_per_job = models.FileField()
    production_size = models.FileField()