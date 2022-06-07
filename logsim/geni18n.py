# -*- coding: utf-8 -*-
"""
This will generate the .pot and .mo files for the application domain and
languages defined below.

The .po and .mo files are placed as per convention in

"appfolder/locale/lang/LC_MESSAGES"

The .pot file is placed in the locale folder.

This script or something similar should be added to your build process.

The actual translation work is normally done using a tool like poEdit or
similar, it allows you to generate a particular language catalog from the .pot
file or to use the .pot to merge new translations into an existing language
catalog.

"""

import subprocess
import sys
import os
import app_const as appC

# we remove English as source code strings are in English
supportedLang = []
for l in appC.supLang:
    if l != u"en":
        supportedLang.append(l)


appFolder = os.getcwd()

# setup some stuff to get at Python I18N tools/utilities

pyExe = sys.executable
pyFolder = os.path.split(pyExe)[0]
pyToolsFolder = os.path.join(pyFolder, 'Tools')
pyI18nFolder = os.path.join(pyToolsFolder, 'i18n')
pyGettext = os.path.join(pyI18nFolder, 'pygettext.py')
pyMsgfmt = os.path.join(pyI18nFolder, 'msgfmt.py')
outFolder = os.path.join(appFolder, 'locale')
encoding = "zh_CN[.UTF-8]"
potLocation = os.path.join(outFolder, 'logsim_chinese_translation.pot')

# build command for pygettext
gtOptions = '-a -d %s -o %s.pot -p %s %s'
tCmd = pyExe + ' ' + pyGettext + ' ' + (gtOptions % (appC.langDomain,
                                                     appC.langDomain,
                                                     outFolder,
                                                     appFolder))

print("Generating the .pot file")
print("cmd: %s" % tCmd)
rCode = subprocess.call(tCmd)
print("return code: %s\n\n" % rCode)

for tLang in supportedLang:
    # build command for msgfmt
    langDir = os.path.join(appFolder, ('locale\%s\LC_MESSAGES' % tLang))
    poFile = os.path.join(langDir, appC.langDomain + '.po')
    tCmd = pyExe + ' ' + pyMsgfmt + ' ' + poFile

    print("Generating the .mo file")
    print("cmd: %s" % tCmd)
    rCode = subprocess.call(tCmd)
    print ("return code: %s\n\n" % rCode)
    #rCode2 = subprocess.call('msgmerge -U ' + poFile + ' ' + potLocation)
    #print("return code for merge: %s\n\n" % rCode2)
