from wurfl import devices
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
    ua = request.META['HTTP_USER_AGENT']

    try:
        device = devices.select_ua(ua, search=algorithm(), filter_noise=True)
    except DeviceNotFound, e:
        device = None

    return {'device':device}
