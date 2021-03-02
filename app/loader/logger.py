import app.loader.config as conf
import logging.config
import sys


level_str = conf._config['LOG_LEVEL']
my_level = str(level_str)

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

### logs to file
# def configure_logging():
#         log_dir = os.path.join(os.path.dirname(__file__), "logs")
#         if not os.path.exists(log_dir):
#             os.makedirs(log_dir, exist_ok=True)
#         logging.basicConfig(
#                 filename=os.path.join(log_dir, 'MentionBot.log'),
#                 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                 filemode='w', level=logging.DEBUG
#         )
#         logging.getLogger("urllib3").setLevel(logging.WARNING)

# def configure_logging():
#
#         logging.basicConfig(
#                 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                 level=logging.DEBUG
#         )
#         logging.getLogger("urllib3").setLevel(logging.WARNING)