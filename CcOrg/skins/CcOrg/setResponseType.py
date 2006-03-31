## Script (Python) "setResponseType"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentType
##title=
##
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

RESPONSE.setHeader('content-type', contentType)
