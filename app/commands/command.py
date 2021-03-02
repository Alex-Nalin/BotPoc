from sym_api_client_python.clients.sym_bot_client import APIClient
from sym_api_client_python.clients.user_client import UserClient
import asyncio
import app.loader.config as conf

## Use config file
audit_stream = conf._config['bot_audit']

class Help:

    def __init__(self, bot_client):
        self.bot_client = bot_client

    async def help(self, msg):

        await asyncio.sleep(0)

        displayHelp = "<card accent='tempo-bg-color--blue' iconSrc=''> \
                            <header><h2>Bot Commands (v1)</h2></header> \
                            <body> \
                              <table style='max-width:100%'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\"> \
                                    <td><b>Command</b></td> \
                                    <td><b>Description</b></td> \
                                  </tr> \
                                </thead> \
                                <tbody> \
                                  <tr> \
                                    <td>" + conf._config['bot@Mention'] + " /help</td> \
                                    <td>Show this menu</td> \
                                  </tr> \
                                </tbody> \
                                </table> \
                            </body> \
                        </card>"

        self.help = dict(message="""<messageML>""" + displayHelp + """</messageML>""")
        return self.bot_client.get_message_client().send_msg(msg['stream']['streamId'], self.help)