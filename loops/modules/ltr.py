from ltr559 import LTR559
import time

class LTR_Wrapper():
    # valori din data sheet
    # gain, min_val, max_val
    LUXRANGE = [(96,    0.01,    600.0),
                (48,    0.02,    1300.0),
                (8,     0.125,   8000.0),
                (4,     0.25,   16000.0),
                (2,     0.5,    32000.0),
                (1,     1.0,    64000.0)]  
    def __init__(self):
        self.ltr559 = LTR559()
        self.ltr559.set_light_integration_time_ms(100)
    
    def get_proximity(self):
        return self.ltr559.get_proximity(passive=False)
    
    def get_lux(self):
        return self.ltr559.get_lux(passive=False)

    # biblioteca oferita de producator utilizeaza doar gain = 4
    # poate fi mai lent decat get_lux
    def get_lux_auto_range(self):
        lux_val = self.ltr559.get_lux()  # nu am niciodata overflow, dar pot avea valori imprecise
        gain = self.ltr559.get_gain()
        
        biggest_gain = 1 
        for range in self.LUXRANGE:
            if lux_val < range[2]: 
                biggest_gain = range[0]
                break
        
        if biggest_gain != gain:
            self.ltr559.set_light_options(active=True, gain=biggest_gain)
            time.sleep(0.5)  # nu are mecanism de ack 
            lux_val = self.ltr559.get_lux()
        
        # print('gain:'+str(self.ltr559.get_gain())+' lux='+str(lux_val))
        return lux_val

