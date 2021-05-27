from django.test import TestCase
from .models import MockAltUpdate
from .views import HealthView
from .tasks import save_altitude, generate_stats, determine_health, update_health
from datetime import datetime
import pytz

# Create your tests here.
class HealthTestCase(TestCase):
    # generates mock querysets to be used for testing
    def setUp(self):
        MockAltUpdate.objects.all().delete()
        below_160_test_set = MockAltUpdate.objects.bulk_create([
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 00, 00, pytz.UTC), altitude=150.0, average=110.0, set="below 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 10, 00, pytz.UTC), altitude=150.0, average=110.0, set="below 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 20, 00, pytz.UTC), altitude=150.0, average=110.0, set="below 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 30, 00, pytz.UTC), altitude=150.0, average=110.0, set="below 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 40, 00, pytz.UTC), altitude=150.0, average=110.0, set="below 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 50, 00, pytz.UTC), altitude=150.0, average=110.0, set="below 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 54, 00, 00, pytz.UTC), altitude=150.0, average=110.0, set="below 160")
        ])
        recovery_test_set = MockAltUpdate.objects.bulk_create([
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 00, 00, pytz.UTC), altitude=150.0, average=110.0, health_msg="WARNING: RAPID ORBITAL DECAY IMMINENT",  set="recovery"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 10, 00, pytz.UTC), altitude=150.0, average=110.0, health_msg="WARNING: RAPID ORBITAL DECAY IMMINENT",  set="recovery"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 20, 00, pytz.UTC), altitude=150.0, average=110.0, health_msg="WARNING: RAPID ORBITAL DECAY IMMINENT",  set="recovery"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 30, 00, pytz.UTC), altitude=170.0, average=160.0, set="recovery"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 40, 00, pytz.UTC), altitude=170.0, average=170.0, set="recovery"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 50, 00, pytz.UTC), altitude=190.0, average=175.0, set="recovery"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 54, 00, 00, pytz.UTC), altitude=190.0, average=175.0, set="recovery")
        ])
        above_160_test_set = MockAltUpdate.objects.bulk_create([
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 00, 00, pytz.UTC), altitude=170.0, average=161.0, set="above 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 10, 00, pytz.UTC), altitude=170.0, average=161.0, set="above 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 20, 00, pytz.UTC), altitude=170.0, average=161.0, set="above 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 30, 00, pytz.UTC), altitude=170.0, average=161.0, set="above 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 40, 00, pytz.UTC), altitude=170.0, average=161.0, set="above 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 50, 00, pytz.UTC), altitude=170.0, average=161.0, set="above 160"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 54, 00, 00, pytz.UTC), altitude=170.0, average=161.0, set="above 160")
        ])

        mixed_test_set = MockAltUpdate.objects.bulk_create([
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 00, 00, pytz.UTC), altitude=170.0, average=161.0, set="mixed"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 10, 00, pytz.UTC), altitude=150.0, average=110.0, set="mixed"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 20, 00, pytz.UTC), altitude=170.0, average=161.0, set="mixed"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 30, 00, pytz.UTC), altitude=150.0, average=110.0, set="mixed"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 40, 00, pytz.UTC), altitude=170.0, average=161.0, set="mixed"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 53, 50, 00, pytz.UTC), altitude=150.0, average=110.0, set="mixed"),
            MockAltUpdate(last_updated=datetime(2021, 5, 25, 23, 54, 00, 00, pytz.UTC), altitude=170.0, average=161.0, set="mixed")
        ])

        return

    # checks determine_health logic for warning case
    def test_warning_message(self):
        warning_altitudes = MockAltUpdate.objects.filter(set = "below 160")
        warning_message = determine_health(warning_altitudes)
        self.assertEqual(warning_message, "WARNING: RAPID ORBITAL DECAY IMMINENT")

    # checks that warning message is not sent if there is not over 1 minute of data
    def test_warning_message_under_one_minute(self):
        altitudes_short_list = MockAltUpdate.objects.filter(set = "below 160").filter(last_updated__gte=datetime(2021, 5, 25, 23, 53, 30, 00, pytz.UTC))
        message = determine_health(altitudes_short_list)
        self.assertEqual(message, "Altitude is A-OK")

    # checks determine_health logic for recovery case
    def test_recovery_message(self):
        recovered_altitudes = MockAltUpdate.objects.filter(set = "recovery")
        recovery_message = determine_health(recovered_altitudes)
        self.assertEqual(recovery_message, "Sustained Low Earth Orbit Resumed")

    # checks determine_health logic for ok case when all recent average altitudes are above 160km
    def test_ok_message_above_160(self):
        ok_altitudes_above = MockAltUpdate.objects.filter(set = "above 160")
        ok_message_above = determine_health(ok_altitudes_above)
        self.assertEqual(ok_message_above, "Altitude is A-OK")

    # checks determine_health logic for ok case with mixed average altitudes
    def test_ok_message_mixed(self):
        ok_altitudes_mixed = MockAltUpdate.objects.filter(set = "mixed")
        ok_message_mixed = determine_health(ok_altitudes_mixed)
        self.assertEqual(ok_message_mixed, "Altitude is A-OK")

    # checks that update_health changes the health_msg field of an object
    def test_update_health(self):
        sample_altupdate = MockAltUpdate.objects.filter(set="mixed").get(last_updated=datetime(2021, 5, 25, 23, 54, 00, 00, pytz.UTC))
        sample_altupdate.health_msg = None
        update_health(sample_altupdate)
        self.assertIsNotNone(sample_altupdate.health_msg)
