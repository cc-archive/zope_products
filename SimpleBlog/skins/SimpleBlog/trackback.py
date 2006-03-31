## Script (Python) "trackback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
response = request.RESPONSE

# extract the necessary bits from the request
title = request.get('title', None)
excerpt = request.get('excerpt', None)
url = request.get('url', None)
blogname = request.get('blog_name', None)

# verify we have the minimal requirements
if url is None:
    # we at least need an URL; return an error condition
    err_msg = "You must supply the URL you are pinging from."
    #context.addTrackback('err!', excerpt, url, blogname)
    
    print """
        <?xml version="1.0" encoding="iso-8859-1"?>
        <response>
        <error>1</error>
        <message>%s</message>
        </response>
    """ % err_msg
else:
    context.addTrackback(title, excerpt, url, blogname)
    print """
        <?xml version="1.0" encoding="iso-8859-1"?>
        <response>
        <error>0</error>
        </response>
    """.strip()

return printed

