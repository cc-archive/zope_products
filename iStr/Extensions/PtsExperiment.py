import Products.PlacelessTranslationService as PTS
import Products.PlacelessTranslationService.PlacelessTranslationService as PTSS
import StringIO

def catalogs(self):
    out = StringIO.StringIO()

    #catalogs = PTS.getTranslationService().getCatalogsForTranslation(None, 'icommons', 'de')
    #print >>out, catalogs
    #print >>out, dir(catalogs[0])
    # _catalog is the actual catalog mapping
    # print >>out, catalogs[0]._catalog
    #print >>out, catalogs[0].info()

    # PTS.getTranslationService().reloadCatalog(catalogs[0])

    # *** start looking here *** 
    product_name = 'iCommons'
    po_file = 'ccweb-en.po'

    pts = self.unrestrictedTraverse('/Control_Panel/TranslationService')
    catalog = getattr(pts, '%s.i18n-%s' % (product_name, po_file))

    print >>out, catalog
    print >>out, dir(catalog)

    print >>out, catalog.reload()
    return out.getvalue()

