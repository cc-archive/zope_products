## Script (Python) "generateUniqueId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##
from DateTime import DateTime
from random import random
request = container.REQUEST

now=DateTime()
time='%s.%s' % (now.strftime('%Y-%m-%d'), str(now.millis())[7:])
rand=str(random())[2:6]
prefix=''
suffix=''

if type_name is not None:
    # check for BlogEntry
    if type_name == 'BlogEntry':
       context.counter.manage_changeProperties(REQUEST=request, 
           last_id=context.counter.getProperty('last_id') + 1 )
       return str(context.counter.getProperty('last_id'))

    # else
    prefix = type_name.replace(' ', '_')+'.'
prefix=prefix.lower()

return prefix+time+rand+suffix
