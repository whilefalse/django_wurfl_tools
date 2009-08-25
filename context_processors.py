"""
Provides template context processors for the automatic detection
and inclusion of the requesting device in the template context.
"""

from wurfl import devices
#You can use this if you want to import the whole wurfl.py module for testing.
#from mock_wurfl import devices

from pywurfl import DeviceNotFound
#Get the best algorithm possible
try:
    from pywurfl.algorithms import LevenshteinDistance as algorithm
except ImportError:
    try:
        from pywurfl.algorithms import JaroWinkler as algorithm
    except ImportError:
        from pywurfl.algorithms import Tokenizer as algorithm

def get_device(request):
    """
    Uses pywurfl to detect the requesting device from the HTTP_USER_AGENT string,
    and adds it to the context with the variable name `device`.

    If the device is not found by pywurfl, it sets the context variable to None. 
    """
    ua = request.META['HTTP_USER_AGENT']

    try:
        device = devices.select_ua(ua, search=algorithm(), filter_noise=True)
    except DeviceNotFound, e:
        device = None

    return {'device':device}
