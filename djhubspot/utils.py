from datetime import datetime, timezone


def pretty_request(request):
    """
    A simple function to convert a Django request to a string the way requests are meant to be
    printed.

    Source: https://gist.github.com/defrex/6140951

    Returns
    -------
    str: A displayable request as a string.
    """
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )


def hubspot_timestamp_to_datetime(hs_timestamp):
    """
    Convert an hubspot timestamp (in millisecond) to an UTC tz aware datetime.

    Cf:
    https://developers.hubspot.com/docs/faq/how-should-timestamps-be-formatted-for-hubspots-apis

    Returns
    -------
    datetime

    """
    # We ensure to work on an integer as hubspot timestamps are transmitted as string.
    hs_timestamp = int(hs_timestamp)
    return datetime.fromtimestamp(hs_timestamp / 1000.0, tz=timezone.utc)
