from sym_api_client_python.clients.user_client import UserClient
from sym_api_client_python.clients.stream_client import StreamClient
from app.commands.command import Help
import defusedxml.ElementTree as ET
import app.loader.config as conf
import traceback
import logging

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
                var_raw += str(message_raw[l]) + " "

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
                    ## Help command when called via :@mention /help call
                        if "/help" in str(commandName):
                            logging.info("Calling /help by " + str(displayName))
                            if audit_stream != "":
                                self.botaudit = dict(message="""<messageML>Function /help called by <b>""" + str(displayName) + """</b> in """ + str(streamID) + """ (""" + str(streamType) + """)</messageML>""")
                                self.bot_client.get_message_client().send_msg(audit_stream, self.botaudit)
                            return await Help.help(self, msg)
                    except:
                        logging.error("/help is not working")
                        traceback.print_exc()
                        if audit_stream != "":
                            self.botaudit = dict(message="""<messageML>ERROR: Function /help called by <b>""" + str(displayName) + """</b> in """ + str(streamID) + """ (""" + str(streamType) + """)</messageML>""")
                            self.bot_client.get_message_client().send_msg(audit_stream, self.botaudit)
                        return logging.debug("Help is not working",  exc_info=True)

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