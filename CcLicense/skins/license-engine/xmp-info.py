## Script (Python) "xmp-info"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lurl=None
##title=
##
from Products.PythonScripts.standard import html_quote

request = container.REQUEST
RESPONSE =  request.RESPONSE

def workType(format):

    WORK_FORMATS = {'Other':None,
                    'Audio':'Sound',
                    'Video':'MovingImage',
                    'Image':'StillImage',
                    'Text':'Text',
                    'Interactive':'InteractiveResource'
                    }

    if format == "":
        return "work"

    return WORK_FORMATS[format] 

license = context.license.issue()

# set up response headers
RESPONSE.setHeader('Content-Type', 'application/xmp');
RESPONSE.setHeader('Content-Disposition', 
                  'attachment; filename="CC_%s.xmp"' % license['name']);

# determine the license statement
if ('publicdomain' in license['deed']):
    statement = "This ${work_type} is dedicated to the public domain."
    copyrighted = False
else:
    year = ('field_year' in request.form and request['field_year']) or ""
    creator = ('field_creator' in request.form and request['field_creator']) or None
    work_type = workType(('field_format' in request.form and
                          request['field_format'])
                         or "")
    
    if creator:
        statement = "Copyright %s %s.  " % (year, creator,)
    else:
        statement = ""

    statement = statement + "This %s is licensed " \
                "to the public under the Creative Commons " \
                "%s License." %  (work_type, license['name'])
    copyrighted = True
    
return {'copyrighted': copyrighted,
        'statement':statement,
        'license_url':license['deed'],
        
        }

