from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path
import SitemapTool

from Globals import InitializeClass

sitemap_globals = globals()

registerDirectory('skins', sitemap_globals)

def initialize(context):
    utils.ToolInit(
        'Sitemap Tool', 
        tools=(SitemapTool.SitemapManager,),
        product_name='SitemapTool', 
        icon='tool.gif', ).initialize(context)
    
    
    
    
    
