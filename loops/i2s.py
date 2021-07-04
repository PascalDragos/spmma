import time
import logging
from logging.handlers import TimedRotatingFileHandler

from misc.message import MessageType
from modules.mic import Microphone

# Logger
l_format = logging.Formatter('%(levelname)s : %(asctime)s %(message)s')  # formatul unei inregistrari
logger = logging.getLogger("i2s")  # instanta de logger
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('logs/i2s.log', when="midnight", interval=1,
                                   encoding='utf8')  # in fiecare zi, alt fisier
handler.setFormatter(l_format) 
handler.prefix = "%Y-%m-%d"  # prefixul pentru un fisier
logger.addHandler(handler)


# producer 2
def i2s_loop(q):
    try:
        print("I2s loop starts...")
        logger.debug("I2s loop starts...")
        mic_delay = 0.5  # seconds
        mic = Microphone(duration=10)
        logger.debug("I2s objects created...")

        while True:
            db, freq = mic.get_noise()
            
            db = list(filter(lambda x: x > 20, 
                list(map(lambda x: round(x, 2), db))))
            freq = list(map(lambda x: round(x, 2), freq))
            
            obj = (sum(db)/len(db), sum(freq)/len(freq))
            logger.info(obj)
            print(obj)
            q.put((MessageType.I2S_MESSAGE, obj))

            # for i in range(len(db)):
            #     obj = (db[i], freq[i])
            #     logger.info(obj)
            #     print(obj)
            #     q.put((MessageType.I2S_MESSAGE, obj))
                
            #time.sleep(mic_delay)
    except KeyboardInterrupt:
        print("I2S loop stops...")
        logger.debug("I2s loop stops...\n")


# Pentru testare
if __name__ == "__main__":
    import multiprocessing
    q = multiprocessing.Queue()
    i2s_loop(q)
