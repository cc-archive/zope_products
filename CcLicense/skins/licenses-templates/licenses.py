## Script (Python) "licenses.old"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# primary dispatch for the /licenses namespace

# /
# /<license code>/
# /<license code>/<version title>
# /<license code>/<version title>.rdf
# /<license code>/<version title>-rdf-checksum
# /<license code>/<version title>-deed
# /<license code>/<version title>-legalcode
# /<license code>/<version title>-legalcode-checksum
#
# In addition, we must now support the following URLs
#
# /<license code>/<version title>/
# /<license code>/<version title>/rdf
# /<license code>/<version title>/rdf-checksum
# /<license code>/<version title>/legalcode
# /<license code>/<version title>/legalcode-checksum
#
# In addition, we must now support the following URLs
#
# /<license code>/<version title>/<cc>/
# /<license code>/<version title>/<cc>/rdf
# /<license code>/<version title>/<cc>/rdf-checksum
# /<license code>/<version title>/<cc>/legalcode

from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

TARGETS = ('deed', 'deed-music', 'deed-sampling', 'legalcode', 'rdf', 'rdf-checksum', 'legalcode-checksum')

# need the following three values to determine the correct dispatch
license_code = version = target = jurisdiction = language = None

# split up the version and target, if necessary
pieces = request.traverse_subpath

# check if there are no pieces and return the licenses index (HTML)
if len(pieces) == 0:
   template = context.restrictedTraverse('licenses-templates/licenses-index')
   return template.pt_render()

# check if there's only one piece, and return the appropriate index
if len(pieces) == 1:
   if pieces[0].lower() == 'index.rdf':
      # return the RDF for all licenses
      RESPONSE.setHeader('content-type', 'application/rdf+xml')
      print context.license.licenses_rdf()
      return printed
   elif pieces[0].lower() == 'publicdomain':
      # return the public domain deed
      request.form['license_code'] = 'publicdomain'
      request.form['pd'] = True
      template = context.restrictedTraverse('licenses-templates/deed-publicdomain')
      return template.pt_render()

   # check for non-deed pages
   elif pieces[0].lower().find('disclaimer') > -1:
      template = context.restrictedTraverse('engine_templates/%s' % 
                                            pieces[0].lower())
      return template.pt_render()


if len(pieces[1].split('-',1)) > 1:
   pieces = pieces [0] + pieces[1].split('-',1) + pieces[2:]
elif len(pieces[1]) >= 4 and pieces[1][-4].lower() == '.rdf':
   pieces = pieces [0] + pieces[1][:-4] + ['rdf'] + pieces[2:]

# <license code> is always the first element
license_code = pieces[0]

# several ways version title and target may be mixed... check each on in succession
if len(pieces) == 4:
   # non-generic jurisdiction, possible language
   version, jurisdiction, target = pieces[1:]
   if len(target.split('.')) > 1:
      target, language = target.split('.', 1)
elif len(pieces) == 3:
   version, target = pieces[1:]
   if target not in TARGETS:
      if len(target.split('.')) > 1:
         target, language = target.split('.', 1)
      else:
         jurisdiction = target
         target = 'deed'
elif len(pieces) == 2:
   version = pieces[1]
   target = 'deed'

# make sure this is a valid version/license-code/jurisdiction
if jurisdiction is None: jurisdiction = '-'
if version is None or version not in context.deeds_tool.versions(license_code, jurisdiction):
   return 'File not found.'

# we need jurisidiction to be '-' for version checking; 
# if we have a generic jurisdiction, stomp it back to nothign
# if jurisdiction == '-': jurisdiction = ''

# set the values into the request
request.form['target'] = target
request.form['version'] = version
request.form['license_code'] = license_code
request.form['jurisdiction'] = jurisdiction
request.form['language'] = request.form['lang'] = language

# replace '+' with 'plus' before doing traversal so it doesn't trip us up
license_code = license_code.replace('+', 'plus')

# render the appropriate template based on the target
if target == 'legalcode':
   # always serve up UTF-8
   RESPONSE.setHeader('Content-Type', 'text/html; charset=UTF-8')

   # redirect to the XHTML file for that legal document
   if jurisdiction == '-': jurisdiction = ''

   template = context.restrictedTraverse('legalcode/%s' % 
       '_'.join(
           [n for n in [license_code, version, jurisdiction, language] 
              if n and n.strip()]
         )  
       ) 
   return template.pt_render() #document_src(REQUEST=request)

else:
   # check for sampling license
   if license_code.find('sampling') > -1:
      target = 'deed-sampling'
   elif license_code.lower() == 'devnations':
      target = 'deed-devnations'
   elif license_code.upper() == 'LGPL':
      target = 'deed-lgpl'
   elif license_code.upper() == 'GPL':
      target = 'deed-gpl'
   elif license_code.lower() == 'publicdomain':
      target = 'deed-publicdomain'

   if target == 'legalcode-checksum':
      request.form['legalcode'] = '_'.join(
           [n for n in [license_code, version, jurisdiction, language] if n and n.strip()]
         )  

   template = context.restrictedTraverse('licenses-templates/%s' % target)

return template.pt_render()
