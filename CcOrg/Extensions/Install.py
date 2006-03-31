import os

from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.utils import getToolByName

from Products.CcOrg.config import PROJECTNAME
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from StringIO import StringIO

def install(self):
    """ Install this product """
    out = []

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    out.append("Successfully installed types for %s." % PROJECTNAME)

    skinsTool = getToolByName(self, 'portal_skins')

    out = []
    SKIN_ROOT = 'Products/CcOrg/skins'
    SKINS = [os.path.join(SKIN_ROOT, n) for n in os.listdir(SKIN_ROOT) if 
             os.path.isdir(os.path.join(SKIN_ROOT, n))]
    portal_skins = skinsTool.getSkinSelections()

    for skinlocation in SKINS:
        skinname = skinlocation.split('/')[-1]

        # make sure we're not traversing into version control
        if skinname.lower() in ('cvs', '.svn'):
            continue

        if skinname not in skinsTool.objectIds():
            createDirectoryView(skinsTool, skinlocation, skinname)
            out.append('Added "%s" directory view to portal_skins' % skinname)

        for skin in portal_skins:
            path = skinsTool.getSkinPath(skin)
            path = [ p.strip() for p in path.split(',') ]
            if skinname not in path:
                path.insert(path.index('custom')+1, skinname)

                path = ", ".join(path)
                skinsTool.addSkinSelection(skin, path)
                out.append('Added "%s" to "%s" skins' % (skinname, skin))
            else:
                out.append('Skipping "%s" skin' % skin)

    return "\n".join(out)

