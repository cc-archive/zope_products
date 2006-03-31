import os, config, stat

# Zope
from OFS import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo

## BEGIN Zope tool/product
## Uncomment this block to make it a plain Zope product/tool
#class IstrTool(PropertyManager, SimpleItem.SimpleItem):
## END Zope tool/product

# BEGIN Plone tool
# Comment out this block if you want a plain Zope product/tool
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.ActionProviderBase import ActionProviderBase

class IstrTool(UniqueObject, PropertyManager, 
               SimpleItem.SimpleItem, ActionProviderBase):
# END Plone tool

    "The IstrTool tool"

    meta_type = 'IstrTool'

    id = 'IstrTool'
    
    manage_options = PropertyManager.manage_options + \
                     SimpleItem.SimpleItem.manage_options + (
        {'label': 'View', 'action': 'index_html',},
        )
    
    _properties = (
        {'id':'title', 'type':'string', 'mode':'w'},
        )
    
    # Standard security settings
    security = ClassSecurityInfo()
    
    security.declareProtected('Manage properties', 'index_html')
    index_html = PageTemplateFile('zpt/index_html', globals())
    
    #####################################################
    # Constructor functions, only used when adding class
    # to objectManager
    
    def manage_addAction(self, REQUEST=None):
        "Add tool instance to parent ObjectManager"
        id = IstrTool.id
        self._setObject(id, IstrTool())
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
        
    constructors = (manage_addAction,)

    # returns a list of allLanguages available, includes a hack to remove the CVS directory
    def allLanguages(self):
        destdir = os.path.join(os.path.split(__file__)[0],config.DATA_DIR)
        languages = []
        for path in os.listdir(destdir):
            fullpath = os.path.join(destdir,path)
            st = os.lstat(fullpath)
            if stat.S_ISDIR(st[stat.ST_MODE]):
                languages.append(path)
        # remove CVS directory
        if 'CVS' in languages:
            languages.remove('CVS')
        languages.sort()
        return languages
        
    # returns the string of the translation, lang is just the string of the language identifier
    def getTranslation(self, lang, id):
        destfile = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, lang, id+'.html')
        if os.path.exists(destfile):
            return file(destfile).read()
        else:
            return ""
        
    # checks if canonical language is newer than lang for id
    def canonicalNewer(self, lang, id):
        canonicalfile = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, config.PRIMARY_LANGUAGE, id+'.html')
        workingfile = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, lang, id+'.html')
        if not os.path.exists(workingfile):
            return False
        else:
            return os.stat(canonicalfile)[stat.ST_MTIME] > os.stat(workingfile)[stat.ST_MTIME]

    def defaultLanguages(self, current):
        if len(current) > 0:
            return current
        elif self.getLanguage() == config.PRIMARY_LANGUAGE:
            return [config.PRIMARY_LANGUAGE]
        else:
            returnList = [config.PRIMARY_LANGUAGE, self.getLanguage()]
            returnList.sort()
            return returnList
