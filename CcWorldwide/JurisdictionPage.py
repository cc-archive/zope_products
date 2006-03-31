from Products.CcWorldwide.config import STATUS_LEVEL
from Products.Archetypes.public import BaseFolderSchema, Schema
from Products.Archetypes.public import StringField, TextField, FileField, LinesField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, FileWidget, LinesWidget, StringWidget, IdWidget
from Products.Archetypes.public import registerType, BaseFolder
from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.CMFCore import CMFCorePermissions
from config import PROJECTNAME

schema = BaseFolderSchema +  Schema((
    StringField('title',
                required=0,
                mode="rw",
                default=None,
                widget=IdWidget(visible={'view' : 'hidden', 'edit':'hidden'}),
                ),
    StringField('id',
                required=1,
                ),
    StringField('status',
		required=1,
                vocabulary=STATUS_LEVEL,
                widget=SelectionWidget(),
                ),
    StringField('partner',
		required=1,
                searchable=1,
                widget=StringWidget(),
                ),
    TextField('leads',
	      required=1,
              default_output_type='text/html',
              widget=TextAreaWidget(label="Jurisdiction project leads"),
              ),
    TextField('materials',
              default_output_type='text/html',
              widget=TextAreaWidget(label='Jurisdiction materials'),
              ),
    TextField('partnerblurb',
              searchable=1,
              required=1,
              default_output_type='text/html',
              widget=TextAreaWidget(label='Partner Blurb'),
              ),
    TextField('acknowledgements',
              searchable=1,
              required=0,
              default_output_type='text/html',
              widget=TextAreaWidget(label='Acknowledgements'),
              ),
    ))

class JurisdictionPage(BaseFolder):

    schema = schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/article_view',
        'permissions': (CMFCorePermissions.View,)
        },
               {
        'id': 'contents',
        'name': 'Contents',
        'action': 'string:${object_url}/folder_contents',
        'permissions': (CMFCorePermissions.AddPortalContent,)
        }
               )

registerType(JurisdictionPage, PROJECTNAME)
