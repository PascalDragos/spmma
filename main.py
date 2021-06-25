#!/usr/bin/env python3
from bme import BME280
from adc import ADC
from ltr import LTR_Wrapper
from mic import Microphone
import time

bme280 = BME280()
bme280.set_operation_mode(operation_mode="weather")
adc = ADC()
ltr = LTR_Wrapper()
mic = Microphone(duration=1)

while True:
    # weather_parameters = bme280.read_and_get_parameters()
    # print(f"\nt: {weather_parameters['t']:.1f},\t{weather_parameters['p']:.3f},\t{weather_parameters['h']:.3f}")

    # temp = adc.read_temp()
    # ox = adc.read_OX()
    # red = adc.read_RED()
    # nh = adc.read_NH3()
    # print(f"t: {temp:.1f};   ")

    lux = ltr.get_lux_auto_range()
    proximity = ltr.get_proximity()
    print(f"lux: {lux:.1f};   proximity: {proximity:.1f}")

    # print ("recording...")
    # db = mic.get_amplitude_at_frequency_range()
    # db = mic.get_dbSPL()

    # print(db, end="\r")

    time.sleep(1)
    
