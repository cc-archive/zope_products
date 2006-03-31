## Script (Python) "getFullname"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=
##
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

if obj is None:
   obj = context
mst = context.portal_membership

try:
   return (mst.getMemberById(obj.Creator()).getProperty('fullname') or obj.Creator())
except AttributeError, e:
   return 'Anonymous'
