from hubspot3.error import (
    EmptyResult as _EmptyResult,
    HubspotError as _HubspotError,
    HubspotBadRequest as _HubspotBadRequest,
    HubspotNotFound as _HubspotNotFound,
    HubspotTimeout as _HubspotTimeout,
    HubspotUnauthorized as _HubspotUnauthorized,
    HubspotServerError as _HubspotServerError,
)


class EmptyResult(_EmptyResult):
    """
    Sub class from hubspot3.

    Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
    djhubspot.
    """
    pass


class HubspotError(_HubspotError):
    """
    Sub class from hubspot3.

    Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
    djhubspot.
    """
    pass


class HubspotBadRequest(_HubspotBadRequest):
    """
    Sub class from hubspot3.

    Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
    djhubspot.
    """
    pass


class HubspotNotFound(_HubspotNotFound):
    """
    Sub class from hubspot3.

    Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
    djhubspot.
    """
    pass


class HubspotTimeout(_HubspotTimeout):
    """
    Sub class from hubspot3.

    Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
    djhubspot.
    """
    pass


class HubspotUnauthorized(_HubspotUnauthorized):
    """
    Sub class from hubspot3.

    Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
    djhubspot.
    """
    pass


class HubspotServerError(_HubspotServerError):
    """
    Sub class from hubspot3.

    Provide an interface allowing users to import hubspot3 in a more intuitive way, directly from
    djhubspot.
    """
    pass


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
