from django.test import RequestFactory

from djhubspot.views import WebhookView

from .base import TestCase


class WebhookViewTestCase(TestCase):
    """Perform test of the 'hubspot_request' decorator."""

    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()

    # FIXME: Uncomment.
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
