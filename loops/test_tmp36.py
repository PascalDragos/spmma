

import time

from modules.adc import ADC



# Pentru testare
if __name__ == "__main__":
    adc = ADC()
    while True:
        t = adc.read_temp()
        print(t)
        time.sleep(1)
