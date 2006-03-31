## Script (Python) "strip_tags"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=text, max_len=195
##title=
##
flag = [1]
def stripfunc(c):
    if not flag[0]:
        if c == '>':
            flag[0] = 1
            return 0
    elif c == '<':
        flag[0] = 0
    return flag[0]               

stripped = filter(stripfunc, text)
words = stripped.split()
result = ''

while (len(result) < max_len) and (len(words) > 0):
   result = " ".join([result, words[0]])
   words = words[1:]

return result
