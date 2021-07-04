import atexit  # pun functii care sa fie apelate cand se termina programul (trebuie sa handle the signals)
import ads1015
import RPi.GPIO as GPIO

''' Canalele sunt :
"in0/ref", "in1/ref", "in2/ref", "ref/gnd
Valori pentru gain:
6.144, 4.096, 2.048 (default), 1.024, 0.512 or 0.256
Valori pentru sample rate:
128, 250, 490, 920, 1600 (default), 2400 or 3300''' 


def cleanup():
    GPIO.output(MICS6814_HEATER_PIN, 0)


class ADC:
    MICS6814_GAIN = 6.144  # gain 2/3
    MICS6814_HEATER_PIN = 24
    ads1015.I2C_ADDRESS_DEFAULT = ads1015.I2C_ADDRESS_ALTERNATE  # pe GitHub e mentionat de Pimoroni si adresa asta

    def __init__(self):
        self.setup()

    def setup(self):
        self.adc = ads1015.ADS1015(i2c_addr=0x49)
        self.adc.set_mode('single')  # unipolar 
        self.adc.set_programmable_gain(self.MICS6814_GAIN) 
        self.adc.set_sample_rate(1600)  

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.MICS6814_HEATER_PIN, GPIO.OUT)
        GPIO.output(self.MICS6814_HEATER_PIN, 1)
        atexit.register(cleanup)

    def read_ADS(self, ch):
        if ch < 3:
            channel_name = 'in' + chr(48 + ch) + '/gnd'
        elif ch == 3:
            channel_name = 'ref/gnd'

        self.adc.set_programmable_gain(4.096)  # gain = 1
        v = self.adc.get_voltage(channel_name)
        Ri = 6000000

        if v <= 0.512:
            self.adc.set_programmable_gain(0.512)  # gain = 8
            v = self.adc.get_voltage(channel_name)
            Ri = 100000
        elif v <= 1.024:
            self.adc.set_programmable_gain(1.024)  # gain = 4
            v = self.adc.get_voltage(channel_name)
            Ri = 3000000
        elif v <= 2.048:
            self.adc.set_programmable_gain(2.048)  # gain = 2
            v = self.adc.get_voltage(channel_name)
            # print(f"2048: {v}")
            Ri = 6000000
        return v, Ri

    def read_MOS(self, ch):
        v, Ri = self.read_ADS(ch)
        return 1.0 / ((1.0 / ((v * 56000.0) / (3.3 - v))) - (1.0 / Ri))

    def read_OX(self):
        return self.read_MOS(0)

    def read_RED(self):
        return self.read_MOS(1)

    def read_NH3(self):
        return self.read_MOS(2)

    def read_temp(self):
        v, Ri = self.read_ADS(3)
        return 100.0 * (v - 0.5)
