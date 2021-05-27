from django.db import models

# Create your models here.
class AltUpdate(models.Model):
    '''
        This class stores updated information for each altitude update.

        Attributes:
            last_updated (DateTimeField): Stores "last_updated" information from
                satellite update page. Value represents a timezone-aware
                DateTime that is converted from an ISO 8601 representation of
                the last time the data was updated.
            altitude (FloatField): Stores "altitude" information from satellite
                update page. Value represents altitude of the satellite in
                kilometers.
            minimum (FloatField): The minimum altitude of the satellite
                calculated over the past 5 minutes of data entries. In units of
                kilometers.
            maximum (FloatField): The maximum altitude of the satellite
                calculated over the past 5 minutes of data entries. In units of
                kilometers.
            average (FloatField): The average altitude of the satellite
                calculated over the past 5 minutes of data entries. In units of
                kilometers.
            health_msg (CharField): A message describing the health/status of
                the satellite based on the average altitudes for data entries
                over the last 5 minutes.

    '''
    last_updated = models.DateTimeField()
    altitude = models.FloatField()
    minimum = models.FloatField(null=True)
    maximum = models.FloatField(null=True)
    average = models.FloatField(null=True)
    health_msg = models.CharField(max_length = 250, null=True)


class MockAltUpdate(models.Model):
    '''This class is identical to the AltUpdate class but is used for testing.
    Contains an added "set" field to identify which test the object is used in.'''
    last_updated = models.DateTimeField()
    altitude = models.FloatField()
    minimum = models.FloatField(null=True)
    maximum = models.FloatField(null=True)
    average = models.FloatField(null=True)
    health_msg = models.CharField(max_length = 250, null=True)
    set = models.CharField(max_length=250, null=True)
