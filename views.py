from django.shortcuts import render_to_response
from django.template.context import RequestContext

def test(request):
    return render_to_response('wurfl/test.html', {'prop':'max_data_rate', 'fn':lambda x,y: True}, context_instance=RequestContext(request))
