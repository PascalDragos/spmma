import time

from misc.message import MessageType

from modules.mic import Microphone


def i2s_loop():
    try:
        mic_delay = 1  # seconds
        mic = Microphone(duration=5)

        while True:
            db, freq = mic.get_noise()
            db = round(db, 2)
            freq = round(freq, 0)
            print(db, freq)
            
            time.sleep(mic_delay)
    except KeyboardInterrupt:
        print("I2S loop stops...")


# Pentru testare
if __name__ == "__main__":
    i2s_loop()
