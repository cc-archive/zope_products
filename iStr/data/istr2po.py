#!/usr/bin/env python

# istr2po.py [directory ...]
# dumps corresponding .po files in current dir

import sys, os, stat, re

sys.argv.remove('CVS')
for dir in sys.argv:
    mode = os.stat(dir)[stat.ST_MODE]
    if (stat.S_ISDIR(mode)): 
        files = os.listdir(dir)
        files.sort()
        buf = ''
        buf += 'msgid ""\n'
        buf += 'msgstr ""\n'
        buf += '"Content-Type: text/plain; charset=UTF-8\\n"\n'
        buf += '"Language-code: '+dir+'\\n"\n'
        buf += '"Language-name: '+dir+'\\n"\n'
        buf += '"Domain: icommons\\n"\n'
        for fname in files:
            if (fname[-5:] != '.html'):
                continue
            f = file(dir+'/'+fname)
            s = f.read()
            s = re.sub(r'"',r'\\"',s) # escapes " character
            s = re.sub(r'\r\n',r'\n',s) # removes line feeds
            s = re.sub(r'\s+$',r'',s) # removes space at the end of the line
            s = re.sub(r'^\s+',r'',s) # removes spaces at the beginning of the line
            s = re.sub(r'\n',r'\\n',s) # escapes CR
            s = re.sub(r'@(\S+?)@',r'%(\1)s',s) # converts @ fields @
            msgid = fname[:-5]
            buf += 'msgid "'+msgid+'"\n'
            buf += 'msgstr "'+s+'"\n'
            buf += '\n'
        pofile = file('icommons-'+dir+'.po','w+')
        pofile.write(buf)
