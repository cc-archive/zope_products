## Script (Python) "get_tlf"
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

if 'VIRTUAL_URL_PARTS' in request.keys():
   return request['VIRTUAL_URL_PARTS'][1].split('/')[0]
else:
   return [n for n in request['PATH_INFO'].split('/') if n][0]

