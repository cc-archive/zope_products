from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.iStr.config import *
from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    ##Import Types here to register them
    import Hello, Translation
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    import IstrTool
    tools = ( IstrTool.IstrTool, )

    utils.ToolInit(
        METATYPE,
        tools=tools,
        product_name=PROJECTNAME,
        icon='tool.gif').initialize(context)
