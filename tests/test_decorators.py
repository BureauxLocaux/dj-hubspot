from django.http import HttpResponse
from django.test import RequestFactory
from django.utils.decorators import method_decorator
from django.views.generic import View

from djhubspot import constants
from djhubspot.decorators import request_is_from_hubspot

from .base import TestCase


@method_decorator(request_is_from_hubspot, name='dispatch')
class MockWebhookView(View):

    def post(self, request):
        """Simply return an HTTP 200 OK if the authorization is granted."""
        return HttpResponse(status=200)


HUBSPOT_SIGNATURE = 'd6bf47bacf91169753444a9807c716c7a45400a9c07df4278328d986b29fc7bf'
REQUEST_BODY = b'[{"objectId":697680835,"propertyName":"dealstage","propertyValue":"closedwon","changeSource":"AUTOMATION_PLATFORM","eventId":1228532628,"subscriptionId":92894,"portalId":5799819,"appId":186886,"occurredAt":1556105815815,"subscriptionType":"deal.propertyChange","attemptNumber":3}]'  # noqa


class RequestIsFromHubspotTestCase(TestCase):
    """
    Perform tests on the `request_is_from_hubspot` decorator.

    Those tests ensure that a view decorated with this method is well protected against requests
    made by anyone other than hubspot.
    """

    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()

    def test_invalid_signature(self):
        """
        Try to perform a POST request on the webhook view with an invalid hubspot signature
        header.
        """
        # We first try to perform the request without the `X-HubSpot-Signature` header ...
        request = self.request_factory.post('/hooks/hubspot/')
        response = MockWebhookView.as_view()(request)

        self.assertEqual(response.status_code, 401)

        # ... then, we put a random string value in it.
        request = self.request_factory.post(
            '/hooks/hubspot/',
            data=REQUEST_BODY,
            content_type='application/json',
        )
        request.META['X-HubSpot-Signature'] = 'invalid_signature'
        response = MockWebhookView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_valid_signature(self):
        """Perform a POST to the webhook view with a valid hubspot signature."""
        request = self.request_factory.post(
            '/hooks/hubspot/',
            data=REQUEST_BODY,
            content_type='application/json',
        )
        request.META[constants.HUBSPOT_SIGNATURE_HEADER_NAME] = HUBSPOT_SIGNATURE
        response = MockWebhookView.as_view()(request)

        self.assertEqual(response.status_code, 200)
