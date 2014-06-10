from suds import MethodNotFound, WebFault
from suds.transport import TransportError
from suds.client import Client
from lxml import etree
from django.http import Http404
from xml.sax._exceptions import SAXParseException

def sites_from_soap(wsdl_url, locations=[':']):
    """
    Note: locations (a list) is given by CUAHSI WOF standard

    returns:
    a list of site names and codes at the given locations
    """

    if not wsdl_url.endswith('.asmx?WSDL'):
        raise Http404("The correct url format ends in '.asmx?WSDL'.")
    try:
         client = Client(wsdl_url)
    except TransportError:
        raise Http404('Url not found')
    except ValueError:
        raise Http404('Invalid url')  # ought to be a 400, but no page implemented for that
    except SAXParseException:
        raise Http404("The correct url format ends in '.asmx?WSDL'.")
    except:
        raise Http404("Sorry, but we've encountered an unexpected error.")
    try:
        response = client.service.GetSites(locations)
    except MethodNotFound:
        raise Http404("Method 'GetSites' not found")
    except WebFault:
        raise Http404('This service does not support an all sites search. \
Please provide a list of locations')  # ought to be a 400, but no page implemented for that
    except:
        raise Http404("Sorry, but we've encountered an unexpected error. This is most likely \
        due to incorrect formatting in the web service response.")
    try:
        ts_element = etree.XML(response)

        site_names = []
        site_codes = []

        for site in ts_element[1:]:
                site_names.append(site[0][0].text)
                site_codes.append(site[0][1].text)
    except:
        return "Parsing error: The Data in the WSDL Url '{0}' was not correctly formatted \
according to the WaterOneFlow standard given at 'http://his.cuahsi.org/wofws.html#waterml'.".format(wsdl_url)
    ret = dict(zip(site_names, site_codes))
    return ret

def site_info_from_soap(wsdl_url, **kwargs):
    site = ':' + kwargs['site']

    if not wsdl_url.endswith('.asmx?WSDL'):
        raise Http404("The correct url format ends in '.asmx?WSDL'.")
    try:
         client = Client(wsdl_url)
    except TransportError:
        raise Http404('Url not found')
    except ValueError:
        raise Http404('Invalid url')  # ought to be a 400, but no page implemented for that
    except SAXParseException:
        raise Http404("The correct url format ends in '.asmx?WSDL'.")
    except:
        raise Http404("Sorry, but we've encountered an unexpected error.")
    try:
        response = client.service.GetSiteInfo(site)
    except MethodNotFound:
        raise Http404("Method 'GetValues' not found")

    try:
        response = client.service.GetSiteInfo(site)
        root = etree.XML(response)
        variables = []

        for element in root.iter():
            if isinstance(element.tag, basestring):
                brackLoc = element.tag.index('}')  #The namespace in the tag is enclosed in {}.
                tag = element.tag[brackLoc+1:]     #Takes only actual tag, no namespace
                if 'variableName' in tag:
                     variables.append(element.text)
        return variables

    except:
        return "Parsing error: The Data in the WSDL Url '{0}' was not correctly formatted \
        according to the WaterOneFlow standard given at 'http://his.cuahsi.org/wofws.html#waterml'.".format(wsdl_url)


def time_series_from_soap(wsdl_url, **kwargs):
    """
    keyword arguments are given by CAUHSI WOF standard :
    site_name_or_code = location
    variable
    startDate
    endDate
    authToken

    returns:
    a string containing a WaterML file with location metadata and data
    """
    var = ':' + kwargs['variable']
    s_d = kwargs.get('startDate', '')
    e_d = kwargs.get('endDate', '')
    a_t = kwargs.get('authToken', '')
        
    try:
        client = Client(wsdl_url)
    except TransportError:
        raise Http404('Url not found')
    except ValueError:
        raise Http404('Invalid url')  # ought to be a 400, but no page implemented for that
    try:
        location = ':' + kwargs['site_name_or_code'] # maybe the user provided a site code
        response = client.service.GetValues(location, var, s_d, e_d, a_t)
    except MethodNotFound:
        raise Http404("Method 'GetValues' not found")
    except WebFault:
                #maybe the user provided a site name
        try:
            allsites = sites_from_soap(wsdl_url)
            location = ':' + allsites[kwargs['site_name_or_code']]
            response = client.service.GetValues(location, var, s_d, e_d, a_t)
        except KeyError:
            Http404('Invalid site name')
        except WebFault:
            raise Http404('One or more of your parameters may be incorrect. \
Location and Variable are not optional, and case sensitive')  # ought to be a 400, but no page implemented for that
        except:
            raise Http404("Sorry, but we've encountered an unexpected error")
    except:
        raise Http404("Sorry, but we've encountered an unexpected error. This is most likely \
due to incorrect formatting in the web service format.")
    try:
        time_series = etree.XML(response)[1]
        
        ts_string = etree.tostring(time_series)
        return ts_string

    except:
        return "Parsing error: The Data in the WSDL Url '{0}' was not correctly formatted \
according to the WaterOneFlow standard given at 'http://his.cuahsi.org/wofws.html#waterml'.".format(wsdl_url)

