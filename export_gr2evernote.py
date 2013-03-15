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
import getpass

def usage():
   print "\nOptions:"
   print "-e, --evernote-user: The Evernote email username (NOT the Evernote username) to send messages to. [required]"
   print "          Username only; do not include the '@m.evernote.com'!"
   print "-g, --gmail-user: The gmail username to send messages from. [required]"
   print "          Username only; do not include the '@gmail.com'!"
   print "-m, --maximum: The maximum number of messages that should be sent."
   print "          If you do not specify a maximum, all messages will be sent."
   print "          Note that Evernote limits the number of notes that can be added via e-mail in a single day."
   print "          For free accounts, the limit is 50; for premium accounts, it is 250."
   print "-n, --notebook: The name of the Evernote notebook to put sent notes in."
   print "          If you do not specify a notebook, sent notes will be put in the default notebook."
   print "-s, --skip: The number of articles to skip before sending the first e-mail message."
   print "          Useful for picking up where you left off from the previous day if you"
   print "          ran into Evernote's e-mail submission daily limit."
   print "-h, --help: Print this message and exit."
   print
   print "When prompted for a password, enter the password for the sender gmail address."
   print "It is expected that the exported starred items are in a file named 'starred_json' in the current working directory."

try:
   opts, args = getopt.getopt( sys.argv[1:], "e:m:n:g:s:h", ["evernote-user=","maximum=","notebook=","gmail-user=","skip=","help"])
except getopt.GetoptError as err:
   print str(err) 
   usage()
   sys.exit(2)

sender_addr = ""
evernote_addr = ""
notebook = ""
message_limit = -1 
skip_count = 0

for o, a in opts:
   if o in ("-g", "--gmail-user"):
      sender_addr = a
   elif o in ("-e", "--evernote-user"):
      evernote_addr = a
   elif o in ("-e", "--maximum"):
      message_limit = int(a)
   elif o in ("-n", "--notebook"):
      notebook = a
   elif o in ("-s", "--skip"):
      skip_count = int(a)
   elif o in ("-h", "--help"):
      usage()
      sys.exit()

if not sender_addr or not evernote_addr:
   print "Missing required parameter."
   usage()
   sys.exit()

sender_addr = sender_addr + "@gmail.com"
evernote_addr = evernote_addr + "@m.evernote.com"

sender_pwd = getpass.getpass()
FROM = sender_addr
TO = [evernote_addr] #must be a list 

json_file = open("starred.json")
json_dict = json.loads( unicode(json_file.read(), encoding="utf-8") )

item_list = json_dict[ "items" ]

print "Number of articles found in json export: %d" % len(item_list)

if message_limit < 0:
   message_limit = len(item_list)

print "Number of notes to be sent to Evernote: %d" % message_limit
if message_limit > 250:
   print "Warning: sending more than 250 messages in one day will most likely fail."

if skip_count > 0:
   print "The first %d articles will be skipped" % skip_count

sent_count = 0
fail_count = 0

for s in item_list:
   if skip_count > 0:
      skip_count = skip_count - 1
      continue

   #print "Title: %s" % unicode(s["title"]).encode('ascii', 'replace')
   subject = unicode(s["title"]).encode('ascii', 'replace')
   if notebook:
      subject = subject + " @" + notebook

   msg_body = ""
   if 'canonical' in s.keys():
      d = s["canonical"][0]
      #print "URL: %s" % unicode(d["href"]).encode('ascii', 'replace')
      msg_body = msg_body + "URL: " + unicode(d["href"]).encode('ascii', 'replace') + "\r\n"
   if 'alternate' in s.keys():
      d = s["alternate"][0]
      #print "Alt URL: %s" % unicode(d["href"]).encode('ascii', 'replace')
      msg_body = msg_body + "Alt URL:" + unicode(d["href"]).encode('ascii', 'replace') + "\r\n"
   if 'summary' in s.keys():
      d = s["summary"]
      #print "Summary: %s" % unicode(d["content"]).encode('ascii', 'replace')
      msg_body = msg_body + "Summary: " + unicode(d["content"]).encode('ascii', 'replace') + "\r\n"
   if 'content' in s.keys():
      d = s["content"]
      #print "Content: %s" % unicode(d["content"]).encode('ascii', 'replace')
      msg_body = msg_body + unicode(d["content"]).encode('ascii', 'replace')
   msg_body = msg_body + "</en-note>\r\n"


   # Prepare actual message
   message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
   """ % (FROM, ", ".join(TO), subject, msg_body)
   try:
         server = smtplib.SMTP("smtp.gmail.com", 587) 
         server.ehlo()
         server.starttls()
         server.login(sender_addr, sender_pwd)
         server.sendmail(FROM, TO, message)
         server.close()
         sent_count = sent_count + 1
         print "Successfully sent message for '%s'" % subject
   except:
         print "Failed to send mail for '%s'" % subject
         fail_count = fail_count + 1

   message_limit = message_limit - 1
   if message_limit < 1:
      print ("Successfully sent {0} notes; {1} failed").format( sent_count, fail_count )
      sys.exit()

print ("Successfully sent {0} notes; {1} failed").format( sent_count, fail_count )

