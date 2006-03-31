"""SitemapTool.py
   Provides a management interface for sitemap editting and examination.

   (c) 2004, Nathan R. Yergler, Creative Commons;
   licensed under the GNU GPL v2 or later.
   """

__id__ = "$Id$"

from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from OFS.ObjectManager import ObjectManager
from Globals import InitializeClass
from DateTime import DateTime
from AccessControl import Owned, ClassSecurityInfo
from AccessControl import Unauthorized, getSecurityManager
from Acquisition import aq_parent, aq_base, aq_inner, aq_chain, aq_get
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from ZPublisher.mapply import mapply
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import UniqueObject, getToolByName, format_stx
from Products.CMFCore.Skinnable import SkinnableObjectManager
from Products.CMFPlone import cmfplone_globals
from Products.CMFPlone.PloneFolder import PloneFolder as TempFolderBase
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.PlacelessTranslationService import translate

import zLOG
import Globals

import os, sys
import urllib
import urlparse
import string
import cStringIO as StringIO

class SitemapItem:
    __allow_access_to_unprotected_subobjects__ = 1
    
    security = ClassSecurityInfo()
	
    def __init__(self, sitemap, id, title='', path='', parent=None):
        self.id = self.title  = id
	self.__sm = sitemap
        self.path = path
        self.children = []
        self.parent = parent
	self.title = title
        
        self.vRoot = False
        
    security.declarePublic('getItemId')
    def getItemId(self):
        return self.id

    security.declarePublic('getPath')
    def getPath(self):
        return self.path

    security.declarePublic('getChildren')
    def getChildren(self):
        return self.children

    def addChild(self, newitem):
        newitem.parent = self
        self.children.append(newitem)

    security.declarePublic('getPublishedState')
    def getPublishedState(self):
        return 'published'

    def splitPath(self, path):
        if path[0]=='/':
	   path = path[1:]

	if path == '':
	   return path

	if path[-1] == '/':
	   path = path[:-1]

        return ['cc'] + path.split('/')

    def nearestObj(self, published, portal):
        """Returns the nearest child to the published object."""

        if portal.unrestrictedTraverse(self.splitPath(self.path)) == published:
            return self
        else:
            for child in self.children:
                if child.nearestObj(published, portal):
                    return child.nearestObj(published, portal)

        return None
    
    def asDict(self, includeChildren=True, portalPath=''):
        """Return a dictionary representation of the object"""
        asd = {'id':self.id,
                'title':self.title,
		'translated':translate('SitemapTool', self.id),
                'path':self.path,
                'parent':self.parent,
                }
	if (urlparse.urlparse(str(self.path))[0] != ''):
	   # absolute url
	   asd['realpath'] = self.path
	else:
	   # relative to portal
	   asd['realpath'] = urlparse.urljoin(portalPath, self.path) #portalPath + self.path

	if includeChildren:
	   asd['children'] = [n.asDict(includeChildren=includeChildren, portalPath=portalPath) for n in self.children]
	else:
	   asd['children'] = []

	return asd

    def byPath(self, path, root='/cc'):
        try:
           if path[:len(root)] == root:
	      path = path[len(root):]
	except TypeError, e:
	   return None

	if self.path == path:
	   return self
	else:
	   for child in self.children:
	       if child.byPath(path, root):
	          return child.byPath(path, root)

	return None

    def transMap(self):
        """Returns the item and it's children as a gettext translation map."""
	items=[n.transMap() for n in self.children]

        trans = """# title: %s\nmsgid "%s"\nmsgstr ""\n""" % \
	    (self.title, self.id)
	items.insert(0, trans)

	return "\n".join(items)

