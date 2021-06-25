import requests
import datetime
import json
import logging

from misc.message import MessageType


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
        f = open('web.cfg',)
        cfg = json.load(f)
        domain = cfg["address"] + ":" + cfg["port"]

        logging.basicConfig(filename="web.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
        logger=logging.getLogger()

        while True:
            (type, obj) = q.get()  # blocanta
            now =  get_time()  # prima functie, vreau timpul cat mai exact
            print("WEB: ")
            print((type, obj))
            
            if type is MessageType.I2C_MESSAGE:
                print("I2c message")
                (weather_parameters, gases, lux, proximity) = obj
                data = {
                    "date": now,
                    "temperature": weather_parameters['t'],
                    "humidity": weather_parameters['h'],
                    "pressure": weather_parameters['p'],
                    "tmp36": weather_parameters['rt']
                }
                print(data)
                requests.post(domain + "/weather", data=data)

                data = {
                    "date": now,
                    "ox": gases['ox'],
                    "red": gases['red'],
                    "nh3": gases['nh3']
                } 
                print(data)
                requests.post(domain + "/gas", data=data)

                data = {
                    "date": now,
                    "light": lux,
                    "proximity": proximity
                }
                print(data)
                requests.post(domain + "/light", data=data)
            
            elif type is MessageType.I2S_MESSAGE:
                print("I2S message")
                (db, freq) = obj
                data = {
                    "date": now,
                    "db": db,
                    "freq": freq,
                }
                print(data)
                requests.post(domain + "/sound", data=data)

            else:
                logger.error("Tipul mesajului MessageType necunoscut")

    except InterruptedError:
        logger.error("Error in communication loop")

    except KeyboardInterrupt:
        logger.error("Server communication loop stops...")


# Pentru testare
if __name__ == "__main__":
    import multiprocessing
    q = multiprocessing.Queue()
    web_loop(q)
