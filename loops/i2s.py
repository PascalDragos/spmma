import time
import logging
from logging.handlers import TimedRotatingFileHandler

from misc.message import MessageType

from modules.mic import Microphone

l_format = logging.Formatter('%(levelname)s : %(asctime)s %(message)s')  # formatul unei inregistrari
logger = logging.getLogger("i2s")  # instanta de logger
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('logs/i2s.log', when="midnight", interval=1, encoding='utf8')  # in fiecare zi, alt fisier
handler.setFormatter(l_format) 
handler.prefix = "%Y-%m-%d"  # prefixul pentru un fisier
logger.addHandler(handler)


# producer 2
def i2s_loop(q):
    try:
        print("I2s loop starts...")
        logger.debug("I2s loop starts...")
        mic_delay = 1  # seconds
        mic = Microphone(duration=5)
        logger.debug("I2s objects created...")

        while True:
            db, freq = mic.get_noise()

            db = round(db, 2)
            freq = round(freq, 0)

            logger.info((db, freq))
            q.put((MessageType.I2S_MESSAGE, (db, freq)))
            
            time.sleep(mic_delay)
    except KeyboardInterrupt:
        print("I2S loop stops...")
        logger.debug("I2s loop stops...\n")


# Pentru testare
if __name__ == "__main__":
    import multiprocessing
    q = multiprocessing.Queue()
    i2s_loop(q)
