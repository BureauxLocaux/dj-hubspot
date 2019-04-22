import json
import logging

logger = logging.getLogger('vendors.dj_hubspot')


def handle_webhook(request):

        # The Hubspot webhook transmits all data directly in the request body.
        raw_message = request.body.decode('utf-8')
        logger.debug("Received message from Hubspot webhook: ", raw_message)

        try:
            message = json.loads(raw_message)[0]  # We only support single-event notifications
        except Exception:
            logger.warning("Unable to parse Hubspot webhook request", decoded_request)
        else:
            return HubspotEvent(message)


class HubspotEvent:

    EVENT_TYPE_COMPANY_CREATED = 'company_created'
    EVENT_TYPE_COMPANY_DELETED = 'company_deleted'
    EVENT_TYPE_COMPANY_UPDATED = 'company_updated'
    EVENT_TYPE_CONTACT_CREATED = 'contact_created'
    EVENT_TYPE_CONTACT_DELETED = 'contact_deleted'
    EVENT_TYPE_CONTACT_UPDATED = 'contact_updated'
    EVENT_TYPE_DEAL_CREATED = 'deal_created'
    EVENT_TYPE_DEAL_DELETED = 'deal_deleted'
    EVENT_TYPE_DEAL_UPDATED = 'deal_updated'

    MESSAGE_EVENT_TO_EVENT_TYPE = {
        'contact.creation': EVENT_TYPE_COMPANY_CREATED,
        'contact.deletion': EVENT_TYPE_COMPANY_DELETED,
        'contact.propertyChange': EVENT_TYPE_COMPANY_UPDATED,
        'company.creation': EVENT_TYPE_CONTACT_CREATED,
        'company.deletion': EVENT_TYPE_CONTACT_DELETED,
        'company.propertyChange': EVENT_TYPE_CONTACT_UPDATED,
        'deal.creation': EVENT_TYPE_DEAL_CREATED,
        'deal.deletion': EVENT_TYPE_DEAL_DELETED,
        'deal.propertyChange' EVENT_TYPE_DEAL_UPDATED,
    }

    message = None
    event_type = None

    def __init__(self, message, **kwargs):
        self.message = message

        raw_event = self.message.get('event')
        try:
            self.event_type = self.MESSAGE_EVENT_TO_EVENT_TYPE[raw_event]
        except KeyError:
            logger.warning("Unrecognized Hubspot event type: ", raw_event)
        else:
            self.parse_event()

    def parse_event(self):
        try:
            getattr(self, 'parse_%s_event' % self.event_type)()
        except (AttributeError, TypeError):
            logger.warning("Unable to parse Hubspot event of type: ", self.event_type)

    def _parse_company_event(self):
        self.company_id = self.message.get('objectId')

    def _parse_contact_event(self):
        self.contact_id = self.message.get('objectId')

    def _parse_deal_event(self):
        self.deal_id = self.message.get('objectId')

    def _parse_updated_event(self):
        self.updated_property_name = self.message.get('propertyName')
        self.updated_property_value = self.message.get('propertyValue')

    def parse_company_updated_event(self):
        self._parse_company_event()
        self._parse_updated_event()

    def parse_contact_created_event(self):
        self._parse_contact_event()

    def parse_contact_updated_event(self):
        self._parse_contact_event()
        self._parse_updated_event()

    def parse_deal_updated_event(self):
        self._parse_deal_event()
        self._parse_updated_event()
