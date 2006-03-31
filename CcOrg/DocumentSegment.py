import config, os, fnmatch, codecs
from Products.Archetypes.public import *
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View

from Products.CMFCore.utils import UniqueObject, getToolByName

schema =  BaseSchema + Schema((
     StringField('id',
                 required=0, ## Still actually required, but
                             ## the widget will supply the missing value
                             ## on non-submits
                 mode="rw",
                 accessor="getId",
                 mutator="setId",
                 default=None,
                 widget=IdWidget(
     label="Short Name",
     label_msgid="label_short_name",
     description="Should not contain spaces, underscores or mixed case. "\
     "Short Name is part of the item's web address.",
     description_msgid="help_shortname",
     visible={'view' : 'hidden', 'edit':'hidden'},
     i18n_domain="plone"),
                 ),                           
    TextField('bodyText',
                required=False,
                accessor='Content',
                widget=RichWidget(label='Body Text'),
                ),
    ))


class DocumentSegment(BaseContent):
    schema = schema
    security = ClassSecurityInfo()

    actions=(
        {'id':'view',
         'name':'View',
         'action':'string:${object_url}/docsegment_view',
         'permission':'View',
         },
        )

registerType(DocumentSegment)
