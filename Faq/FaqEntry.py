import Products.Archetypes.ExtensibleMetadata
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

import string

schema = Products.Archetypes.ExtensibleMetadata.ExtensibleMetadata.schema + \
         Schema((
    StringField('id',
                required=0, ## Still actually required, but
                            ## the widget will supply the missing value
                            ## on non-submits
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                widget=IdWidget(label_msgid="label_name",
                                description_msgid="help_name",
                                visible={'view' : 'invisible',
                                         'edit' : 'hidden'},
                                i18n_domain="plone"),
                ),

    StringField('title',
                required=0,  ## Still required, but calculate it from question
                searchable=1,
                default='',
                accessor='Title',
                widget=StringWidget(label_msgid="label_title",
                                    description_msgid="help_title",
                                    visible={'view' : 'invisible',
                                             'edit' : 'hidden'},
                                    i18n_domain="plone"),
                ),
    StringField('question',
                required = 1,
                searchable = 1,
                mutator='setQuestion',
                widget=StringWidget(label_msgid = "label_question",
                                    description_msgid = "desc_question",
                                    i18n_domain = "faq")
                ),

    TextField('answer',
              required = 1,
              searchable = 1,
              allowable_content_types = ("text/html", "text/structured"),
              widget=TextAreaWidget(description_msgid = "desc_answer",
                                    label_msgid = "label_answer",
                                    i18n_domain = "faq",
                                    rows=6),
              ),
    ))


class FaqEntry(BaseContent):
    """A simple archetype"""
    schema = schema
    archetype_name = 'Faq Entry'
    meta_type = 'FaqEntry'

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'faqentry_view',
        'permissions': (CMFCorePermissions.View,)
        },)

    def __munchTitle(self, title):
        """Munches a title into an ID, removing spaces and 
	other non-url characters."""
        title = title.replace(' ', '_')
	new_id = "".join( [n for n in title 
	                   if (n in string.letters) or 
			      (n in string.digits)] )

	return new_id.lower()

    def setQuestion(self, title):

        # check if we need to reset the ID from it's ugly default
	if self.getId()[:8] == 'faqentry':
	   self.setId(self.__munchTitle(title))
           self.setTitle(self.getId())

        # save the new title.
	self.question = title

registerType(FaqEntry)
