import logging
import json
from json import JSONDecodeError

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .decorators import request_is_from_hubspot
from .events import HubspotEvent
from .utils import pretty_request

from . import constants


logger = logging.getLogger('vendors.dj_hubspot')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(request_is_from_hubspot, name='dispatch')
class WebhookView(View):
    """
    Webhook endpoint dedicated to the handling of the hubspot notifications.
    """

    hubspot_events = []
    raw_body = None

    def process_event(self, event):
        """
        Process a single event.
        """
        raise NotImplementedError

    def process_events(self):
        """
        Process all the events contained in the request.

        This could be overridden to perform batch processing.
        """
        logger.debug(f"Processing {len(self.hubspot_events)} hubspot event(s).")
        for event in self.hubspot_events:
            self.process_event(event)

    def post(self, request):
        """
        Receive notifications from hubspot.

        Here is an example of a webhook request payload.
        ```
        [{
            "objectId": 1246965,
            "propertyName": "lifecyclestage",
            "propertyValue": "subscriber",
            "changeSource": "ACADEMY",
            "eventId": 3816279340,
            "subscriptionId": 25,
            "portalId": 33,
            "appId": 1160452,
            "occurredAt": 1462216307945,
            "subscriptionType": "contact.propertyChange",
            "attemptNumber": 0,
        }]
        """
        logger.debug('--- New request from hubspot.')

        # FIXME: At the moment, warning lvl is the only way to output something ...
        logger.warning(pretty_request(request))

        self.raw_body = request.body.decode('utf-8')

        try:
            json_events = json.loads(self.raw_body)
        except (JSONDecodeError, TypeError):
            # The content of the request seems to be invalid.
            logger.error(
                'Invalid request body received from hubspot.',
                extra={'raw_body': self.raw_body},
            )
            return HttpResponse('Bad request', status=constants.HTTP_400_BAD_REQUEST)

        for event in json_events:
            # FIXME: Handle errors. Log invalid events.
            self.hubspot_events.append(HubspotEvent(event))

        # Process hubspot events.
        self.process_events()

        return HttpResponse()
