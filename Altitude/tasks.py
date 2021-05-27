from Altitude.models import AltUpdate
from celery import shared_task
from datetime import datetime, timedelta
from numpy.random import random_sample
import urllib.request
import json

from django.utils import dateparse
from django.utils.timezone import make_aware

from django.db.models import Avg, Max, Min


@shared_task()
def obtain_satellite_data():
    '''This task is called every 10 seconds and fills in a new AltUpdate object with data from the satellite update page'''

    url = 'http://nestio.space/api/satellite/data'
    openUrl = urllib.request.urlopen(url)
    data = openUrl.read() if openUrl.getcode()==200 else print("Error receiving data", operUrl.getcode())
    json_data = json.loads(data)

    update = {
        'last_updated': make_aware(dateparse.parse_datetime(json_data['last_updated'])),
        'altitude': float(json_data['altitude'])
    }
    new_altitude = save_altitude(update)

    generate_stats(new_altitude)
    update_health(new_altitude)

    return


def save_altitude(update):
    '''
        This function takes a dictionary of data values and creates a new AltUpdate object

        Parameters:
            update: Dictionary with keys 'last_updated' and 'altitude'

        Returns:
            new_altitude: AltUpdate object with last_updated and altitude from the update dictionary

    '''
    new_altitude = AltUpdate.objects.create(
        last_updated = update['last_updated'],
        altitude = update['altitude']
    )
    print(f"ran save_altitude, new object created with last_updated: {update['last_updated']}, altitude: {update['altitude']}")

    return new_altitude


def generate_stats(new_altitude):
    '''
        This function calculates and saves the average, maximum, and minimum values over 5 minutes given an AltUpdate object.

        Parameters:
            new_altitude: AltUpdate object with specified latest_time and altitude

    '''
    latest_time = new_altitude.last_updated
    five_minutes_ago = latest_time - timedelta(minutes=5)

    recent_updates = AltUpdate.objects.filter(last_updated__gte = five_minutes_ago)

    new_altitude.average = recent_updates.aggregate(Avg('altitude'))['altitude__avg']
    new_altitude.maximum = recent_updates.aggregate(Max('altitude'))['altitude__max']
    new_altitude.minimum = recent_updates.aggregate(Min('altitude'))['altitude__min']
    new_altitude.save()

    return


def update_health(new_altitude):
    '''
        This function updates the health status for an AltUpdate object

        Parameters:
            new_altitude: AltUpdate object with specified latest_time, altitude, and average

    '''
    latest_time = new_altitude.last_updated
    one_minute_ago = latest_time - timedelta(minutes=1)

    recent_updates = AltUpdate.objects.filter(last_updated__gte = one_minute_ago)

    new_altitude.health_msg = determine_health(recent_updates)
    new_altitude.save()

    return


def determine_health(recent_updates):
    '''
        This function determines the health status based on a queryset of AltUpdate objects over 1 minute.

        Parameters:
            recent_updates: A queryset of AltUpdate objects

        Returns:
            String providing information about the health of the satellite at the time of the most recent AltUpdate in the queryset
    '''


    over_160 = False
    for update in recent_updates:
        if update.average >= 160.0:
            over_160 = True

    number_of_updates = recent_updates.count()

    if not over_160 and number_of_updates > 6:
        return "WARNING: RAPID ORBITAL DECAY IMMINENT"
    else:
        recent_warning = False
        for update in recent_updates:
            if update.health_msg == "WARNING: RAPID ORBITAL DECAY IMMINENT":
                recent_warning = True
        if recent_warning:
            return "Sustained Low Earth Orbit Resumed"
        else:
            return "Altitude is A-OK"
