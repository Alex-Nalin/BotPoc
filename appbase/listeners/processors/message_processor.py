from sym_api_client_python.clients.user_client import UserClient
from sym_api_client_python.clients.stream_client import StreamClient
from appbase.commands.command import Help, SendIMmsg
import defusedxml.ElementTree as ET
import appbase.botloader.config as conf
from appbase.data import wordfilter, alertroom
import traceback
import logging, html

## Use config file
audit_stream = conf._config['bot_audit']


"""This will process the message posted in Symphony UI"""
class MessageProcessor:

    def __init__(self, bot_client):
        self.bot_client = bot_client

    async def processor(self, msg):

        mention = ""
        mention_len = ""

        try:
            firstname = msg['user']['firstName']
        except:
            firstname = "N/A"
        try:
            lastname = msg['user']['lastName']
        except:
            lastname = "N/A"
        displayName = msg['user']['displayName']
        email = msg['user']['email']
        userID = msg['user']['userId']
        try:
            username = msg['user']['username']
        except:
            username = "N/A"
        streamID = msg['stream']['streamId']
        streamType = msg['stream']['streamType']


        userFromid = UserClient.get_user_from_id(self, userID)
        userCompany = (userFromid['company'])

        logging.debug("--> User ID: " + str(userID) + " & full name: " + str(firstname) + " " + str(lastname))
        try:
            logging.debug("--> User email: " + str(email) + " & username: " + str(username) + " display Name: " + str(displayName))
        except:
            logging.debug("--> User email: " + str(email) + " & displayName: " + str(displayName))

        logging.debug("--> Stream Type: " + str(streamType) + " with stream ID: " + str(streamID))
        logging.debug("--> User is from: \"" + userCompany + "\" pod")

        ## Normal message in the chat - no @mention of #hashtag nor $cashtag
        msg_xml = msg['message']
        msg_root = ET.fromstring(msg_xml)
        msg_text = msg_root[0].text
        logging.debug(msg_text)

        try:
            ## Get the command send and check its lenght
            message_raw = self.sym_message_parser.get_text(msg)
            list_len = int(len(message_raw))

            ## Adds the items to one variable
            var_raw = ""
            for l in range(list_len):
                word = message_raw[l]
                var_raw += str(message_raw[l]) + " "

                if str(word).lower() in str(wordfilter.WordFilter).lower():
                    self.alertmessage = dict(message="<messageML>\"" + str(word) + "\" triggered by <b>" + str(displayName) + "</b> in " + str(streamID) + " (" + str(streamType) + ")</messageML>")
                    self.bot_client.get_message_client().send_msg(alertroom.AlertRoom, self.alertmessage)
                else:
                    pass

            message_reader = str(var_raw).replace("[", "").replace("'", "").replace("]", "")
            logging.debug("message_reader: " + str(message_reader))

        except:
            return await Help.help(self, msg)

        ## Getting @mention details
        try:
            mention_raw = self.sym_message_parser.get_mentions(msg)
            mention = str(mention_raw).replace("['", "").replace("', '", ", ").replace("']", "")
            logging.debug("mentions, hashtags, cashtags: " + str(mention))
            mention_split = str(mention).split(",")
            mention_len = len(str(mention_split[0]))
            firstMention = mention_split[0]
            logging.debug("firstMention: " + str(firstMention))
        except:
            firstMention = mention
            logging.debug("No @mention",  exc_info=True)

        """
        This is to make sure the user is from the allowed pod(s)
        """
        if userCompany in conf._config['allowedPod']:
            logging.debug("Inside allowed Pod(s), True")
            podAllowed = True
        else:
            podAllowed = False
            logging.debug("Outside allowed Pod(s), False")


        try:
            ## If within allowed Pod
            if podAllowed:

                ## Making sure the bot @mention is used and matches to respond back
                if str(firstMention) == str(conf._config['bot@Mention']):
                    logging.debug("mention: " + str(mention))
                    commandName = str(message_reader)[int(mention_len)+1:]
                    logging.debug("commandName: " + str(commandName))

                    try:
                        if "/help" in str(commandName):
                            logging.info("Calling /help by " + str(displayName))
                            if audit_stream != "":
                                self.botaudit = dict(message="""<messageML>Function /help called by <b>""" + str(displayName) + """</b> in """ + str(streamID) + """ (""" + str(streamType) + """)</messageML>""")
                                self.bot_client.get_message_client().send_msg(audit_stream, self.botaudit)
                            return await Help.help(self, msg)
                    except Exception as ex:
                        logging.error("/help did not run for External User call")
                        logging.exception("Message Command Processor Exception: {}".format(ex))
                        await auditLogging(self, ex, displayName, streamID, streamType, msg, userID, firstname)

                    try:
                        if "/getid" in str(commandName):
                            logging.debug("Getting room streamid")

                            if audit_stream != "":
                                self.botaudit = dict(message="""<messageML>Function /getid called by <b>""" + str(displayName) + """</b> in """ + str(streamID) + """ (""" + str(streamType) + """)</messageML>""")
                                self.bot_client.get_message_client().send_msg(audit_stream, self.botaudit)
                            try:
                                roomStreamID = ((StreamClient.get_room_info(self, streamID))['roomSystemInfo']['id'])
                                self.getstreamid = dict(message="<messageML>Room stream ID is " + str(roomStreamID) +"</messageML>")
                                self.bot_client.get_message_client().send_msg(streamID, self.getstreamid)
                            except:
                                self.getstreamid = dict(message="<messageML>Sorry, /getid only works in Rooms</messageML>")
                                self.bot_client.get_message_client().send_msg(streamID, self.getstreamid)
                    except Exception as ex:
                        logging.error("/getid did not run")
                        logging.exception("Message Command Processor Exception: {}".format(ex))
                        await auditLogging(self, ex, displayName, streamID, streamType, msg, userID, firstname)

                else:
                    ## Gets stream IM of caller and bot
                    streamIM = (StreamClient.create_im(self, [str(userID)])['id'])
                    ## Sends message to the calling user via IM
                    self.imMesage = dict(message="""<messageML>Hi, """ + firstname + """, how are you today?</messageML>""")
                    self.bot_client.get_message_client().send_msg(streamIM, self.imMesage)
                    return logging.debug("bot @mentioned does not match expected, or not calling bot command")
            else:
                return logging.debug("User is not from the allowed Pod(s)")
        except:
            traceback.print_exc()
            return logging.debug("bot @mentioned was not used",  exc_info=True)


## allow to get inside Symphony any exception messages
async def auditLogging(self, ex, displayName, streamID, streamType, msg, userID, firstname):
    try:
        if audit_stream != "":
            exception_format = html.escape('Message Command Processor Exception: {}'.format(ex))
            self.bot_client.get_message_client().send_msg(audit_stream, dict(message='<messageML>' + exception_format + '<br/><br/>Mesage sent by ' + str(displayName) + 'in ' + str(streamID) + ' (' + str(streamType) + '): <code>' + str(self.sym_message_parser.get_text(msg)) + '</code>Error:<code>' + html.escape(traceback.format_exc()) + '</code></messageML>'))
            return await SendIMmsg.sendIMmsg(self, StreamClient, userID, firstname," your last command did not run, please reach out to the Bot Admin")
    except:
        logging.debug("auditLogging function did not run")