## Script (Python) "getStyle"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = container.REQUEST
RESPONSE =  request.RESPONSE

styles = [n for n in context.Subject() if n.islower()]

try:
  return styles[0]
except:
  return 'centercontent'
  # return ''
