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

from misc.message import MessageType
from misc.message import ButtonType

from web import web_loop
from i2c import i2c_loop
from spi import spi_loop
from i2s import i2s_loop


def main():
    logging.basicConfig(filename="spmma.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
    logger=logging.getLogger()

    # cozi partajate intre procese python
    queue_sensors = multiprocessing.Queue()
    queue_display = multiprocessing.Queue()
    queue_web = multiprocessing.Queue()

    # procele care gestioneaza cele 4 interfete utilizate, asignarea cozilor
    process_i2c = multiprocessing.Process(target=i2c_loop, args=(queue_sensors,))
    process_i2s = multiprocessing.Process(target=i2s_loop, args=(queue_sensors,))
    process_spi = multiprocessing.Process(target=spi_loop, args=(queue_display,))
    process_web = multiprocessing.Process(target=web_loop, args=(queue_web,))

    # pornim procesele
    process_i2c.start()
    # process_i2s.start()
    process_spi.start()
    # process_web.start()

    current_variable = 0
    variables = ["t",  "p", "h", "l", "ox", "red", "nh3"]
    display_is_sleeping = False
    while True:
        # proceseaza un mesaj venit de la interfata i2c sau i2s 
        sensor_object = queue_sensors.get()  # functie blocanta
        print(sensor_object)

        (type, obj) = sensor_object
        if type is MessageType.I2C_MESSAGE:
            (weather_parameters, gases, lux, proximity) = obj
            
            param = variables[current_variable]
            if param in ["t",  "p", "h"]:
                queue_display.put((param, weather_parameters[param]))
            elif param in ["ox", "red", "nh3"]:
                queue_display.put((param, gases[param]))
            else:
                queue_display.put((param, lux))
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
            queue_web.put(sensor_object)

        else:
            logger.error("Tipul mesajului MessageType necunoscut")

            
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSPMMA app stops...")
