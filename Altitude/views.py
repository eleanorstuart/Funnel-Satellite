from django.shortcuts import render
from django.views.generic import ListView
from .models import AltUpdate
from datetime import date, datetime


# Create your views here.

def HomeView(request):
    '''Renders home.html file at home url'''
    return render(request, 'home.html')

class UpdateListView(ListView):
    '''Creates update-log page with AltUpdate entries from the current day (UTC)'''
    model = AltUpdate
    context_object_name = 'updates'
    queryset = AltUpdate.objects.filter(last_updated__date = datetime.utcnow()).order_by('-last_updated')
    template_name = 'update-log.html'

def StatsView(request):
    '''Gets the most recent AltUpdate and sends information to stats.html page'''
    latest_info = AltUpdate.objects.latest('last_updated')
    return render(request, 'stats.html', {'minimum': latest_info.minimum, 'maximum': latest_info.maximum, 'average': latest_info.average})

def HealthView(request):
    '''Gets the most recent AltUpdate and sends information to health.html page'''
    latest_info = AltUpdate.objects.latest('last_updated')
    return render(request, 'health.html', {'health_msg': latest_info.health_msg})
