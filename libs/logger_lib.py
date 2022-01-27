# region Logging
import logging

logging.basicConfig(format='%(asctime)s'
                           ' - %(name)s'
                           ' - %(levelname)s'
                           ' - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
# endregion


# Log Errors caused by Updates.
def info(msg):
    logger.info(f'Update info: {msg}')
    # print(msg)


def error(update, err):
    logger.error(f'Update "{update}" caused error: "{err}"')
    # print(update, "\n", err)


def warning(update, msg):
    logger.warning(f'Update "{update}" caused warning: "{msg}"')
    # print(update, "\n", msg)
