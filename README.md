# POC Bot (Alert Bot)

This is the core base of bot and has the below features:

- config and logger is loaded only once (botloader)
- Log level can be set directly via config.json
- Message handler and @mentioned users is parsed
- Docker file ready for deployments
- Help Menu/table is already defined


This bot was build using the Symphony Python SDK. (QAed: 1.3.3)

https://developers.symphony.com/symphony-developer/docs/get-started-with-python.


<b>WORKFLOW</b>

Add the bot to a room and receive alerts for filtered keywords in another room


- <b>Commands list</b>:
  
    @BotPoc /help
  
    @BotPox /getid -> retrieve the stream id of the current room


- <b>Bot Deployment</b>:

Create a Service Account on your pod:
https://developers.symphony.com/symphony-developer/docs/create-a-bot-user

Generate an RSA Key Pair:

    openssl genrsa -out mykey.pem 4096
    openssl rsa -in mykey.pem -pubout -out pubkey.pem

Copy (zip) or clone this PocBot's latest code from repo:
https://github.com/Alex-Nalin/BotPoc

Install the required libraries:

    pip install -r requirements.txt

Modify resources\config.json to point to your desired Pod and update the below info about your bot:

    "botPrivateKeyName": "private.pem",
    "botUsername": "BotPoc",
    "bot@Mention": "@BotPoc",
    "botEmailAddress": "BotPoc@symphony.com",

Rename the following files under data folder:

    alertroom_sample.py -> alertroom.py
    wordfilter_sample.py -> wordfilter.py

Update alertroom.py to include one stream id of a room to get alerted in, example below:

    AlertRoom = {'fDZp6QvMhuwuq4XhwBMbIn___ogL9mrMdA'}

Update wordfilter.py to add word(s) to be alerted for:

    WordFilter = {'Symphony', 'Adia', 'Bot', 'POC'}

Modify the config.json to add your Company name (as visible to others) under allowedPod:

    "allowedPod" : "Symphony Private Pod Name",

You can change log level via config.json, changing to INFO, WARN or DEBUG

    "LOG_LEVEL" : "INFO"



You can decide to log to STDERR (useful for docker) or to a log file by updating app/loader/logger.py

STDERR:

    logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w', level=my_level
    )
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)
    
    logger.addHandler(stderr_handler)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

Log File:

    now = datetime.now()
    dt = now.strftime("%d-%m-%Y-%H-%M-%S")
    
    log_dir = os.path.join(os.path.dirname(__file__), "../logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
            filename=os.path.join(log_dir, 'MirrorBot-' + dt +'.log'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filemode='w', level=my_level
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING))
    
You can enable bot audit by entering a streamid to receive notification:
(The audit has been enhanced with exception reporting)

    "bot_audit": ""
    
Starting with Python SDK 1.3, datafeed.id is used to managed session better in case of failure and
you can choose where to store the datafeed.id

    "datafeedIdFilePath": "appbase"

Start the bot using main_async.py and use "@PocBot /help" to display the commands