## Script (Python) "base_css"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.PythonScripts.standard import html_quote

request = container.REQUEST
RESPONSE =  request.RESPONSE

sheets = ['/includes/front-new.css']
if (not('weblog' in request['URL']) and 
    not('press'  in request['URL']) and
    not('press-releases' in request['URL'])):
    sheets.append('/includes/publish.css')

for sheet in sheets:
   print "     @import url(%s/%s);" % (context.portal_url(), sheet)

print " #search {display:none;}"

return printed
