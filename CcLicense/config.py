import os.path

PROJECTNAME = "CcLicense"
SKINS_DIR = 'skins'

GLOBALS = globals()

product_name = 'CcLicense'
plone_product_name = 'License Engine'
meta_type='LicenseEngine'

license_view_permission = 'View License Engine'
unique_id = 'license'

__data_dir = os.path.dirname(os.path.abspath(__file__))

XSLT_SOURCE=os.path.join(__data_dir, 'chooselicense.xsl') 
#'/var/lib/zope/dev/Extensions/chooselicense.xsl'
LICENSE_FILE = os.path.join(__data_dir, 'licenses.xml')
#'/var/lib/zope/dev/Products/CcLicense/Extensions/licenses.xml'   
LICENSES_RDF = os.path.join(__data_dir, 'licenses.rdf')
