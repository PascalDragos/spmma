"""
Procesul master care coordoneaza celelalte procese

Prin interfata I2C se comunica cu
    LTR-559 (senzorul de lumina, proximitate)
    BME280 (senzorul de temperatura, umiditate, presiune)
    ADS1015 (ADC la care sunt conectate rezistentele senzorilor de gaze si TMP36)

Prin interfata I2S se comunica cu
    SPH0645 (microfonul)

Prin interfata SPI se comunica cu
    ecranul IPS aflat pe EnviroPlus

Prin interfata WiFi se comunica cu
    serverul care pune la dispozitie un API de tip REST
"""

import multiprocessing
import logging
from logging.handlers import TimedRotatingFileHandler

from misc.message import MessageType
from misc.message import ButtonType

from web import web_loop
from i2c import i2c_loop
from spi import spi_loop
from i2s import i2s_loop

# Logger
l_format = logging.Formatter('%(levelname)s : %(asctime)s %(message)s')  # formatul unei inregistrari
logger = logging.getLogger("spmma")  # instanta de logger
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('logs/spmma.log', when="midnight", interval=1,
                                   encoding='utf8')  # in fiecare zi, alt fisier
handler.setFormatter(l_format)
handler.prefix = "%Y-%m-%d"  # prefixul pentru un fisier
logger.addHandler(handler)


def main():
    # cozi partajate intre procese python
    queue_sensors = multiprocessing.Queue()
    queue_display = multiprocessing.Queue()
    queue_web = multiprocessing.Queue()

    # procele care gestioneaza cele 4 interfete utilizate, asignarea cozilor
    process_i2c = multiprocessing.Process(target=i2c_loop, args=(queue_sensors,))
    process_i2s = multiprocessing.Process(target=i2s_loop, args=(queue_sensors,))
    process_spi = multiprocessing.Process(target=spi_loop, args=(queue_display,))
    process_web = multiprocessing.Process(target=web_loop, args=(queue_web,))

    logger.debug("Queue and processes created")

    # pornim procesele
    process_i2c.start()
    process_i2s.start()
    process_spi.start()
    # process_web.start()

    logger.debug("Processes started")
    logger.debug("i2c_object = ((BME temp, humidity, pressure, TMP temp), (OX, RED, NH3), lux, proximity)")

    current_variable = 0
    variables = ["t", "h", "l", "s", "ox", "red", "nh3"]
    display_is_sleeping = False

    while True:
        # proceseaza un mesaj venit de la interfata i2c sau i2s
        sensor_object = queue_sensors.get()  # functie blocanta
        logger.info(sensor_object)

        (type, obj) = sensor_object
        param = variables[current_variable]
        if type is MessageType.I2C_MESSAGE:
            (weather_parameters, gases, lux, proximity) = obj

            if param == "t":
                queue_display.put((param, weather_parameters["rt"]))
            elif param == "h":
                queue_display.put((param, weather_parameters[param]))
            elif param == "l":
                queue_display.put((param, lux))
            elif param in ["ox", "red", "nh3"]:
                queue_display.put((param, gases[param]))
            else:
                pass
            
            # trimite informatiile la procesul care se ocupa de comunicatia cu serverul
            queue_web.put(sensor_object)

        elif type is MessageType.BTN_MESSAGE:
            if obj is ButtonType.SLEEP:
                display_is_sleeping = not display_is_sleeping
                queue_display.put(('sleep', display_is_sleeping))

            elif obj is ButtonType.NEXT:
                current_variable = current_variable + 1 if current_variable + 1 < len(variables) else 0
                param = variables[current_variable]

            else:
                logger.error("Tipul mesajului ButtonType necunoscut")

        elif type is MessageType.I2S_MESSAGE:
            if param == "s":
                queue_display.put((param, obj[0]))
            queue_web.put(sensor_object)

        else:
            logger.error("Tipul mesajului MessageType necunoscut")


if __name__ == "__main__":
    try:
        print("SPMMA starts...")
        main()
    except KeyboardInterrupt:
        print("SPMMA stops...")
        logger.debug("SPMMA app stops...\n")
