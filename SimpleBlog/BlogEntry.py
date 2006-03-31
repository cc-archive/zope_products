from Products.Archetypes.public import BaseSchema, BaseFolderSchema, Schema
from Products.Archetypes.public import StringField, TextField, LinesField, BooleanField, ImageField, FileField
from Products.Archetypes.public import TextAreaWidget, VisualWidget,  MultiSelectionWidget, StringWidget, IdWidget, ImageWidget, FileWidget
from Products.Archetypes.public import RichWidget, BooleanWidget
from Products.Archetypes.public import BaseContent, registerType, BaseFolder
from Products.CMFCore import CMFCorePermissions
from Products.CMFDefault.Image import addImage

from DateTime import DateTime
import Permissions

import PIL.ImageFile
import string
import cStringIO as StringIO

schema = BaseFolderSchema +  Schema((
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
    StringField('title',
                required=1,
                searchable=1,
                default='',
                accessor='Title',
		mutator='setTitle',
                widget=StringWidget(label_msgid="label_title",
                                    description_msgid="help_title",
                                    i18n_domain="plone"),
                ),    
    StringField('trackback_rdf',
    		required=0,
		searchable=0,
		visible=0,
		mode='r',
		accessor='getTBrdf',
		),
    StringField('description',
                searchable=1,
                isMetadata=1,
                accessor='Description',
                widget=TextAreaWidget(label='Description', 
                       visible={'view' : 'hidden', 'edit':'hidden'},
		       description='Give a description for this SimpleBlog.'),),
    TextField('body',
              searchable=1,
              required=0,
              mutator='setBody',
              primary=1,
              default_content_type='text/html',
              default_output_type='text/html',
              allowable_content_types=('text/plain','text/structured', 'text/html',),
              widget=RichWidget(label='Body')),
    BooleanField('makeThumbnail',
                 searchable=0,
                 isMetadata=0,
                 mutator='setMakeThumbnail',
                 mode='w',
                 widget=BooleanWidget(
    label='Make thumbnail.',
    description='If checked, a thumbnail of the Picture will be created.')),

    ImageField('blogImage',
                searchable=0,
                isMetadata=0,
                mutator='setBlogImage',
		mode='w',
                widget=ImageWidget(label='Picture', 
		       description='Add an image to this blog entry.'),),
    LinesField('categories',
                    accessor='EntryCategory', 
                    edit_accessor='EntryCategory', 
                    index='KeywordIndex', 
                    vocabulary='listCategories',
                    widget=MultiSelectionWidget(format='select', label='Categories', description='Select to which categories this Entry belongs to')),

    BooleanField('alwaysOnTop', 
             default=0,
             index='FieldIndex:schema',
             widget=BooleanWidget(label='Entry is always listed on top.', description='Controls if the Entry (when published) shown as the first Entry. If not checked, the effective date is used.')),
              ),
                                  )

