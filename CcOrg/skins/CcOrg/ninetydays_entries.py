## Script (Python) "ninetydays_entries"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.PythonScripts.standard import html_quote
from DateTime import DateTime

request = container.REQUEST
RESPONSE =  request.RESPONSE
zc = context.portal_catalog

# get the end date (today)
now = DateTime()

# get the start date (today - 3 months)
then = now - 90

objects = []

# find the blog container path
blogpath = context.simpleblog_tool.getObjectPath(context.simpleblog_tool.getStartpoint(context))

startDate = then
endDate = now

results = zc.searchResults(meta_type = 'BlogEntry', 
                           path=blogpath, 
                           review_state='published', 
                           sort_order='reverse', sort_on='effective'
                           )

for result in results:
   create_date = DateTime(str(result.getObject().getEffectiveDate()))
   if create_date > startDate and \
      create_date < endDate:
      objects.append(result)

return objects
