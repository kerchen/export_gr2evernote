# A script for exporting all starred items from Google Reader to HTML files,
# using exported JSON data from Google's Takeout 
#
# Copyright 2013 Paul Kerchen, Davide Della Casa
#
# This program is distributed under the terms of the GNU General Public License v3.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
import smtplib
import json
import io
import getopt, sys
import os.path
import string

def usage():
   print "Converts exported starred articles from a Google Reader export file."
   print "The file 'starred.json' must be in the directory that this script is"
   print "invoked from.  Each article will be exported to its own HTML file."
   print "\nOptions:"
   print "-h, --help: Print this message and exit."

try:
   opts, args = getopt.getopt( sys.argv[1:], "h", ["help"])
except getopt.GetoptError as err:
   print str(err) 
   usage()
   sys.exit(2)

for o, a in opts:
   if o in ("-h", "--help"):
      usage()
      sys.exit()

# Provides a decent filename. A variation of: http://stackoverflow.com/a/295146/1318347
def cleanFileName(value):
  valid_chars = "-_() %s%s" % (string.ascii_letters, string.digits)
  untrimmedFileName = ''.join(c for c in value if c in valid_chars)
  maximumFileNameLength = 200
  if len(untrimmedFileName) > maximumFileNameLength:
    trimmedFileName = (untrimmedFileName[:maximumFileNameLength] + '..')
  else:
    trimmedFileName = untrimmedFileName
  return trimmedFileName.strip()

json_file = open("starred.json")
json_dict = json.loads( unicode(json_file.read(), encoding="utf-8") )

item_list = json_dict[ "items" ]

articleCounter = 0
for s in item_list:
   articleCounter += 1
   title = str(articleCounter)
   if 'title' in s.keys():
      title = title + " " + s["title"]
   fileName = cleanFileName(title) + '.html'
   file = open(fileName, 'w+')

   html_body = ""

   if 'alternate' in s.keys():
      d = s["alternate"][0]
      alternateURL = d["href"]
      html_body = html_body + '<p>URL: <a href="'+alternateURL+'">'+alternateURL+'</a></p>'
   if 'canonical' in s.keys():
      d = s["canonical"][0]
      canonicalURL = d["href"]
      hintAboutSecondURL  = (' 2') if 'alternate' in s.keys() else ''
      html_body = html_body + '<p>URL'+hintAboutSecondURL+': <a href="'+canonicalURL+'">'+canonicalURL+'</a></p>'

   html_body = html_body + '<hr>'

   if 'summary' in s.keys():
      d = s["summary"]
      html_body = html_body + d["content"]
   if 'content' in s.keys():
      d = s["content"]
      html_body = html_body + d["content"]

   file.write(html_body.encode("UTF-8"))
   file.close()

   print('extracted: ' + fileName)

print('...done')

