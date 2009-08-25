# About
django_wurfl_tools provides a number of tools to make integration of WURFL into a django project easier.

It's not a 'framework' and doesn't force you to work in any particular way, it just gives you the tools you need.

This is in development. Expect more features to come.

# Prerequisites
[PyWurfl](http://celljam.net/) - see the link for installation instructions. 

If you want to use the Levenshtein distance or Jaro-Winkler algorithms for user agent similarity, you'll need the [Levenshtein Module](http://celljam.net/downloads/pywurfl/python-Levenshtein-0.10.1.tar.gz)

The template context processor attempts to use algorithms in the following order - LevenshteinDistance, JaroWinkler, Tokenizer.

# Installation
 * You'll need to create a wurfl.py file in this directory, by running the wurfl2python.py script included with pywurfl, on the [latest version of WURFL.xml](http://sourceforge.net/projects/wurfl/files/WURFL/latest/wurfl-latest.xml.gz/download). The one included is dated August 21st, but you'd be wise to get the latest version.
 * Drop this directory into the root of your django project, or wherever you keep your django apps.
 * Add `'django_wurfl_tools'` to your `INSTALLED_APPS` setting in settings.py. This is required to use the templatetags provided.

#Usage
## Template Context Processor
  * Add `'django_wurfl_tools.context_processors.get_device'` to your `TEMPLATE_CONTEXT_PROCESSORS` setting in settings.py.
  * This will put a variable named `device` into your context (as long as you're using `RequestContext`), which is a pywurfl object representing the current device, or None if the device couldn't be found.
  * Any device variables can then be accessed as `{{device.<property_name>}}`. For more info, check out the [pywurfl docs](http://celljam.net/).


## Template Tags
  * In any template where you want to use the template tags, add `{% load wurfl %}`. This loads the following tags:

### device_debug
Prints out some device debug information. Useful for debugging which device is requesting the page.

#### Usage
`{% device_debug %}`

### device_prop
Prints out the value of a device property. Also useful for debugging or telling the user about their device.

####Usage

`{% device_prop "model_name" %}`

Note that this is the same as:

`{{ device.model_name }}`

However, the device_prop tag allows you to access a dynamic property, like so:

`{% device_prop property %}` - where `'property'` is a context variable with the value of e.g. "model_name".

### device_has
Allows conditional hiding/showing of markup depending on a device property. Also allows the use of inequalities.

#### Usage
You can test a property in a boolean context:

    {% device_has "vpn" %}
       You have VPN! 
    {% else %} 
       No VPN I'm afraid :( 
    {% end_device_has %}`

You can also test against inequalities. Valid inequalities are [==, !=, <, >, <=, >=, or a callable].

The callable should take two arguments, the property value as it's first, and the value to compare against
as it's second. It should return a boolean.

Logical and/or/not are not currently supported

    {% device_has "max_data_rate" >= 9 %}
        Fast 
    {% end_device_has %}
    {% device_has "max_data_rate" >= 40.5 %}
        Really fast
    {% end_device_has %}
    {% device_has "max_data_rate" callable 10.34 %}
        Maybe fast or slow, depends what callable does
    {% end_device_has %}

Both the device property and the comparison value may be context variables
    {% device_has prop == prop_val %}
        Passed - {{prop}} == {{prop_val}}
    {% else %}
        Failed - {{prop}} != {{prop_val}}
    {% end_device_has %}