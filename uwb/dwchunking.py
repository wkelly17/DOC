#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  Copyright (c) 2014 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Jesse Griffin <jesse@distantshores.org>


"""
"""

import os
import sys
import codecs

TMPL = u'''====== Book Reference {1} ======


===== TFT: =====

{0}


===== UTB: =====

{0}


===== Important Terms: =====

  * **[[:en:uwb:notes:key-terms:example|example]]**
  * **[[:en:uwb:notes:key-terms:example|example]]**
 

===== Translation Notes: =====


    * **bold words**  - explanation
    * **bold words**  - explanation
  
===== Links: =====

  * **[[en/bible-training/notes:43luk/questions/comprehension/01|Luke Chapter 1 Checking Questions]]**
 

**[[en/bible-training/notes:43luk/01/14|<<]] | [[en/bible-training/notes:43luk/01/18|>>]]**'''


def splice(s):
    for i in s.split('\n===== '):
        ref, txt = i.split('=====\n', 1)
        ref = ref.strip()
        filepath = getpath(ref.lower())
        if not filepath: continue
        writeFile(filepath, TMPL.format(txt.strip(), ref))

def getpath(r):
    try:
        book, ref = r.split(' ')
        #bk = books[book]
        c, vv = ref.split(':')
        v = vv.split('-')[0]
        return '{0}/{1}/{2}.txt'.format(book, c.zfill(3), v.zfill(3))
    except:
        return False

def writeFile(f, content):
    makeDir(f.rpartition('/')[0])
    out = codecs.open(f, encoding='utf-8', mode='w')
    out.write(content)
    out.close()

def makeDir(d):
    '''
    Simple wrapper to make a directory if it does not exist.
    '''
    if not os.path.exists(d):
        os.makedirs(d, 0755)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filetochunk = str(sys.argv[1]).strip()
        if not os.path.exists(filetochunk):
            print 'Directory not found: {0}'.format(filetochunk)
            sys.exit(1)
    else:
        print 'Please specify the file to chunk.'
        sys.exit(1)
    src = codecs.open(filetochunk, encoding='utf-8').read()
    splice(src)
