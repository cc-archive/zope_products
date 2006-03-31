## Script (Python) "month_list"
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

years = {}
lines = []

# find the blog container path
blogpath = context.simpleblog_tool.getObjectPath(context.simpleblog_tool.getStartpoint(context))

results = zc.searchResults(meta_type = 'BlogEntry', 
                           path=blogpath, 
                           review_state='published', 
                           )

for result in results:
   create_date = DateTime(str(result.getObject().creation_date))
   month = (create_date.month(), create_date.Month())
   year = create_date.year()

   if year not in years:
      years[year] = []

   if month not in years[year]:
      years[year].append(month)

year_nums = years.keys()
year_nums.sort()
year_nums.reverse()

for y in year_nums:
   years[y].sort()
   mos = years[y]
   mos.reverse()
   for mo in mos:
      lines.append('<a href="%s/%s/%02d">%s %s</a>' % (request['URL'], y, mo[0], mo[1], y))

return "<br/>".join(lines)
