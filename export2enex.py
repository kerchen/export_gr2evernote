# A script for exporting all starred items from Google Reader to Evernote,
# using exported JSON data from Google's Takeout and Evernote's
# note emailing feature. 
#
# Copyright 2013 Paul Kerchen
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


def usage():
   print "\nOptions:"
   print "-n, --notebook: The name of the Evernote notebook to put sent notes in."
   print "          If you do not specify a notebook, sent notes will be put in the default notebook."
   print "-m, --maximum: The maximum number of articles that should be converted."
   print "          If you do not specify a maximum, all messages will be converted."
   print "-h, --help: Print this message and exit."

try:
   opts, args = getopt.getopt( sys.argv[1:], "n:m:h", ["notebook=","maximum=","help"])
except getopt.GetoptError as err:
   print str(err) 
   usage()
   sys.exit(2)

sender_user = ""
evernote_user = ""
notebook = ""
message_limit = -1 
skip_count = 0
continue_from_prev = False

for o, a in opts:
   if o in ("-n", "--notebook"):
      notebook = a
   elif o in ("-m", "--maximum"):
      message_limit = int(a)
   elif o in ("-h", "--help"):
      usage()
      sys.exit()

json_file = open("starred.json")
json_dict = json.loads( unicode(json_file.read(), encoding="utf-8") )

item_list = json_dict[ "items" ]

if message_limit < 0:
   message_limit = len(item_list)

print('<?xml version="1.0" encoding="UTF-8"?>')
print('<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export2.dtd">')
print('<en-export export-date="20130320T150950Z" application="Evernote" version="Evernote Mac 5.0.6 (400960)">')

for s in item_list:
   subject = ""
   if 'title' in s.keys():
      subject = unicode(s["title"]).encode('ascii', 'replace')
   if notebook:
      subject = subject + " @" + notebook

   msg_body = ""
   msg_body = msg_body + '<note><title>'+subject+'</title><content><![CDATA[<?xml version="1.0" encoding="UTF-8" standalone="no"?> <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"> <en-note>'
   msg_url = ""

   if 'canonical' in s.keys():
      d = s["canonical"][0]
      msg_url = unicode(d["href"]).encode('ascii', 'replace')
   if 'alternate' in s.keys():
      d = s["alternate"][0]
      msg_url = unicode(d["href"]).encode('ascii', 'replace')
   if 'summary' in s.keys():
      d = s["summary"]
      msg_body = msg_body + unicode(d["content"]).encode('ascii', 'replace')
   if 'content' in s.keys():
      d = s["content"]
      msg_body = msg_body + unicode(d["content"]).encode('ascii', 'replace')
   msg_body = msg_body + "</en-note>]]>\r\n</content>\r\n"
   msg_body = msg_body + "<note-attributes><source>web.clip</source><source-url>" + msg_url + "</source-url></note-attributes>"
   msg_body = msg_body + "</note>\r\n"

   print(msg_body)

   message_limit = message_limit - 1
   if message_limit < 1:
      break

print('</en-export>')

