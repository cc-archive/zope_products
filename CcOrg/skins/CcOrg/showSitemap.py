## Script (Python) "showSitemap"
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

return [n for n in context.Subject() if n == 'show Sitemap']
