## Script (Python) "translate_target"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=domain, id, target
##title=
##
from Products.PythonScripts.standard import html_quote
from Products.PlacelessTranslationService import getTranslationService

request = container.REQUEST
RESPONSE =  request.RESPONSE

return getTranslationService().utranslate(domain, id, target_language=target)

