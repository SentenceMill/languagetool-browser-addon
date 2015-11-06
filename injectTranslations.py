#!/usr/bin/python3
# Daniel Naber, 2015-11-04
# Created a JSON file based on the existing English file,
# but using the translations from another language (needed
# as Transifex removes the 'placeholders' keys). Also,
# inject translation for language names.

import json
import re
import sys

def loadLanguageDict(filename):
    codeToLang = {}
    file = open(filename)
    for line in file:
        regex = re.compile("([a-z][a-z]|[a-z][a-z]-[A-Z][A-Z]|[a-z][a-z][a-z])\\s*=\\s*(.*)")  # e.g. "de", "de-DE", "ast"
        match = regex.match(line)
        if match:
            codeToLang[match.group(1)] = match.group(2)
    return codeToLang

if len(sys.argv) != 4:
    sys.stderr.write("Usage: " + sys.argv[0] + " <translationLangCode> <englishFile> <translatedFile>\n")
    sys.exit()

translationLangCode = sys.argv[1]
coreDictFile = "../languagetool/languagetool-language-modules/" + translationLangCode + "/src/main/resources/org/languagetool/MessagesBundle_" + translationLangCode + ".properties"
codeToLang = loadLanguageDict(coreDictFile)
englishFile = open(sys.argv[2]).read()
translatedFile = open(sys.argv[3])
translatedJson = json.loads(translatedFile.read())
newFile = englishFile

for k in translatedJson:
    translation = translatedJson[k]['message'].replace("\n", "\\\\n")
    backup = newFile
    newFile = re.sub('("' + k + '": {\\s*"message":\\s*".*?")', '"' + k + '": {\n    "message": "' + translation + '"', newFile, flags=re.MULTILINE|re.DOTALL)
    if backup == newFile:
        sys.stderr.write("WARN: Could not replace " + k + "\n")

newJson = json.loads(newFile)
for key in codeToLang:
    newKey = key.replace("-", "_")
    if newKey in newJson:
        raise Exception("Cannot add key '" + newKey + "' to file, already exists")
    translatedLang = bytes(codeToLang[key], "utf-8").decode("unicode_escape")   # e.g. Franz\\u00f6sisch -> Französisch
    newJson[newKey] = {'message': translatedLang, 'description': 'automatically added by injectTranslation.py'}

print(json.dumps(newJson, indent=2, ensure_ascii=False))
