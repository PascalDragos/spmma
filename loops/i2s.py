import time

from misc.message import MessageType

from modules.mic import Microphone


# producer 2
def i2s_loop(q):
    try:
        mic_delay = 1  # seconds
        mic = Microphone(duration=1)

        while True:
            db, freq = mic.get_noise()
            db = round(db, 2)
            freq = round(freq, 0)
            q.put((MessageType.I2S_MESSAGE, db, freq))
            
            time.sleep(mic_delay)
    except KeyboardInterrupt:
        print("I2S loop stops...")


# Pentru testare
if __name__ == "__main__":
    import multiprocessing
    q = multiprocessing.Queue()
    i2s_loop(q)
