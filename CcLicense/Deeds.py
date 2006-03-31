"""
CcLicense
LicenseEngine.py
$Id$

copyright 2004-2005, Nathan R. Yergler, Creative Commons
licensed to the public under the GNU GPL 2
"""

import lxml.etree
#import libxml2
#import libxslt
import sha
import os

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.ObjectManager import ObjectManager

from config import meta_type, product_name, plone_product_name
from config import license_view_permission, unique_id
from config import LICENSE_FILE

class LicenseDeeds(UniqueObject, SimpleItem):
    meta_type = 'License Deeds Support Tool'
    id = 'deeds_tool'

    pt_dir = 'skins/engine_templates'

    security = ClassSecurityInfo()

    def __init__(self):
        pass

    # support methods
    def versions(self, code, jurisdiction='-'):
        doc = lxml.etree.parse(file(LICENSE_FILE, 'r'))
        res = doc.xpath("//license[@id='%s']/jurisdiction[@id='%s']/version/@id" % (code, jurisdiction) )

        return [n.text for n in res]

    def latestVersion(self, code, jurisdiction='-'):
        return max(self.versions(code, jurisdiction))

    def versionUrl(self, code, jurisdiction, version):
        doc = lxml.etree.parse(file(LICENSE_FILE, 'r'))
        res = doc.xpath("//license[@id='%s']/jurisdiction[@id='%s']/version[@id='%s']/@uri" % (code, jurisdiction,version) )

        if len(res) > 0:
            return res[0].text

    def sha1_hexdigest(self, in_str):
        sha1 = sha.new(in_str)
        return sha1.hexdigest().upper()

InitializeClass(LicenseDeeds)
