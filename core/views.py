from django.http import JsonResponse
from .models import State, City, College, Branch

def search_states(request):
    query = request.GET.get('q', '')
    states = State.objects.filter(name__icontains=query).values('id', 'name')[:10]
    return JsonResponse(list(states), safe=False)

def search_cities(request):
    query = request.GET.get('q', '')
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(name__icontains=query)
    if state_id:
        cities = cities.filter(state_id=state_id)
    cities = cities.values('id', 'name')[:10]
    return JsonResponse(list(cities), safe=False)

def search_colleges(request):
    query = request.GET.get('q', '')
    colleges = College.objects.filter(name__icontains=query).values('id', 'name')[:10]
    return JsonResponse(list(colleges), safe=False)

def search_branches(request):
    query = request.GET.get('q', '')
    branches = Branch.objects.filter(name__icontains=query).values('id', 'name')[:10]
    return JsonResponse(list(branches), safe=False)
