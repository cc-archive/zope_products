"""\
$Id$

copyright 2004, Nathan R. Yergler, Canterbury School
based on work under license from Zope Corp. (CMFCalendar/Extensions/Install.py)

"""

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName, ToolInit

# from Products.Stoa import stoa_globals, stoa_fti
from Products.SitemapTool import sitemap_globals

from Acquisition import aq_base
from cStringIO import StringIO
import string

def install(self):
    "Register the SitemapTool directory views and content types."
    
    out = StringIO()
    typestool = getToolByName(self, 'portal_types')
    skinstool = getToolByName(self, 'portal_skins')
    metadatatool = getToolByName(self, 'portal_metadata')
    catalog = getToolByName(self, 'portal_catalog')
    portal_url = getToolByName(self, 'portal_url')

    # Setup the skins
    # This is borrowed from CMFDefault/scripts/addImagesToSkinPaths.pys
    if 'SitemapTool' not in skinstool.objectIds() :
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews(skinstool, 'skins', sitemap_globals)
        out.write("Added directory views to portal_skins\n")

    # Now we need to go through the skin configurations and insert
    # the skin folders into the configurations.
    # YES THE ORDER HERE DOES MATTER!
    skins_folders = ('SitemapTool',)

    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))

	for folder in skins_folders:
           if folder not in path:
                
               try: 
                   path.insert(path.index('zpt_content'), folder)
               except ValueError:
                   pass
            
               str_path = string.join(path, ', ')

               # addSkinSelection will replace existing skins as well.
               skinstool.addSkinSelection(skin, str_path)
               out.write("Added '%s' to %s skin\n" % (folder,skin))
           else:
               out.write("Skipping %s skin, '%s' is already set up\n" % (
                   skin, folder))

    return out.getvalue()
