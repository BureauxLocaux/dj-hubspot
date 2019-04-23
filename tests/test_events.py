from djhubspot.events import HubspotEvent

from .base import TestCase


# The content of a subscription from hubspot to use in unit tests.
JSON_EVENT = {
    "objectId": 697680835,
    "propertyName": "dealstage",
    "propertyValue": "1f4f1ec1-8174-49f3-a112-4eaa4748e38e",
    "changeSource": "CRM_UI",
    "eventId": 802835955,
    "subscriptionId": 92894,
    "portalId": 5799819,
    "appId": 186886,
    "occurredAt": 1556094637139,
    "subscriptionType": "deal.propertyChange",
    "attemptNumber": 0
}


class HubspotEventTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.event = HubspotEvent(JSON_EVENT)

    def test_event_type(self):
        self.assertEqual(
            self.event.event_type,
            HubspotEvent.EVENT_TYPE_DEAL_UPDATED,
        )

    # FIXME: Not sure about the timezone yet.
    # def test_occurred_at(self):
    #     self.assertEqual(
    #         self.event.occurred_at,
    #         datetime(2019, 4, 24, 10, 30, 37, 139000),
    #     )
