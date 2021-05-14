import re
import difflib
from event import Event

try:
  import imgurpython
except (ImportError, SystemError):
  print("Warning: QDB module requires imgurpython.")
  imgurpython = object

try:
  import requests
except (ImportError, SystemError):
  print("Warning: QDB module requires requests.")
  requests = object


class QDB:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.bot = bot
        self.say = say
        try:
          from imgur_credentials import ImgurCredentials as ic
        except (ImportError, SystemError):
            print("Warning: imgur module requires credentials in modules/imgur_credentials.py")
            class PhonyIc:
                imgur_client_id = "None"
                imgur_client_secret = "None"
            ic = PhonyIc()
        self.imgur_client_id = ic.imgur_client_id
        self.imgur_client_secret = ic.imgur_client_secret

        # prevent unecessarily clearing our mem_store['qdb'] dict
        if not "qdb" in self.bot.mem_store:
          self.bot.mem_store['qdb'] = {}
        #define a key for _recent since that will not be a potential channel name
        self.bot.mem_store['qdb']['_recent'] = []

        # subscribing to all lines ALSO catches lines matching ".qdb something something"
        # so we don't need a second ".qdb" event
        all_lines = Event('1__all_lines__')
        all_lines.define('.*')
        all_lines.subscribe(self)

        self.bot.register_event(all_lines, self)

        self.help = ".qdb <search string of first line> | <search string of last line>"
        self.MAX_BUFFER_SIZE = 500
        self.MAX_HISTORY_SIZE = 10

    def _imgurify(self, url):
        client = imgurpython.ImgurClient(self.imgur_client_id, self.imgur_client_secret)

        replacement_values = list()

        if type(url) is list:
            for u in url:
                resp = client.upload_from_url(u)
                replacement_values.append(resp)
        else:
            try:
                resp = client.upload_from_url(url)
                replacement_values.append(resp)
            except imgurpython.helpers.error.ImgurClientError as e:
                self.bot.debug_print("ImgurClientError: ")
                self.bot.debug_print(str(e))
            except UnboundLocalError as e:
                self.bot.debug_print("UnboundLocalError: ")
                self.bot.debug_print(str(e))
            except requests.exceptions.ConnectionError as e:
                self.bot.debug_print("ConnectionError: ")
                self.bot.debug_print(str(e))
        return replacement_values

    def _detect_url(self, quote):
        """
        for tsd printouts and imgflip (.meme)
        follows this format:
        http://irc.teamschoolyd.org/printouts/8xnK5DmfMz
        http://i.imgflip.com/zs1e6.jpg
        """
        tsd_regex = "(?P<url>http://irc\.teamschoolyd\.org/printouts/\w+)"
        if_regex = "(?P<url>http://i\.imgflip\.com/\w+.jpg)"

        # to allow us to check both variables at the end
        tsd_url, if_url = None, None

        try:
            tsd_url = re.search(tsd_regex, quote).group("url")
        except AttributeError:
            pass
        try:
            if_url = re.search(if_regex, quote).group("url")
        except AttributeError:
            pass

        if not tsd_url and not if_url:
            return quote

        if tsd_url:
          url = tsd_url
        if if_url:
          url = if_url

        repl = self._imgurify(url)

        if tsd_url:
          new_quote = re.sub(tsd_regex, repl[0]['link'], quote)
        if if_url:
          new_quote = re.sub(if_regex, repl[0]['link'], quote)
        return new_quote

    def strip_formatting(self, msg):
        """Uses regex to replace any special formatting in IRC (bold, colors) with nothing"""
        return re.sub('([\x02\x1D\x1F\x16\x0F]|\x03([0-9]{2})?)', '', msg)

    def add_buffer(self, event=None, debug=False):
        """Takes a channel name and line passed to it and stores them in the bot's mem_store dict
        for future access. The dict will have channel as key. The value to that key will be a list
        of formatted lines of activity.
        If the buffer size is not yet exceeded, lines are just added. If the buffer
        is maxed out, the oldest line is removed and newest one inserted at the beginning.
        """
        if debug:
            print("Line: " + event.line)
            print("Verb: " + event.verb)
            print("Channel: " + event.channel)
            print("")
        if not event:
            return
        #there are certain things we want to record in history, like nick changes and quits
        #these often add to the humor of a quote. however, these are not specific to a channel
        #in IRC and our bot does not maintain a userlist per channel. Therefore, when nick
        #changes and quits occur, we will add them to every buffer. This is not technically
        #correct behavior and could very well lead to quits/nick changes that are not visible
        #showing up in a quote, but it's the best we can do at the moment
        if not event.channel:
            #discard events with unwanted verbs
            if event.verb not in ["QUIT", "NICK"]:
                return
            try:
                for chan in list(self.bot.mem_store['qdb'].keys()):
                    if chan != '_recent':
                        if len(self.bot.mem_store['qdb'][chan]) >= self.MAX_BUFFER_SIZE:
                            self.bot.mem_store['qdb'][chan].pop()
                        line = self.format_line(event)
                        if line:
                            self.bot.mem_store['qdb'][chan].insert(0, line)
            except (KeyError, IndexError):
                print("QDB add_buffer() error when no event channel")
        #now we continue with normal, per channel line addition
        #create a dictionary associating the channel with an empty list if it doesn't exist yet
        else:
            if event.channel not in self.bot.mem_store['qdb']:
                self.bot.mem_store['qdb'][event.channel] = []
            try:
            #check for the length of the buffer. if it's too long, pop the last item
                if len(self.bot.mem_store['qdb'][event.channel]) >= self.MAX_BUFFER_SIZE:
                    self.bot.mem_store['qdb'][event.channel].pop()
                #get a line by passing event to format_line
                #insert the line into the first position in the list
                line = self.format_line(event)
                if line:
                    self.bot.mem_store['qdb'][event.channel].insert(0, line)
            except IndexError:
                print("QDB add_buffer() error. Couldn't access the list index.")

    def format_line(self, event):
        """Takes an event and formats a string appropriate for quotation from it"""

        # first strip out printout urls and replace them with imgur mirrors
        # commenting out for now to avoid uploading to imgur so often
        #event.msg = self._detect_url(event.msg)

        #format all strings based on the verb
        if event.verb == "":
            return ''
        elif event.verb == "PRIVMSG":
            #special formatting for ACTION strings
            if event.msg.startswith('\001ACTION'):
                #strip out the word ACTION from the msg
                return ' * %s %s\n' % (event.user, event.msg[7:])
            else:
                return '<%s> %s\n' % (event.user, self.strip_formatting(event.msg))
        elif event.verb == "JOIN":
            return ' --> %s has joined channel %s\n' % (event.user, event.channel)
        elif event.verb == "PART":
            return ' <-- %s has left channel %s\n' % (event.user, event.channel)
        elif event.verb == "NICK":
            return ' -- %s has changed their nick to %s\n' % (event.user, event.msg)
        elif event.verb == "TOPIC":
            return ' -- %s has changed the topic for %s to "%s"\n' % (event.user, event.channel, event.msg)
        elif event.verb == "QUIT":
            return ' <-- %s has quit (%s)\n' % (event.user, event.msg)
        elif event.verb == "KICK":
            #this little bit of code finds the kick target by getting the last
            #thing before the event message begins
            target = event.line.split(":", 2)[1].split()[-1]
            return ' <--- %s has kicked %s from %s (%s)\n' % (event.user, target, event.channel, event.msg)
        elif event.verb == "NOTICE":
            return ' --NOTICE from %s: %s\n' % (event.user, event.msg)
        else:
            #no matching verbs found. just ignore the line
            return ''

    def get_qdb_submission(self, channel=None, start_msg='', end_msg='', strict=False):
        """Given two strings, start_msg and end_msg, this function will assemble a submission for the QDB.
        start_msg is a substring to search for and identify a starting line. end_msg similarly is used
        to search for the last desired line in the submission. This function returns a string ready
        for submission to the QDB if it finds the desired selection. If not, it returns None.
        """
        if not channel:
            return None
        #must have at least one msg to search for and channel to look it up in
        if len(start_msg) == 0 or not channel:
            return None
        #first, check to see if we are doing a single string submission.
        if end_msg == '':
            for line in self.bot.mem_store['qdb'][channel]:
                if start_msg.lower() in line.lower():
                    return self._detect_url(line) #removing temporary printout urls and replacing with imgur
            #making sure we get out of the function if no matching strings were found
            #don't want to search for a nonexistent second string later
            return None
        #search for a matching start and end string and get the buffer index for the start and end message
        start_index = -1
        end_index = -1
        """Finds matching string for beginning line. Buffer is traversed in reverse-chronological order
        .qdb -> strict = False -> earliest occurence
        .qdbs -> strict = True -> latest occurence
        """
        for index, line in enumerate(self.bot.mem_store['qdb'][channel]):
            #print "evaluating line for beginning: {}".format(line)
            if start_msg.encode('utf-8','ignore').lower() in line.encode('utf-8','ignore').lower():
                #print "found match, start_index={}".format(index)
                start_index = index
                if strict:
                    break
        #finds newest matching string for ending line
        for index, line in enumerate(self.bot.mem_store['qdb'][channel]):
            #print "evaluating line for end: {}".format(line)
            if end_msg.lower() in line.lower():
                #print "found match, end_index={}".format(index)
                end_index = index
                break
        #check to see if index values are positive. if not, string was not found and we're done
        if start_index == -1 or end_index == -1 or start_index < end_index:
            return None
        #now we generate the string to be returned for submission
        submission = ''
        try:
            for i in reversed(list(range(end_index, start_index + 1))):
                #print 'Index number is ' + str(i) + ' and current submission is ' + submission
                submission += self._detect_url(self.bot.mem_store['qdb'][channel][i]) #detect temporary printout urls and replace with imgur
        except IndexError:
            print("QDB get_qdb_submission() error when accessing list index")


        return submission

    def submit(self, qdb_submission, debug=False):
        """Given a string, qdb_submission, this function will upload the string to hlmtre's qdb
        server. Returns a string with status of submission. If it worked, includes a link to new quote.
        """
        if debug:
            print("Submission is:")
            print(qdb_submission)
            print("Current buffer is:")
            print(self.bot.mem_store['qdb'])
            print("")
            return ''
        #accessing hlmtre's qdb api
        url = 'https://qdb.zero9f9.com/api.php'
        payload = {'q':'new', 'quote': qdb_submission.rstrip('\n')}
        try:
          qdb = requests.post(url, payload)
        except requests.exceptions.ConnectionError as e:
          self.bot.debug_print("ConnectionError: ")
          self.bot.debug_print(str(e))
        #check for any HTTP errors and return False if there were any
        try:
            qdb.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.bot.debug_print('HTTPError: ')
            self.bot.debug_print(str(e))
            self.bot.debug_print("Perhaps informative:")
            self.bot.debug_print(url)
            self.bot.debug_print(str(payload))
            return "HTTPError encountered when submitting to QDB"
        try:
            q_url = qdb.json()
            self.add_recently_submitted(q_url['id'], qdb_submission)
            return "QDB submission successful! https://qdb.zero9f9.com/quote.php?id=" + str(q_url['id'])
        except (KeyError, UnicodeDecodeError):
            return "Error getting status of quote submission."
        return "That was probably successful since no errors came up, but no status available."

    def delete(self, user, post_id='', passcode=''):
        """A special function that allows certain users to delete posts"""
        #accessing hlmtre's qdb api
        url = 'http://qdb.zero9f9.com/api.php'
        payload = {'q':'delete', 'user':user, 'id':post_id, 'code':passcode}
        deletion = requests.get(url, params=payload)
        #check for any HTTP errors and return False if there were any
        try:
            deletion.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.bot.debug_print('HTTPError: ')
            self.bot.debug_print(str(e))
            return "HTTPError encountered when accessing QDB"
        try:
            del_status = deletion.json()
            if del_status['success'] == "true":
              for quote in self.bot.mem_store['qdb']['_recent']: # they're a list of dicts
                if int(post_id) in quote:
                  self.bot.mem_store['qdb']['_recent'].remove(quote)
              return "QDB deletion succeeded."
            return "QDB deletion failed."
        except (KeyError, UnicodeDecodeError):
            return "Error getting status of quote deletion."

    def recently_submitted(self, submission):
        """Checks to see if the given submission is string is at least 75% similar to the strings
        in the list of recently submitted quotes.
        Returns the id of the quote if it was recently submitted. If not, returns -1.
        """
        #set up a difflib SequenceMatcher with the first string to test
        comparer = difflib.SequenceMatcher()
        comparer.set_seq1(submission)
        #if we find that it has 75% similarity or greater to a recent submission, return True
        try:
            for recent_quote in self.bot.mem_store['qdb']['_recent']:
                comparer.set_seq2(list(recent_quote.values())[0])
                if comparer.ratio() >= .75:
                    return list(recent_quote.keys())[0]
        except TypeError:
            return -1
        except KeyError:
            return -1
        except IndexError:
            return -1
        return -1

    def add_recently_submitted(self, q_id, submission):
        """Takes a string, submission, and adds it to the list of recent submissions.
        Also we do length checking, only keep record of the previous MAX_HISTORY_SIZE quotes.
        """
        #first, see if we have reached the maximum history size. if so, remove last item
        if len(self.bot.mem_store['qdb']['_recent']) >= self.MAX_HISTORY_SIZE:
            self.bot.mem_store['qdb']['_recent'].pop()
        #inserting a dict with the qdb id of the submission and the submission content
        self.bot.mem_store['qdb']['_recent'].insert(0, {q_id:submission})

    def handle(self, event):
        #first check to see if there is a special deletion going on
        if event.msg.startswith(".qdbdelete") and event.is_pm:
            deletion = event.msg.split(' ', 2)
            try:
                #requires the format ".qdbdelete <post_id> <password>"
                self.say(event.user, self.delete(event.user, deletion[1], deletion[2]))
            except IndexError:
                self.say(event.user, "Not enough parameters provided for deletion.")
            return
        """
        See if we're going to generate a qdb submission, or just add the line to the buffer.
        .qdb is the standard, generous implementation selected after hours of testing and ideal for a significant number of situations where lines are repeated. Use specific search strings. the start_index of the submission will be the EARLIEST occurrence of the substring in the buffer.
        .qdbs is the strict implementation. The start_index will be the LATEST occurrence of the substring.
        """

        if event.msg.startswith(".qdb ") or event.msg.startswith(".qdbs "):
            #split the msg with '.qdb[s] ' stripped off beginning and divide into 1 or 2 search strings
            #e.g. ".qdb string1|string2" -> [".qdb", "string1|string2"]
            cmd_parts = event.msg.split(None,1)
            if len(cmd_parts) < 2:
                #do something here to handle '.qdb[s]'
                return
            #determine if using strict mode
            strict_mode = cmd_parts[0] == ".qdbs"
            #split the search parameter(s)
            #e.g. "string1|string2" -> ["string1", "string2"]
            string_token = cmd_parts[1].split('|', 1)
            start_msg = string_token[0].rstrip()
            #see if we only have a one line submission
            if len(string_token) == 1:
                #s is the string to submit
                s = self.get_qdb_submission(event.channel, start_msg)
                recent = self.recently_submitted(s)
                if recent > 0:
                    q_url = "http://qdb.zero9f9.com/quote.php?id=" + str(recent)
                    self.printer("PRIVMSG " + event.channel + " :QDB Error: A quote of >75% similarity has already been posted here: " + q_url + "\n")
                    return
                if not s:
                    self.printer("PRIVMSG " + event.channel + ' :QDB Error: Could not find requested string.\n')
                    return
                #Print the link to the newly submitted quote
                self.printer("PRIVMSG " + event.channel + ' :' + self.submit(s) + '\n')
                return
            #We should only get here if there are two items in string_token
            end_msg = string_token[1].lstrip()
            s = self.get_qdb_submission(event.channel, start_msg, end_msg, strict_mode)
            recent = self.recently_submitted(s)
            if recent > 0:
                q_url = "http://qdb.zero9f9.com/quote.php?id=" + str(recent)
                self.printer("PRIVMSG " + event.channel + " :QDB Error: A quote of >75% similarity has already been posted here: " + q_url + "\n")
                return
            #if there's nothing found for the submission, then we alert the channel and gtfo
            if not s:
                self.printer("PRIVMSG " + event.channel + ' :QDB Error: Could not find requested quotes or parameters were not specific enough.\n')
                return
            #print the link to the new submission
            self.printer("PRIVMSG " + event.channel + ' :' + self.submit(s) + '\n')
            return
        self.add_buffer(event)
