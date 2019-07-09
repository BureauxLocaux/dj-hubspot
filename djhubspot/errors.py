# Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
# djhubspot.
from hubspot3.error import *  # noqa


class DJHubspotError(Exception):
    """
    Errors from djhubspot.
    """
    pass


class HubspotEventError(DJHubspotError):
    """
    Error related to hubspot events.
    """
    pass
