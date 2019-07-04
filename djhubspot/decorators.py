import hashlib
import logging

from django.conf import settings
from django.http import HttpResponse

from . import constants

logger = logging.getLogger('vendors.dj_hubspot')


def assert_request_is_from_hubspot(request):
    """
    Compare the content of a header named 'X-HubSpot-Signature' with a sha256 of
    the concatenation of both app secret and request body.
    """
    client_secret = settings.HUBSPOT_APP_SECRET

    source_string = client_secret.encode() + request.body
    hubspot_signature = hashlib.sha256(source_string).hexdigest()

    try:
        if hubspot_signature != request.META[constants.HUBSPOT_SIGNATURE_HEADER_NAME]:
            logger.error(
                'Invalid signature received from Hubspot webhook request. You may have to '
                'check the settings of your projects.',
                extra={
                    'request': request,
                }
            )
            return False
    except KeyError:
        logger.warning('Hubspot signature header is missing from the request.', extra={
            'request': request,
        })
        return False
    else:
        return True


def request_is_from_hubspot(function):
    """
    Protect a view by ensuring that the request has been emitted by hubspot.

    This is done by comparing the content of a header named 'X-HubSpot-Signature' with a sha256 of
    the concatenation of both app secret and request body.

    Here is an example of a hubspot signature header:
    ```
    X-Hubspot-Signature: 6e4eb65b0bd0a54faba1f4c0d208ef8d43725bb2275684c95a8711859b4d5e8d
    ```

    Here is a complete example of an hubspot request:

    ```
    Host: pro.test.bureauxlocaux.com
    X-Forwarded-Proto: https
    Connection: close
    X-Hubspot-Signature: 6e4eb65b0bd0a54faba1f4c0d208ef8d43725bb2275684c95a8711859b4d5e8d
    User-Agent: HubSpot Connect 2.0 (http://dev.hubspot.com/) - WebhooksExecutorDaemon-executor
    X-Hubspot-Timeout-Millis: 10000
    Accept-Encoding: snappy,gzip,deflate
    b'[
        {
            "objectId":697680835,
            "propertyName":"dealstage",
            "propertyValue":"1f4f1ec1-8174-49f3-a112-4eaa4748e38e",
            "changeSource":"CRM_UI",
            "eventId":802835955,
            "subscriptionId":92894,
            "portalId":5799819,
            "appId":186886,
            "occurredAt":1556094637139,
            "subscriptionType":"deal.propertyChange",
            "attemptNumber":0
        }
    ]'
    ```

    Returns
    -------
    TODO
    """
    def wrap(request, *args, **kwargs):

        if not assert_request_is_from_hubspot(request):
            return HttpResponse('Unauthorized', status=constants.HTTP_401_UNAUTHORIZED)

        # Access granted!
        return function(request, *args, **kwargs)

    return wrap
