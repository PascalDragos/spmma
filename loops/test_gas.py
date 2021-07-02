from modules.adc import ADC
import time


adc = ADC()

with open("gas.txt", "a") as gas_file:
    try:
        while True:
            ox = adc.read_OX()
            red = adc.read_RED()
            nh3 = adc.read_NH3()
            gases = {"ox": ox, "red": red, "nh3": nh3}
            gas_file.write(str(gases) +"\n")
            #print(gases)
            time.sleep(5*60)
    except:
        pass

print("done")
