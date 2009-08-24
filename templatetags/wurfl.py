from django import template
register = template.Library()

def get_device_from_context(context):
    try:
        device = context['device']
        return device
    except KeyError:
        return None

def parse_with_else(parser, token, end_tag):
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return nodelist_true, nodelist_false

ops = {
    '==': lambda x,y: x == y,
    '!=': lambda x,y: x != y,
    '<': lambda x,y: x < y,
    '>': lambda x,y: x > y,
    '<=': lambda x,y: x <= y,
    '>=': lambda x,y: x >= y
}


@register.tag
def device_has(parser, token):
    try:
        values = token.split_contents()
        tag_name = values[0]
        prop_name = template.Variable(values[1])
        if len(values) >= 3:
            if len(values) != 4:
                msg = "`%s` tag malformed.\n" % tag_name +\
                    "If you have more than one argument, you must have both.\n"+\
                    "an operator [==,!=,<,>,<=,>=], and a value to compare to.\n"
                raise template.TemplateSyntaxError(msg)

            op = values[2]
            try:
                operator = ops[op]
            except KeyError:
                msg = "`%s` tag malformed.\n" % tag_name +\
                      "Operator `%s` is not valid.\n" % op+\
                      "Valid operators are [==,!=,<,>,<=,>=].\n"
                raise template.TemplateSyntaxError(msg)
            
            val = template.Variable(values[3])
        else:
            operator = ops['=']
            val = True
            
    except IndexError:
        msg = "`%s` tag requires at least one argument, the property name. \n" % tag_name +\
        "An optional second argument gives a value to compare against (default: boolean True)."
        raise template.TemplateSyntaxError(msg)

    nodelist_true, nodelist_false = parse_with_else(parser, token, 'end_device_has')

    return DeviceHasNode(prop_name, val, operator, nodelist_true, nodelist_false)


class DeviceHasNode(template.Node):
    def __init__(self, prop_name, val, operator, nodelist_true, nodelist_false):
        self.prop_name = prop_name
        self.val = val
        self.operator = operator
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        device = get_device_from_context(context)

        self.prop_name = self.prop_name.resolve(context)
        self.val = self.val.resolve(context)

        #If no params were passed
        if type(self.val) == type(True) and self.val == True:
            compare = lambda x,y: bool(x) and unicode(x) != u"none"
        else:
            compare = lambda x,y: self.operator(x,y)
            
        passed = bool(device) and compare(getattr(device, self.prop_name, None), self.val)
        
        if passed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)



@register.tag
def device_prop(parser, token):
    try:
        values = token.split_contents()
        tag_name = values[0]
        prop_name = template.Variable(values[1])
    except IndexError:
        msg = "`%s` tag requires at least one argument, the property name. \n" % tag_name
        raise template.TemplateSyntaxError(msg)
    return DevicePropNode(prop_name)


class DevicePropNode(template.Node):
    def __init__(self, prop_name):
        self.prop_name = prop_name

    def render(self, context):
        device = get_device_from_context(context)
        self.prop_name = self.prop_name.resolve(context)
        
        if not device:
            return "None"
        else:
            val = getattr(device, self.prop_name, None)
            return unicode(val)
                


@register.tag
def device_debug(parser, token):
    return DeviceDebugNode()


class DeviceDebugNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):     
        debug = "<div class=\"wurfl-device-debug\"><h1>Device Debug</h1>"

        device = get_device_from_context(context)
        if not device:
            debug += "<h2>No `device` attribute found in context, or device was not found.</h2></div>"
            return debug

        for group_name, capabilities in device.groups.iteritems():
            debug += "<h2>%s</h2><pre>" % group_name
            
            for capability in capabilities:
                debug += "\n%s = %s" % (capability, getattr(device, capability))
                
            debug += "</pre>"

        debug += "</div>"

        return debug

@register.tag
def device_found(parser, token):
    nodelist_true, nodelist_false = parse_with_else(parser, token, 'end_device_found')

    return DeviceFoundNode(nodelist_true, nodelist_false)


class DeviceFoundNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        device = get_device_from_context(context)
        
        if device:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
