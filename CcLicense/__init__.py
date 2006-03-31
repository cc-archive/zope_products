from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path

from config import SKINS_DIR, GLOBALS, PROJECTNAME, product_name
import LicenseEngine
import Deeds

tools = (LicenseEngine.LicenseEngine,Deeds.LicenseDeeds)

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
	init = utils.ToolInit( product_name,
						   tools = tools,
						   product_name = product_name,
						   icon = 'tool.gif',
						   )
						   
	init.initialize(context)
    
