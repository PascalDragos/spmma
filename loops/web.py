import requests
import datetime
import json
import logging

import logging
from logging.handlers import TimedRotatingFileHandler

from misc.message import MessageType


l_format = logging.Formatter('%(levelname)s : %(asctime)s %(message)s')  # formatul unei inregistrari
logger = logging.getLogger("web")  # instanta de logger
logger.setLevel(logging.DEBUG) # afisez informatiile de la debug in sus
handler = TimedRotatingFileHandler('logs/web.log', when="midnight", interval=1, encoding='utf8')  # in fiecare zi, alt fisier
handler.setFormatter(l_format) 
handler.prefix = "%Y-%m-%d"  # prefixul pentru un fisier
logger.addHandler(handler)


def time_format(dt):
    return "%s:%.3f%s" % (
        dt.strftime('%Y-%m-%d %H:%M'),
        float("%06.3f" % (dt.second + dt.microsecond / 1e6)),
        dt.strftime('%z')
    )   


def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
    

def web_loop(q):
    try:
        print("Web loop starts...")
        logger.debug("WEB loop starts...")

        f = open('web.cfg',)
        cfg = json.load(f)

        domain = cfg["address"] + ":" + cfg["port"]
        logger.debug(f"WEB loop on domain: {domain}")

        web_session = requests.Session()
        web_session.headers.update({"pass" : cfg["password"]})

        while True:
            (type, obj) = q.get()  # blocanta
            now =  get_time()  # prima functie, vreau timpul cat mai exact
            logger.info(f"Received {(type, obj)}")
            
            if type is MessageType.I2C_MESSAGE:
                (weather_parameters, gases, lux, proximity) = obj
                data = {
                    "date": now,
                    "temperature": weather_parameters['t'],
                    "humidity": weather_parameters['h'],
                    "pressure": weather_parameters['p'],
                    "tmp36": weather_parameters['rt']
                }
                logger.info(domain + "/weather, POST, data: " + str(data))
                web_session.post(domain + "/weather", data=data)

                data = {
                    "date": now,
                    "ox": gases['ox'],
                    "red": gases['red'],
                    "nh3": gases['nh3']
                } 
                
                logger.info(domain + "/gas, POST, data: " + str(data))
                web_session.post(domain + "/gas", data=data)

                data = {
                    "date": now,
                    "light": lux,
                    "proximity": proximity
                }
                
                logger.info(domain + "/light, POST, data: " + str(data))
                web_session.post(domain + "/light", data=data)
            
            elif type is MessageType.I2S_MESSAGE:
         
                (db, freq) = obj
                data = {
                    "date": now,
                    "db": db,
                    "freq": freq,
                }
                logger.info(domain + "/sound, POST, data: " + str(data))
                web_session.post(domain + "/sound", data=data)

            else:
                logger.error("Tipul mesajului MessageType necunoscut")


    except InterruptedError:
        print("Error in communication loop")
        logger.error("Error in communication loop")

    except KeyboardInterrupt:
        print("Web loop stops...")
        logger.debug("Server communication loop stops...\n")

    except Exception as ex:
        print("Error in communication loop")
        logger.error(repr(ex))

# Pentru testare
if __name__ == "__main__":
    import multiprocessing
    q = multiprocessing.Queue()
    web_loop(q)
