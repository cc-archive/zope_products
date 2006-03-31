import config, os, fnmatch, codecs
from Products.Archetypes.public import *
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View

from Products.CMFCore.utils import UniqueObject, getToolByName

schema =  BaseSchema + Schema((
    ReferenceField('sidebar',
                required=False,
                accessor='Sidebar',
                mutator='setSidebar',
                relationship='KnowsAbout',
                allowed_types=('DocumentSegment',),
                addable=True,
                widget=ReferenceWidget(label='Sidebar', show_content_type=True),
                ),
    TextField('bodyText',
                required=False,
                accessor='BodyText',
                mutator='setBodyText',
                widget=RichWidget(label='Body Text'),
                ),
    ))


class CompositeDocument(BaseContent):
    schema = schema
    security = ClassSecurityInfo()

    actions=(
        {'id':'view',
         'name':'View',
         'action':'string:${object_url}/twocol_view',
         'permission':'View',
         },
        )

    security.declareProtected(View, 'SidebarContent')
    def SidebarContent(self):
       return self.restrictedTraverse(self.Sidebar()).Content()
    
registerType(CompositeDocument)