class SitemapManager(PloneBaseTool, UniqueObject, SimpleItem, PropertyManager): 
    """ This tool provides some functions for SimpleBlog objects """ 
    id = 'sitemap_tool' 
    meta_type= 'Site map manager' 
    toolicon = 'skins/plone_images/add_icon.gif'
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 0
    use_session=""

    plone_tool = 1
        
    __implements__ = (PloneBaseTool.__implements__,
                      SimpleItem.__implements__, )
    
    manage_options = ( ({'label':'Overview', 'action':'manage_overview'}, 
                        {'label':'Sitemap',  'action':'manage_sitemap'}, 
                        {'label':'i18n',  'action':'manage_i18n'}, 
                        ) + 
                       SimpleItem.manage_options + 
		       PropertyManager.manage_options)

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_overview')
    manage_overview = PageTemplateFile('www/sitemap_overview', globals())
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_sitemap')
    manage_sitemap = PageTemplateFile('www/manage_sitemap',
                                                   globals())
    manage_sitemap.__name__ = 'manage_sitemap'
    manage_sitemap._need__name__ = 0

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_i18n')
    manage_i18n = PageTemplateFile('www/manage_i18n', globals())
    manage_i18n.__name__ = 'manage_i18n'
    manage_i18n._need__name__ = 0

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_add_child_form')
    manage_add_child_form = PageTemplateFile('www/manage_addItem_form',
                                             globals())
    manage_add_child_form.__name__ = 'manage_add_child_form'
    manage_add_child_form._need__name__ = 0
    
    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_edit_child_form')
    manage_edit_child_form = PageTemplateFile('www/manage_editItem_form',
                                                   globals())
    manage_edit_child_form.__name__ = 'manage_edit_child_form'
    manage_edit_child_form._need__name__ = 0

    manage_main = manage_overview

    def __init__(self):
        # initialize the site map container
        self._map = SitemapItem(self, '__root__', path='/', title="nav root")

        # add default properties
        # self.manage_addProperty('i18n domain', '', 'string')
        
    def _getState(self):
        try:
            return self.publishedState
        except:
            return 'published'

    security.declarePublic('getRoot')
    def getRoot(self):
        return self._map

    def _checkChildren(self, childlist, id):
        for item in childlist:
           if item.getItemId() == id:
	      return id
	    
    security.declarePrivate('_findById')
    def _findById(self, id, root):
        if root.id == id:
            return root
        
        for child in root.children:
            if child.getItemId() == id:
                return child
            else:
                inchild = self._findById(id, child)
                if inchild:
                    return inchild

        return None

    security.declarePublic('ById')
    def ById(self, id):
        "Return the item for a particular ID"
        return self._findById(id, self.getRoot())

    security.declarePublic('sameUrl')
    def sameUrl(self, url1, url2):
        if urlparse.urlunsplit(urlparse.urlsplit(url1)) == \
	   urlparse.urlunsplit(urlparse.urlsplit(url2)):
	   return True
	else:
	   return False

    security.declarePublic('rootNav')
    def rootNav(self, include_root=False):
        "Return the root level nav."
        root = self.getRoot()
        result = []

	if include_root:
	   result.append(root.asDict(False, getToolByName(self, 'portal_url')()))
        
        for item in root.children:
	    result.append(item.asDict(False, 
	                  getToolByName(self, 'portal_url')()))

        return result

    security.declarePublic('flatten')
    def flatten(self, include_root=False):

        def _walk_children(result, siteitem, portal_path, prefix=''):
            for item in siteitem.children:
                result.append(item.asDict(includeChildren=False,
                                          portalPath=portal_path))
                result[-1]['title'] = '%s%s' % (prefix, result[-1]['title'])
                _walk_children(result, item, portal_path, prefix=prefix + '-')

        root = self.getRoot()
        result = []

	if include_root:
	   result.append(root.asDict(False,
                                     getToolByName(self, 'portal_url')()))
        _walk_children(result, root, getToolByName(self, 'portal_url')())
        return result
    
    security.declarePublic('crunch_string')
    def crunch_string(self, instr):
        """Return a string all lower case with breaks removed."""
        result = "".join(instr.split()).lower()

        return result

    security.declarePublic('findNearestObj')
    def findNearestObj(self, pub_obj):
        """foo"""
        portal = getToolByName(self, 'portal_url').getPortalObject()
	portal = portal.unrestrictedTraverse('cc')
        return self.getRoot().nearestObj(pub_obj, portal)
    
    security.declarePrivate('_findByPath')
    def _findByPath(self, pub_path):
        """Find the closest match to our current location;
        look for exact url matches first, parent directory matches second,
        peer matches third.
        """
	return self.getRoot().byPath(pub_path)

    security.declarePrivate('_peers')
    def _peers(self, item):
        return item.parent.children

    security.declarePrivate('_isAncestor')
    def _isAncestor(self, ancestorPath, child):
        """Returns true if ancestorPath is accessible by walking up child's
        parents.
        """
        
        while child is not None:
            if child.path != ancestorPath:
                child = child.parent
            else:
                return True

        return False

    security.declarePublic('getUrl')
    def getUrl(self, request, url=None):
        if url is None:
            if hasattr(request, 'VIRTUAL_URL_PARTS'):
                path = getattr(request, 'VIRTUAL_URL_PARTS')[1]
                
                # check if we're called from a manage page
                if 'manage' in path.split('/')[-1]:
                    return '/'.join(path.split('/')[:-1])
                else:
                    return path
        else:
            # XXX
            return url
            
    security.declarePublic('localnav')
    def localnav(self, request):
        result = []

        # find the nearest SitemapItem
        find_path = self.getUrl(request)
        published = current = self._findByPath(find_path)
        #published = current = self._findByPath(request['PATH_TRANSLATED'])

        # walk up the heirarchy to the appropriate second level item
        # (current.parent == self.getRoot())
	if (current is not None) and (current.parent is not None):
            while (current.parent.parent is not None):
                current = current.parent

        # retrieve the entire nav tree for this section as a list of dicts
	if current is not None:
           result = [n.asDict(portalPath=getToolByName(self, 'portal_url')()) 
	             for n in current.children]
	else:
	   result = []

	return result

    security.declarePublic('breadcrumbs')
    def breadcrumbs(self, request):
        result = []

        # find the nearest SitemapItem
        if 'VIRTUAL_URL_PARTS' in request.keys():
           find_path = request['VIRTUAL_URL_PARTS'][1]
        else:
           find_path = [n for n in request['PATH_INFO'].split('/') if n][0]

        current = self._findByPath(find_path)

        if current is not None: current = current.parent

        while current is not None:
            result.append(current.asDict(portalPath=getToolByName(self, 'portal_url')()))
            current = current.parent

        result.reverse()
        return result

        # prune any unnecessary children
	for toplevel in result:
	    if toplevel['path'] == published.path:
	       # this is the actual item we're working with;
               for subitem in toplevel['children']:
                   subitem['children'] = []
	    elif toplevel['parent'] == published:
	       # this is the immediate child of the published object
	       # prune it's children
	       toplevel['children'] = []
            elif self._isAncestor(toplevel['path'], published):
                pass
            else:
                toplevel['children'] = []

	return result

        for current in result:
            if current['id'] == item_path[-1].id:
                # this is the last item, let it through
                # XXX check for expand levels
                pass
            elif current['id'] not in [n.id for n in item_path]:
                current.children = []
                
        return result
    
    security.declarePrivate('_makeId')
    def _makeId(self, title):
        valid_chars = string.letters + string.digits
        id = ''
        
        for char in title:
            if char in valid_chars:
                id = id + char

        return id

    security.declareProtected(CMFCorePermissions.AddPortalContent,
                              'editChild')
    def editChild(self, id, path, title):
        child = self.ById(id)
        
        child.path = path
        child.title = title

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_EditChild')
    def manage_EditChild(self, REQUEST):
        "Process the edit."
        form = REQUEST.form or {}

        self.editChild(form['id'], form['path'], form['title'])
        
	self._p_changed = True

        REQUEST.RESPONSE.redirect('%s/manage_sitemap' % self.absolute_url())

    security.declareProtected(CMFCorePermissions.AddPortalContent,
                              'addChild')
    def addChild(self, parent_id, path, title):
        
        id = '%s.%s' % (parent_id, self._makeId(title))
        newitem = SitemapItem(self, id, path=path, title=title)

        self._findById(parent_id, self.getRoot()).addChild(newitem)
	self._p_changed = True
    
    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_AddChild')
    def manage_AddChild(self, REQUEST):
        """ add a child. """
        form = REQUEST.form or {}

        if ('paths' not in form) or ('titles' not in form):
            err_msg = "You must specify a URL and a title."
            REQUEST.RESPONSE.redirect('%s/manage_sitemap?err_msg=%s' % (
                self.absolute_url(), err_msg))
            
        parent = form['parents'][0]
        path = form['paths'][0]
        title = form['titles'][0]
        
        self.addChild(parent, path, title)

        REQUEST.RESPONSE.redirect('%s/manage_sitemap' % self.absolute_url())

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'deleteItem')
    def deleteItem(self, id):
        to_delete = self._findById(id, self.getRoot())
        td_parent = to_delete.parent

        del td_parent.children[td_parent.children.index(to_delete)]
    
    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_DeleteItem')
    def manage_DeleteItem(self, REQUEST):
        """ delete an item. """
        form = REQUEST.form or {}
        err_msg = None

        if 'ids' not in form:
            err_msg = "You must select an item to delete."
            ids = []
        else:
            ids = form['ids']

        for id in ids:
            # make sure we're not trying to delete the root
            if id == '__root__':
                err_msg = "You can not delete the root item."
                continue

            self.deleteItem(id)
            self._p_changed = True

        if not err_msg:
            REQUEST.RESPONSE.redirect('%s/manage_sitemap' % self.absolute_url())
        else:
            REQUEST.RESPONSE.redirect('%s/manage_sitemap?err_msg=%s' % (
                self.absolute_url(), err_msg))

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'manage_cmf_submit')
    def manage_cmf_submit(self, request):
        form = request.form or {}

        if form.get('action', 'cancel').lower() == 'save':
            # process the form
            if (self.ById(form['parent_id']).path == form['path']):
                return  "Hey! An item can't be it's own parent!"
                
            # first check if this path already exists in the site map
            if self.getRoot().byPath(form['path']):
                self.deleteItem(self.getRoot().byPath(form['path']).id)

            self.addChild(form['parent_id'],
                          form['path'],
                          form['title']
                          )
            
            return 'Saved sitemap information.'
    
InitializeClass(SitemapItem)    
InitializeClass(SitemapManager)

