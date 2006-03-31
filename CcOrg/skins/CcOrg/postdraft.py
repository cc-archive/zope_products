## Script (Python) "postdraft"
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

blog = getattr(context.simpleblog_tool.getStartpoint(context), 'entry')

title = request['title']
body  = request['bodytext']
username = request['username']

entry_id = context.generateUniqueId('BlogEntry')
blog.invokeFactory('BlogEntry', entry_id)
newentry = getattr(blog, entry_id)

newentry.setTitle(title)
newentry.setBody(body)
# newentry.old_username=username

print newentry.absolute_url()
return printed