class BlogEntry(BaseFolder):
    """
    A BlogEntry can exist inside a SimpleBlog Folder or an EntryFolder
    """

    schema = schema

    global_allow=0
    
    content_icon='entry_icon.gif'
    
    filter_content_types=1
    allowed_content_types=('Link', 'Image', 'File')
    
    actions = ({
       'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/blogentry_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'references',
          'name': 'References',
          'action': 'string:${object_url}/reference_edit',
          'permissions': (CMFCorePermissions.ModifyPortalContent,),
          'visible':0},
        {'id': 'trackback',
          'name': 'Trackback',
          'action': 'string:${object_url}/trackback',
          'permissions': (CMFCorePermissions.View,),
          'visible':0},
        {'id': 'metadata',
          'name': 'Properties',
          'action': 'string:${object_url}/base_metadata',
          'permissions': (CMFCorePermissions.ModifyPortalContent,),
          'visible':0})

    def __munchTitle(self, title):
        """Munches a title into an ID, removing spaces and 
	other non-url characters."""
	new_id = "".join( [n for n in title 
	                   if (n in string.letters) or 
			      (n in string.digits)] )

	return new_id.lower()

    def setTitle(self, title):

        # check if we need to reset the ID from it's ugly default
	if self.getId()[:9] == 'blogentry':
	   self.setId(self.__munchTitle(title))

        # save the new title.
	self.title=title

    def setMakeThumbnail(self, makeTn):
        self.__makeTn = makeTn
        
    def setBlogImage(self, image):
        # determine the image identifier
	self._img_count = getattr(self, '_img_count', 0) + 1
        img_id = 'blog_image_%s' % self._img_count

	# upload the file
    	filedata = image.read()
        addImage(self, img_id,
	         title=img_id, file=filedata)

        # make the thumbnail, if necessary
        if self.__makeTn:
	    p = PIL.ImageFile.Parser()
	    p.feed(filedata)
	    thumbnail = p.close()
            # thumbnail = PilImage.open(StringIO.StringIO(getattr(self,img_id).data))
	    #StringIO.StringIO(filedata))
            thumbnail.thumbnail((200,200))

            thumbnail_data = StringIO.StringIO()
            thumbnail.save(thumbnail_data, 'JPEG')

            # create the thumbnail in the ZODB
            addImage(self, '%s_thumbnail' % img_id,
                     title = '%s_thumbnail' % img_id,
                     file=thumbnail_data.getvalue()
                     )

            # set the body text
            self.setBody("\n".join(
                (self.getBody(),
                 '<a href="%s/%s"><img alt="%s" src="%s/%s_thumbnail" /></a>' %
                 (self.absolute_url(), img_id, img_id,
                  self.absolute_url(), img_id)
                 )
                )
                         )

            # reset the make thumbnail flag
            self.__makeTn = False
        else:
            # append the url to the end of the entry body
            self.setBody("\n".join(
                (self.getBody(),
                 '<img alt="%s" src="%s/%s" />' %
                 (img_id, self.absolute_url(), img_id)
                 )
                )
                         )
    
    def getTBrdf(self, comment=False):
    	rdf = """
	<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
	         xmlns:dc="http://purl.org/dc/elements/1.1/"
		 xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/">
	  <rdf:Description
	      rdf:about="%s"
	      dc:identifier="%s"
	      dc:title="%s"
              trackback:ping="%s/trackback" />
	</rdf:RDF>
	""" % (self.absolute_url(), self.absolute_url(), 
	       self.title, self.absolute_url() )

	if comment:
	   return "<!-- %s -->" % rdf
	else:
	   return rdf

    def addTrackback(self, title, excerpt, url, blog_name):
        ping = (title, excerpt, url, blog_name, DateTime('US/Pacific'))

	try:
	   self.trackback_pings.append(ping)
	except:
	   self.trackback_pings = [ping,]

    def getTB(self):
        try:
	   return self.trackback_pings
	except:
	   return []

    def setBody(self, newbody):
        # store the new body text
        self.body = newbody

        # ping any urls contained in the body

    def getAlwaysOnTop(self):
        if hasattr(self, 'alwaysOnTop'):
            if self.alwaysOnTop==None or self.alwaysOnTop==0:
                return 0
            else:
                return 1
        else:
            return 0
            
    def getIcon(self, relative_to_portal=0):
        try:
            if self.getAlwaysOnTop()==0:
                return 'entry_icon.gif'
            else:
                return 'entry_pin.gif'
        except:
            return 'entry_icon.gif'
        
    def listCategories(self):
        # traverse upwards in the tree to collect all the available categories
        # stop collecting when a SimpleBlog object is reached
        
        cats=[]
        parent=self.aq_parent
        portal=self.portal_url.getPortalObject()
        
        while parent!=portal:
           if parent.portal_type=='Blog' or parent.portal_type=='BlogFolder':
               # add cats
               pcats=parent.categories
               for c in pcats:
                   if c not in cats:
                       cats.append(c)
               if parent.portal_type=='Blog':
                   break
           parent=parent.aq_parent
           
        # add the global categories
        for c in self.simpleblog_tool.getGlobalCategories():
            if not c in cats:
                cats.append(c)           
        cats.sort()
        return tuple(cats)

    def start(self):
        return self.getEffectiveDate()
        
    def end(self):
        """ 
        return the same data as start() since an entry is not an event but an item that is published on a specific
        date. We want the entries in the calendar to appear on only one day.
        """
        return self.getEffectiveDate()

    def entryDate(self, format='%B %d, %Y'):
        """Returns the entry's date, formatted for display."""
	return self.start().strftime(format)

registerType(BlogEntry)
