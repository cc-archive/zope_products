import config, os, fnmatch, codecs, stat, re, Products.PlacelessTranslationService
from Products.Archetypes.public import *
from AccessControl import ClassSecurityInfo

schema = BaseSchema + Schema((
    StringField('id',
                required=0,
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                widget=IdWidget(
    visible={'view' : 'hidden', 'edit':'hidden'},
    i18n_domain="plone"),
                ),
        StringField('title',
                required=0,
                mode="rw",
                accessor="getTitle",
                mutator="setTitle",
                default=None,
                widget=IdWidget(
    visible={'view' : 'hidden', 'edit':'hidden'},
    i18n_domain="plone"),
                ),
    StringField('language',                         
                required=1,
                accessor='getLanguage',
                mutator='setLanguage',
                widget=StringWidget(label='Language code'),
                )))

                             
class Translation(BaseContent):
    schema = schema

    security = ClassSecurityInfo()

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/translation_view',
        'permissions': (config.VIEW_PERMISSION,),
        'action': 'string:${object_url}/gettext'
        },
               )

    def setLanguage(self, newValue):
        self.language = newValue
        self.setId(self.getLanguage())
        destdir = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, self.getLanguage())
        if not os.path.exists(destdir):
            os.mkdir(destdir, 0777)

    security.declareProtected(config.VIEW_PERMISSION, 'canonicalIds')
    def canonicalIds(self):
        workingpath = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, config.PRIMARY_LANGUAGE)
        return [os.path.splitext(n)[0] for n in fnmatch.filter(os.listdir(workingpath), '*.html')]

    def translatedIds(self):
        workingpath = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, self.getLanguage())
        return [os.path.splitext(n)[0] for n in fnmatch.filter(os.listdir(workingpath), '*.html')]
        

    def getCanonical(self, id):
        destfile = os.path.join(os.path.split(__file__)[0],config.DATA_DIR,config.PRIMARY_LANGUAGE,id+'.html')
        if os.path.exists(destfile):
            return file(destfile).read()
        else:
            return ""
        
    def getTranslated(self, id):
        destfile = os.path.join(os.path.split(__file__)[0],config.DATA_DIR,self.getLanguage(),id+'.html')
        if os.path.exists(destfile):
            return file(destfile).read()
        else:
            return ""

    security.declareProtected(config.EDIT_PERMISSION, 'setTranslated')
    def setTranslated(self, id, new):
        destfile = os.path.join(os.path.split(__file__)[0],config.DATA_DIR,self.getLanguage(),id+'.html')
        f = file(destfile, 'w+')
        f.write(new)
        f.flush()
        self.createPo()
        self.reloadCatalog()

    def reloadCatalog(self):
        product_name = 'iStr'
        po_file = 'icommons-'+self.getLanguage()+'.po'
        pts = self.unrestrictedTraverse('/Control_Panel/TranslationService')
        catalog = getattr(pts, '%s.i18n-%s' % (product_name, po_file))
        catalog.reload()

    def createPo(self): # adapted from istr2po.py
        destdir = os.path.join(os.path.split(__file__)[0],config.DATA_DIR,self.getLanguage())
        files = os.listdir(destdir)
        files.sort()
        buf = ''
        buf += 'msgid ""\n'
        buf += 'msgstr ""\n'
        buf += '"Content-Type: text/plain; charset=UTF-8\\n"\n'
        buf += '"Language-code: '+self.getLanguage()+'\\n"\n'
        buf += '"Language-name: '+self.getLanguage()+'\\n"\n'
        buf += '"Domain: icommons\\n"\n'

        for fname in files:
            if (fname[-5:] != '.html'):
                continue
            f = file(destdir+'/'+fname)
            s = f.read()
            s = re.sub(r'"',r'\\"',s) # escapes " character
            s = re.sub(r'\r\n',r'\n',s) # removes line feeds
            s = re.sub(r'\s+$',r'',s) # removes space at the end of the line
            s = re.sub(r'^\s+',r'',s) # removes spaces at the beginning of the line
            s = re.sub(r'\n',r'\\n',s) # escapes CR
            s = re.sub(r'@(\S+?)@',r'${\1}',s) # converts @ fields @
            msgid = fname[:-5]
            buf += 'msgid "'+msgid+'"\n'
            buf += 'msgstr "'+s+'"\n'
            buf += '\n'
        pofile = file(os.path.join(os.path.split(__file__)[0],config.I18N_DIR,'icommons-'+self.getLanguage()+'.po'), 'w+')
        pofile.write(buf)
        

    def canonicalNewer(self, id):
        canonicalfile = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, config.PRIMARY_LANGUAGE, id+'.html')
        workingfile = os.path.join(os.path.split(__file__)[0], config.DATA_DIR, self.getLanguage(), id+'.html')
        if not os.path.exists(workingfile):
            return False
        else:
            return os.stat(canonicalfile)[stat.ST_MTIME] > os.stat(workingfile)[stat.ST_MTIME]

    def testing(self):
        return Products.PlacelessTranslationService.catalogRegistry

registerType(Translation)
