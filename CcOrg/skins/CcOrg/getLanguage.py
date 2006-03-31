## Script (Python) "getLanguage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Returns the language code to use for "help" pages linked from the license engine

request = container.REQUEST
RESPONSE =  request.RESPONSE

if 'lang' in request.keys():
   request.form['language'] = request['lang']

if 'language' in request.keys():
   return request['language']

return request['HTTP_ACCEPT_LANGUAGE'].split(';', 1)[0].split(',')[0]
