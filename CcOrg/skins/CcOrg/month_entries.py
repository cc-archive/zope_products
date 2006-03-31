## Script (Python) "month_entries"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=month=None, year=None
##title=
##
from Products.PythonScripts.standard import html_quote
from DateTime import DateTime

request = container.REQUEST
RESPONSE =  request.RESPONSE
zc = context.portal_catalog

if month == None or year == None:
   if len(traverse_subpath) == 2:
      year, month = traverse_subpath
   else:
      now = DateTime()
      year = now.year()
      month = now.month()

objects = []

# find the end date
next_month = int(month) + 1
next_year = year

if next_month > 12:
   next_month = 1
   next_year = int(next_year) + 1

# find the blog container path
blogpath = context.simpleblog_tool.getObjectPath(context.simpleblog_tool.getStartpoint(context))

startDate = DateTime('%s/%s/1' % (year, month))
endDate = DateTime('%s/%s/1' % (next_year, next_month))

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
