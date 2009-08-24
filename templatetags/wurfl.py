"""
django_wurfl_tools.templatetags.wurfl

Provides template tags for easy querying of the requesting device.

All of these template tags assume that there is a variable named
`device` in the template context, which is an instance of pywurfl.Device.

This can be achieved by using the provided template context processor.
"""

from django import template
register = template.Library()


def get_device_from_context(context):
    """
    Tries to get the device object from the context and return it.

    @param context: The Django template context
    @return: An instance of pywurfl.Device or None if the device is not found
    """
    try:
        device = context['device']
        return device
    except KeyError:
        return None

def parse_with_else(parser, token, end_tag):
    """
    Utility function to do the common task of parsing to an end tag,
    with an optional else tag.

    @param parser: The parser object passed to the templatetag compile function
    @param token: The token object passed to the templatetag compile function
    @param end_tag: The name of the end tag to parse to
    @type end_tag: string
    @return: a list of [nodelist_true, nodelist_false], representing nodelists to render for
    true and false respectively
    """
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return nodelist_true, nodelist_false


#A list of lambda functions to do inequality comparisons
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
    """Django templatetag compilation function to compare a device property 
    in a boolean context or with an inequality
    
    Usage:
    {% device_has "device_attr" %} Something {% else %} Something else {% end_device_has %} - Compares in a boolean context.
    {% device_has "device_attr" >= 9.0 %} Something {% else %} Something else {% end_device_has %} - Compares against an inequality
    {% device_has "device_attr" != "hi" %} Something {% end_device_has %} - Else is optional
    {% device_has device_attr == attr_val %} Something {% end_device_has %} - Attribute name and value can both reference context variables
    """

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
    """Renderer for device_has template_tag. 
    See django_wurfl_tools.templatetags.device_has for more details."""

    def __init__(self, prop_name, val, operator, nodelist_true, nodelist_false):
        """Initialiser for DeviceHasNode"""
        self.prop_name = prop_name
        self.val = val
        self.operator = operator
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        """Renders the true nodelist if the comparison evaluates to true,
        otherwise renders the false nodelist"""
        device = get_device_from_context(context)

        self.prop_name = self.prop_name.resolve(context)
        self.val = self.val.resolve(context)

        #If no inequality and value were passed, we use a boolean context
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
    """Django templatetag compilation function to return a string representation
    of a device property.
    
    Usage:
    {% device_prop "prop_name" %} - Outputs value of device.prop_name
    {% device_prop prop_name %} - Property name can be a context variable
    """
    try:
        values = token.split_contents()
        tag_name = values[0]
        prop_name = template.Variable(values[1])
    except IndexError:
        msg = "`%s` tag requires at least one argument, the property name. \n" % tag_name
        raise template.TemplateSyntaxError(msg)
    return DevicePropNode(prop_name)


class DevicePropNode(template.Node):
    """Renderer for device_prop templatetag.
    See django_wurfl_tools.templatetags.device_prop for more details."""

    def __init__(self, prop_name):
        """Initialiser for DevicePropNode"""
        self.prop_name = prop_name

    def render(self, context):
        """Renders the DeviceProp node by getting the value on the device
        or None if the property doesn't exist"""

        device = get_device_from_context(context)
        self.prop_name = self.prop_name.resolve(context)
        
        if not device:
            return "None"
        else:
            val = getattr(device, self.prop_name, None)
            return unicode(val)
                


@register.tag
def device_debug(parser, token):
    """Django templatetag compilation function for printing some device debug."""
    return DeviceDebugNode()


class DeviceDebugNode(template.Node):
    """Renderer for device_debug templatetag.
    See django_wurfl_tools.templatetags.device_debug for more details."""

    def __init__(self):
        "Initialiser for DeviceDebugNode. Does nada"""
        pass

    def render(self, context):     
        """Renders the DeviceDebugNode, printing out all the properties we
        know about the device"""
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
    """Django templatetag compilation function to check if the device was found in WURFL"""
    nodelist_true, nodelist_false = parse_with_else(parser, token, 'end_device_found')

    return DeviceFoundNode(nodelist_true, nodelist_false)


class DeviceFoundNode(template.Node):
    """Renderer for device_found templatetag"""
    def __init__(self, nodelist_true, nodelist_false):
        """"Initialiser for DeviceFoundNode"""
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        """Renders the true nodelist if the devices was found in WURFL,
        otherwise renders the false nodelist."""
        device = get_device_from_context(context)
        
        if device:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
