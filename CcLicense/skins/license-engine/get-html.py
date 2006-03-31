## Script (Python) "get-html"
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

license_info = context.license.licenseUrlToCode(lurl or request['license_url'])
request.form['license_code'], request.form['jurisdiction'], request.form['version'] = license_info

if license_info[0] == 'publicdomain':
   del request.form['license_code']
   request.form['publicdomain'] = True

license = context.license.issue()
print license['rdf']
return printed

