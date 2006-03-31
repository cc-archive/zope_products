import os.path

PROJECTNAME = "CcLicense"
SKINS_DIR = 'skins'

GLOBALS = globals()

product_name = 'CcLicense'
plone_product_name = 'License Engine'
meta_type='LicenseEngine'

license_view_permission = 'View License Engine'
unique_id = 'license'

__prod_dir = os.path.dirname(os.path.abspath(__file__))
__data_dir = os.path.join(__prod_dir, 'api_xml')

XSLT_SOURCE=os.path.join(__data_dir, 'chooselicense.xsl') 
LICENSE_FILE = os.path.join(__data_dir, 'licenses.xml')
LICENSES_RDF = os.path.join(__prod_dir, 'licenses.rdf')
