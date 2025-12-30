from django.shortcuts import render

def job_list(request):
    return render(request, 'jobs/job_list.html')
