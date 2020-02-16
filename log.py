# import os
import logging

# from pathlib import Path


# try:
#     data = Path(os.environ['XDG_DATA_HOME']).absolute() / 'blockchain'
# except KeyError:
#     data = Path(os.environ['HOME']).absolute() / '.local' / 'share' / 'blockchain'
# data.mkdir(parents=True, exist_ok=True)

# logging.basicConfig(filename=str(data / 'blockchain.log'),
#                     filemode='a',
#                     format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('blockchain')
