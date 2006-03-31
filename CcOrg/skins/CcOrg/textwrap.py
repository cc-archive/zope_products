## Script (Python) "textwrap"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=input_text, cols=70
##title=
##
from Products.PythonScripts.standard import html_quote

request = container.REQUEST
RESPONSE =  request.RESPONSE

result = []
lines = input_text.split('\n')

for line in lines:
   out_words = []
   in_words = line.split()

   for word in in_words:
      if (len(' '.join(out_words)) + len(word)) > 70:
         result.append(' '.join(out_words))
         out_words = [word]
      else:
         out_words.append(word)

   result.append(' '.join(out_words))

return '\n'.join(result)
