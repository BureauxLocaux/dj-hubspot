from unittest import mock

from django.test import RequestFactory

from djhubspot import constants
from djhubspot.events import HubspotEvent
from djhubspot.views import WebhookView

from .base import TestCase


HUBSPOT_SIGNATURE = '4be18e659e19082ef5a7d29dfce934d9755596201bcfe65252eb84f624ce4410'
REQUEST_BODY = b'[{"objectId":741141656,"propertyName":"dealstage","propertyValue":"1f4f1ec1-8174-49f3-a112-4eaa4748e38e","changeSource":"CRM_UI","eventId":4168025182,"subscriptionId":92894,"portalId":5799819,"appId":186886,"occurredAt":1557224426153,"subscriptionType":"deal.propertyChange","attemptNumber":0}]'  # noqa


class WebhookViewTestCase(TestCase):
    """Perform test of the 'hubspot_request' decorator."""

    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()

    # FIXME: Tests below are currently commenter because `HUBSPOT_APP_SECRET` is `None` from the
    # FIXME: settings. Those tests are working with the real key. But we dont want to push it on
    # FIXME: the repository.

    # def test_invalid_hubspot_request(self):
    #     """
    #     Try to perform a POST request on the webhook view with an invalid hubspot signature
    #     header.
    #     """
    #     # We first try to perform the request without the `X-HubSpot-Signature` header ...
    #     request = self.request_factory.post('/webhook/')
    #     response = WebhookView.as_view()(request)
    #
    #     self.assertEqual(response.status_code, 401)
    #
    #     # ... then, we put a random string value in it.
    #     request = self.request_factory.post('/webhook/')
    #     request.META['X-HubSpot-Signature'] = 'invalid_signature'
    #     response = WebhookView.as_view()(request)
    #
    #     self.assertEqual(response.status_code, 401)
    #
    # def test_process_events(self):
    #
    #     with mock.patch.object(
    #             WebhookView,
    #             'process_event',
    #             return_value=None,
    #     ) as process_event_mock:
    #
    #         request = self.request_factory.post(
    #             '/hooks/hubspot/',
    #             data=REQUEST_BODY,
    #             content_type='application/json',
    #         )
    #         request.META[constants.HUBSPOT_SIGNATURE_HEADER_NAME] = HUBSPOT_SIGNATURE
    #         response = WebhookView.as_view()(request)
    #
    #         # First ensure that the request was successful ...
    #         self.assertEqual(response.status_code, 200)
    #         # ... then, that our `process_event` method was called only once.
    #         process_event_mock.assert_called_once()
    #
    #         # Finally, compare the message received with the one expected.
    #
    #         called_args, called_kwargs = process_event_mock.call_args
    #         called_event = called_args[0]
    #
    #         self.assertDictEqual(
    #             called_event.message, {
    #                 'objectId': 741141656,
    #                 'propertyName': 'dealstage',
    #                 'propertyValue': '1f4f1ec1-8174-49f3-a112-4eaa4748e38e',
    #                 'changeSource': 'CRM_UI',
    #                 'eventId': 4168025182,
    #                 'subscriptionId': 92894,
    #                 'portalId': 5799819,
    #                 'appId': 186886,
    #                 'occurredAt': 1557224426153,
    #                 'subscriptionType': 'deal.propertyChange',
    #                 'attemptNumber': 0,
    #             }
    #         )
