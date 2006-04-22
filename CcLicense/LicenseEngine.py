"""
CcLicense
LicenseEngine.py
$Id$

copyright 2004-2005, Nathan R. Yergler, Creative Commons
licensed to the public under the GNU GPL 2
"""

import lxml.etree
import os
import re
import StringIO

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.PortalContent import PortalContent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PythonScripts.standard import url_unquote_plus, url_quote

from config import meta_type, product_name, plone_product_name
from config import license_view_permission, unique_id
from config import XSLT_SOURCE, LICENSE_FILE, LICENSES_RDF
from xmlcache import XmlCache

class LicenseEngine(PortalContent, UniqueObject, SimpleItem):
	meta_type = 'License Engine'
	id = unique_id
	
	pt_dir = 'skins/engine_templates'
	
	security = ClassSecurityInfo()
	
	def __init__(self):
		pass
	
	def LICENSE_FILE(self):
		if not(hasattr(self, '_v_LICENSE_FILE')):
			self._v_LICENSE_FILE = XmlCache(LICENSE_FILE)
			
		return self._v_LICENSE_FILE()

	def XSLT_SOURCE(self):
		if not(hasattr(self, '_v_XSLT_SOURCE')):
			self._v_XSLT_SOURCE = XmlCache(XSLT_SOURCE)

		return self._v_XSLT_SOURCE()
		
	# user interface dispatch, etc
 	security.declarePublic('__call__')
        def __call__(self):
            """Perform a restricted traverse to the engine's index page;
            this allows it to exist in the filesystem or ZODB."""
            return self.unrestrictedTraverse('engine_templates/engine_index_html').pt_render()

 	security.declarePublic('index_html')
        index_html = __call__ #PageTemplateFile(os.path.join(pt_dir, 'engine_index_html.pt'), globals())
	# __call__ = index_html 

	# core engine methods
 	security.declarePublic('workRdf')
 	def workRdf(self, license_url, title=None, creator=None, copyright_holder=None, copyright_year=None, description=None, format=None, work_url=None, source_work_url=None):
		# Takes the work metadata values and combines them with the license RDF;
		# returns a string containg the full RDF.
		
		WORK_FORMATS = {'Other':None,
				'Audio':'Sound',
				'Video':'MovingImage',
				'Image':'StillImage',
				'Text':'Text',
				'Interactive':'InteractiveResource'
				}
		
		if format in [n.lower() for n in WORK_FORMATS.keys()]:
		   # this is an non-DC format
		   format = WORK_FORMATS[format.lower().capitalize()]
		
		# generate the work RDF
		work_rdf = ''
		if title:
		   work_rdf += '\t<dc:title>'+ title + '</dc:title>\n'
				
		if copyright_year:
		   work_rdf += '\t<dc:date>' + copyright_year + '</dc:date>\n'
		
		if description:
		   work_rdf += '\t<dc:description>'+ description + '</dc:description>\n'
		
		if creator:
		   work_rdf += '\t<dc:creator><Agent><dc:title>'+ creator + \
					   '</dc:title></Agent></dc:creator>\n'
				
		if copyright_holder:
		   work_rdf += '\t<dc:rights><Agent><dc:title>' + copyright_holder + \
					   '</dc:title></Agent></dc:rights>\n'
		
		if format:
		   work_rdf += '\t<dc:type rdf:resource="http://purl.org/dc/dcmitype/%s" />\n' % format
					
		if source_work_url:
		   work_rdf += '\t<dc:source rdf:resource="%s" />\n' % (source_work_url)
		
		if work_rdf:
		   work_rdf = '\n%s' % work_rdf[:-1]
		
		rdf = """
		<Work rdf:about="">
		\t<license rdf:resource="%s" />%s
		</Work>
		""" % (license_url, work_rdf)
		
		return rdf
 	
 	security.declarePublic('licenseUrlToCode')
 	def licenseUrlToCode(self, lurl):
		# Takes a license URL and converts it to a license code + jurisdiction.
		# Returns a tuple of (code, jurisdiction, version)
		
		pieces = [n for n in lurl.split('/') if n.strip()]
		pieces.reverse()
	
		if (pieces[0].lower() == 'publicdomain'):
 		   return (pieces[0], '', 0)

		# find out if we have a jurisdiction
		try:
		   version = float(pieces[0])
		
		   # no jurisdiction
		   jurisdiction = ''
		   code = pieces[1]
		except:
		   # jurisidiction present
		   jurisdiction = pieces[0]
		   version = float(pieces[1])
		   code = pieces[2]
		
		return (code, jurisdiction, version)
 	
 	security.declarePublic('licenseRdf')
	def licenseRdf(self, issue_xml):
	
		START = "<licenserdf>"
		END = "</licenserdf>"
		
		rdf_block = issue_xml[ issue_xml.find(START) + len(START) : issue_xml.find(END) ]
		
		# strip out any blank lines
		rdf_lines = [n for n in rdf_block.split('\n') if n.strip()]
		
		# apply proper formatting
		if len(rdf_lines) > 1:
		   rdf_lines[0] = rdf_lines[0].strip()
		   rdf_lines[1] = rdf_lines[1].strip()
		   rdf_lines[-1] = rdf_lines[-1].strip()
		   rdf_lines[-2] = rdf_lines[-2].strip()
		
		for i in range(2,len(rdf_lines) - 2):
		   rdf_lines[i] = "   %s %s" % (rdf_lines[i].strip()[:-2], rdf_lines[i].strip()[-2:])
		
		firstlines = rdf_lines[0].split(' ')
		rdf_lines.insert(1, "    %s" % firstlines[-1])
		rdf_lines[0] = " ".join(firstlines[:-1])
		
		rdf_lines.append('')
		
		return "\n".join(rdf_lines)
	
	security.declarePublic('licenseCodeToUrl')
	def licenseCodeToUrl(self, code, jurisdiction='', version=2.0):
		"""Generates a license URL from the code and jurisdiction;
		defaults to the current license version."""
		
		lurl = 'http://creativecommons.org/licenses/%s/%s/%s' % (code, version, jurisdiction)
		if lurl[-1] != '/':
		   lurl = '%s/' % lurl
		
		return lurl
	
	security.declarePublic('licenseCodeToAnwers')
	def licenseCodeToAnswers(self, licenseCode, jurisdiction='', version=None, locale=''):
		"""Takes an old style license code (ie, by-nc-nd) and
		generates the appropriate answers.xml string for parsing
		by chooselicense.xsl.
		"""
		
		answers = {'jurisdiction':jurisdiction}
		pieces = [n.strip() for n in licenseCode.split('-')]
		
		# check for explicit version
		if version is not None: answers['version'] = version

		# determine the license type
		is_samp = len([n for n in pieces if n.find('sampling') > -1]) > 0
		is_pd = ('pd' in pieces)
		is_gpl = ('gpl' in [n.lower() for n in pieces])
		is_lgpl = ('lgpl' in [n.lower() for n in pieces])
		is_devnations = ('devnations' in pieces)
		is_plain = not(is_samp or is_pd or is_gpl or is_lgpl or is_devnations)
		
		# munch the pieces
		if is_samp:
		   # this is a sampling license
		   answers['sampling'] = [n for n in pieces if n.find('sampling') > -1][0]
                   # convert '+' to 'plus'
                   answers['sampling'] = answers['sampling'].replace('+', 'plus')
                   # we split out [nc|sampling+] so we need to check that case
                   if 'nc' in pieces:
                      answers['sampling'] = 'ncsamplingplus'
		
		# generate and return the XML
		for p in pieces:
		   # check for derivatives status
		   if p in ['nd', 'sa']:
			  if p == 'nd':
				 answers['derivatives'] = 'n'
			  else:
				 answers['derivatives'] = p
		
		   if p == 'nc':
			  answers['commercial'] = 'n'
		
		if is_plain:
		   lclass = 'standard'
		elif is_samp:
		   lclass = 'recombo'
		elif is_pd:
		   lclass = 'publicdomain'
		elif is_gpl:
		   lclass = 'gpl'
		elif is_lgpl:
		   lclass = 'lgpl'
		elif is_devnations:
		   lclass = 'devnations'
		
		xml = """<answers>
		<locale>%s</locale>
		<license-%s>
		%s
		</license-%s>
		</answers>""" % (locale, lclass, 
						 "\n".join(["<%s>%s</%s>" % (n, answers[n], n) for n in answers.keys()]),
						 lclass)
		
		return xml

	security.declarePublic("issue_partner")
	def issue_partner(self, request=None):
		if request is None:
			request = self.REQUEST

		RESPONSE =  request.RESPONSE
		
		license = self.issue(request)
		
		# determine the license selection
		license_url = deed_url = license['deed']
		license_name = license['name']
		license_button = license['imageurl']
		
		# compute the new exit url
                try:
   			exit_url = url_unquote_plus(request['exit_url'])
			exit_url = exit_url.replace('[license_url]', url_quote(license_url))
			exit_url = exit_url.replace('[license_name]', license_name)
			exit_url = exit_url.replace('[license_button]', url_quote(license_button))
			exit_url = exit_url.replace('[deed_url]', url_quote(deed_url))
		except:
			exit_url = ""
		return {'name':license_name,
			'deed_url':deed_url,
			'exit_url':exit_url,
			}
	
	security.declarePublic("issue")
	def issue(self, request=None):
		if request is None:
			request = self.REQUEST

		RESPONSE =  request.RESPONSE
		
		jurisdiction = ''
		locale = request.get('lang', '')
		
		if request.has_key('pd') or request.has_key('publicdomain') or (request.has_key('license_code') and request['license_code'] == 'publicdomain'):
		   # this is public domain
		   answers="""<answers>
		   <license-publicdomain />
		</answers>
		"""
		
		# check for license_code
		elif request.has_key('license_code'):
		   jurisdiction = (('jurisdiction' in request.keys()) and (request['jurisdiction'])) or \
						  (('field_jurisdiction' in request.keys()) and (request['field_jurisdiction'])) or \
						  ''
		   answers = self.licenseCodeToAnswers(request['license_code'], jurisdiction, version = request.form.get('version', None), locale=locale)
		
		else:
		   jurisdiction = ('field_jurisdiction' in request.keys() and request['field_jurisdiction']) or jurisdiction
		
		   # this is plain-jane CC
		   answers = u"""<answers>
			<locale>%s</locale>
			<license-standard>
			  <jurisdiction>%s</jurisdiction>
			  <commercial>%s</commercial>
			  <derivatives>%s</derivatives>
			<version>%s</version>
		   </license-standard>
		</answers>
		""" % (locale, jurisdiction, request['field_commercial'], request['field_derivatives'], ('version' in request.form and request['version'] or ''))
		
		# generate the license RDF, etc
		license_xml, license_name, license_uri, license_img, licenseonlyrdf = self.license_xslt(answers)
		file('output.log', 'w').write(answers)

		license_rdf = self.html_comment(license_xml)
		
		# generate the work RDF
		work_rdf = self.workRdf(license_url = license_uri,
										title= (request.has_key('field_worktitle') and request['field_worktitle']) or None,
										creator= (request.has_key('field_creator') and request['field_creator']) or None,
										copyright_holder= (request.has_key('field_copyrightholder') and request['field_copyrightholder']) or None,
										copyright_year= (request.has_key('field_year') and request['field_year']) or None,
										description= (request.has_key('field_description') and request['field_description']) or None,
										format= (request.has_key('field_format') and request['field_format']) or None,
										work_url= (request.has_key('work_url') and request['work_url']) or None,
										source_work_url= (request.has_key('field_sourceurl') and request['field_sourceurl']) or None
									   )
		old_workurl = """<Work rdf:about=""><license rdf:resource="%s"/></Work>""" % license_uri
		license_rdf = license_rdf.replace(old_workurl, work_rdf)
		
		license = {'name':license_name,
			   'deed':license_uri,
			   'licenserdf': licenseonlyrdf,
			   'issue_xml':license_xml,
			   'imageurl':license_img,
			   'jurisdiction':jurisdiction,
			   'rdf':license_rdf,
			  }
		
		return license
	
	security.declarePublic("html_comment")
	def html_comment(self, xml_doc):
		"""Strip the <html> tags from the html xml element returned
		by the web service."""
		
		START = '<html>'
		END = '</html>'
		
		return xml_doc[xml_doc.find(START) + len(START):xml_doc.find(END)]
	
	security.declarePublic("getLicenseWorkRdf")
	def getLicenseWorkRdf(self, license_url, title=None, creator=None, 
			      copyright_holder=None, copyright_year=None, 
			      description=None, format=None, work_url=None, 
			      source_work_url=None):
		WORK_FORMATS = {'Other':None,
						'Audio':'Sound',
						'Video':'MovingImage',
						'Image':'StillImage',
						'Text':'Text',
						'Interactive':'InteractiveResource'
					   }
		
		if format in [n.lower() for n in WORK_FORMATS.keys()]:
		   # this is an non-DC format
		   format = WORK_FORMATS[format.lower().capitalize()]
		
		# generate the work RDF
		work_rdf = ''
		if title:
		   work_rdf += '\t<dc:title>'+ title + '</dc:title>\n'
				
		if copyright_year:
		   work_rdf += '\t<dc:date>' + copyright_year + '</dc:date>\n'
		
		if description:
		   work_rdf += '\t<dc:description>'+ description + '</dc:description>\n'
		
		if creator:
		   work_rdf += '\t<dc:creator><Agent><dc:title>'+ creator + \
					   '</dc:title></Agent></dc:creator>\n'
				
		if copyright_holder:
		   work_rdf += '\t<dc:rights><Agent><dc:title>' + copyright_holder + \
					   '</dc:title></Agent></dc:rights>\n'
		
		if format:
		   work_rdf += '\t<dc:type rdf:resource="http://purl.org/dc/dcmitype/%s" />\n' % format
					
		if source_work_url:
		   work_rdf += '\t<dc:source rdf:resource="%s" />\n' % (source_work_url)
		
		if work_rdf:
		   work_rdf = '\n%s' % work_rdf[:-1]
		
		self.REQUEST.form['license_code'], self.REQUEST.form['jurisdiction'], self.REQUEST.form['version'] = self.licenseUrlToCode(license_url)
	
		# strip outter tags off license rdf
		lrdf = self.issue()['licenserdf']
		extract = re.compile('<license .*</license>', re.M|re.S|re.I).search(lrdf)
		lrdf = lrdf[extract.start():extract.end()]

		rdf = """
		<rdf:RDF xmlns="http://web.resource.org/cc/"
			xmlns:dc="http://purl.org/dc/elements/1.1/"
			xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
		<Work rdf:about=""
		\t<license rdf:resource="%s" />%s
		</Work>
		
		%s
		
		</rdf:RDF>
		""" % (license_url, work_rdf, lrdf)
		
		return rdf
		
	security.declarePublic("license_xslt")
	def license_xslt(self, answers):
	   """Returns a tuple containing an XML document, html, the license URL and
	   the license name."""
	
	   answers = lxml.etree.parse(StringIO.StringIO(answers))
	
	   # parse the stylesheet
	   transform = lxml.etree.XSLT( self.XSLT_SOURCE() )

	   # apply the stylesheet to the answers
	   result = transform.apply(answers)
	
	   # get the license info XML
	   license_xml = lxml.etree.tostring(result.getroot())
	
	   # extract the license information
	   name = result.xpath('//license-name')[0].text
	
	   uri = result.xpath('//license-uri')[0].text
	   rdf = lxml.etree.tostring(result.xpath('//rdf')[0])
	   licenserdf = lxml.etree.tostring(result.xpath('//licenserdf')[0])
	   img_src = result.xpath('//html/a/img/@src')[0]

	   return (license_xml, name, uri, img_src, licenserdf)

	security.declarePublic("languageJurisdiction")
	def languageJurisdiction(self, lang, jurisdiction=None):
	   """Returns the default jurisdiction for a language,
	   or the specififed jurisdiction."""

           if jurisdiction != None:
              return jurisdiction

           lang_country = re.split('[-_]',lang)
           if len(lang_country) == 2:
              lang = lang_country[0]+'_'+lang_country[1].upper()

	   license_doc = self.LICENSE_FILE()
	
	   langs = license_doc.xpath('//jurisdiction-info/languages')

	   for l in langs:
	      if lang in l.text.split():
	         juris = l.xpath('../@id')
                 if juris and len(juris) > 0:
                    return juris[0]

	   return None

	security.declarePublic("jurisdictionLanguages")
	def jurisdictionLanguages(self, jurisdiction):
	   """Returns a list of default languages for a jurisdiction."""
	   result = {}
	   
	   license_doc = self.LICENSE_FILE()

	   js_langs = license_doc.xpath("//jurisdiction-info[@id='%s']/"
					"languages" % jurisdiction)

	   if js_langs:
		   return js_langs[0].text.split()
	   else:
		   return []


	security.declarePublic("jurisdictions")
	def jurisdictions(self, launched=False):
	   """Returns a list of license jurisdictions.  If launched is
	   False, all jurisdictions will be returned, including those still
	   in the planning phase.  If True, only jurisdictions which have
	   produced licenses will be returned."""
	   
	   result = []
	   
	   license_doc = self.LICENSE_FILE()
	
	   js = license_doc.xpath('//jurisdiction-info')

	   for j in js:
	       j_id = j.xpath('./@id')[0]

	       j_info = {'id':j_id}
	       j_info['uri'] = j.xpath('./uri')[0].text
	       j_info['launched'] = (j.xpath('./@launched')[0] == 'true')

	       result.append((j_id, j_info))

	   if launched:
	       result = [n for n in result if n[1]['launched']]

	   # sort the result by country code
	   result.sort( lambda x,y: cmp(x[0], y[0]) )

	   return result

	security.declarePublic("jurisdictions")
	def licenses_rdf(self, ):
           return file(LICENSES_RDF).read()

InitializeClass(LicenseEngine)
