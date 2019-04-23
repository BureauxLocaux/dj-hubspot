class HubspotError(Exception):
    pass


# TODO: Create more specific event errors.
class HubspotEventError(HubspotError):
    pass
