import threading
import time
import logging
from logging.handlers import TimedRotatingFileHandler

from misc.message import MessageType
from misc.message import ButtonType

from modules.bme import BME280
from modules.adc import ADC
from modules.ltr import LTR_Wrapper


# valori pentru senzorul de proximitate utilizat ca buton
PROXIMTY_SLEEP_TRESHOLD = 500
PROXIMTY_NEXT_TRESHOLD = 50


# Logger
l_format = logging.Formatter('%(levelname)s : %(asctime)s %(message)s')  # formatul unei inregistrari
logger = logging.getLogger("i2c")  # instanta de logger
logger.setLevel(logging.DEBUG)  # afisez informatiile de la debug in sus
handler = TimedRotatingFileHandler('logs/i2c.log', when="midnight", interval=1, encoding='utf8')  # in fiecare zi, alt fisier
handler.setFormatter(l_format) 
handler.prefix = "%Y-%m-%d"  # prefixul pentru un fisier
logger.addHandler(handler)


# exista 2 threaduri care acceseaza LTR
# sincronizare cu semafoare
lock = threading.Lock()


# Producer 1
def i2c_loop(q):
    try:
        print("I2c loop starts...")
        logger.debug("I2c loop starts...")

        bme280 = BME280()
        lock.acquire()
        bme280.set_operation_mode(operation_mode="weather")
        lock.release()
        adc = ADC()
        ltr = LTR_Wrapper()

        logger.debug("Objects created")

        button_delay = 0.5  # seconds
        button_debounce = 1.5 # seconds
        read_delay = 10  # seconds

        logger.debug("Processes start...")
        button_thread(q, ltr, button_delay, button_debounce)
        sensor_thread(q, bme280, adc, ltr, read_delay)

        while True:
            # for keeping alive
            time.sleep(60*60)

    except KeyboardInterrupt:
        print("I2C loop stops...")
        logger.debug("I2c loop stops...\n")


def button_thread(q, ltr, button_delay, button_debounce):
    lock.acquire()
    proximity = ltr.get_proximity()
    lock.release()

    if proximity > PROXIMTY_SLEEP_TRESHOLD:
        logger.info((MessageType.BTN_MESSAGE, ButtonType.SLEEP))   
        q.put((MessageType.BTN_MESSAGE, ButtonType.SLEEP))
        # dau mesaj sa afisez alta valoare pe ecran
        t = threading.Timer(button_debounce, button_thread, [q, ltr, button_delay, button_debounce])
        t.daemon = True
        t.start()

    elif proximity > PROXIMTY_NEXT_TRESHOLD:
        logger.info((MessageType.BTN_MESSAGE, ButtonType.NEXT))
        q.put((MessageType.BTN_MESSAGE, ButtonType.NEXT))
        t = threading.Timer(button_debounce, button_thread, [q, ltr, button_delay, button_debounce])
        t.daemon = True
        t.start()
    else:
        t = threading.Timer(button_delay, button_thread, [q, ltr, button_delay, button_debounce])
        t.daemon = True
        t.start()


def sensor_thread(q, bme280, adc, ltr, read_delay):
    lock.acquire()
    weather_parameters = bme280.read_and_get_parameters()
    weather_parameters['rt'] = adc.read_temp() - 1
    lock.release()

    lock.acquire()
    ox = adc.read_OX()
    red = adc.read_RED()
    nh3 = adc.read_NH3()
    lock.release()
    gases = {"ox": ox*1.2 , "red": red, "nh3": nh3}

    lock.acquire()
    lux = ltr.get_lux_auto_range()
    proximity = ltr.get_proximity()
    lock.release()

    weather_parameters['t'] = round(weather_parameters['t'], 2)
    weather_parameters['rt'] = round(weather_parameters['rt'], 2)
    if weather_parameters['rt'] < 22:
        weather_parameters['rt'] = 24.6
    weather_parameters['p'] = round(weather_parameters['p'], 2)
    weather_parameters['h'] = round(weather_parameters['h'] + 10, 2)

    for k, v in gases.items():
        gases[k] = round(v, 0)
    lux = round(lux, 1)

    i2c_object = (weather_parameters, gases, lux, proximity)

    logger.info((MessageType.I2C_MESSAGE, i2c_object))
    q.put((MessageType.I2C_MESSAGE, i2c_object))

    t = threading.Timer(read_delay, sensor_thread, [
                        q, bme280, adc, ltr, read_delay])
    t.daemon = True
    t.start()


# Pentru testare
if __name__ == "__main__":
    import multiprocessing
    q = multiprocessing.Queue()
    i2c_loop(q)
