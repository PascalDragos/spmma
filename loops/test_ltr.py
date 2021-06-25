from modules.ltr import LTR_Wrapper
import time

ltr = LTR_Wrapper()

while True:
    lux = ltr.get_lux_auto_range()
    proximity = ltr.get_proximity()
    print(f"lux {lux}, prox{proximity}")
    time.sleep(1)