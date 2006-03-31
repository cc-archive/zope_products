import difflib

def getdiff(a, b):

    a = a.splitlines(True)
    b = b.splitlines(True)

    d = difflib.Differ()

    return ''.join(list(d.compare(a, b)))
