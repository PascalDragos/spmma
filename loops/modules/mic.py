import sounddevice
import numpy
import sys
import math
import pickle


class Microphone():
    def __init__(self, 
                 sample_rate=22000,  #  Sample rate in Hz
                 duration=1):  # Duration, in seconds, of noise sample capture

        self.duration = duration
        self.sample_rate = sample_rate

        self.noise_floor = sys.float_info.max
        self.max_dbSPL = 0
        self.it = 0


    def record(self):
        pcm = sounddevice.rec(
            frames=int(self.duration * self.sample_rate), # dimensiunea array-ului de iesire
            samplerate=self.sample_rate,
            blocking=True, # cand am array-ul, am si datele deja scrise in el
            channels=1, #  avem doar un canal, un singur microfon
            dtype='int32' # le vreau ca int pe 32 de biti
        )
        return Signed32_to_Signed18(pcm) # datele sunt de fapt signed 18 << (8 + 6)


    def get_noise(self):
        big_pcm = self.record()[int((self.duration-2)*self.sample_rate):]
        pcms = numpy.split(big_pcm, 10)

        dbSPLs = []
        freqs = []

        for pcm in pcms:
            vmax = numpy.amax(pcm)
            vmin = numpy.amin(pcm)
            
            # DCoffset = numpy.average(pcm) # sunetul nu e centrat in 0
            DCoffset = (vmax + vmin) / 2
            vmax_noDC = vmax - DCoffset # il centrez
            vmin_noDC = vmin - DCoffset # il centrez
            
            vabs = abs(vmax_noDC) if (abs(vmax_noDC) > abs(vmin_noDC)) else abs(vmin_noDC)  # varful

            if vabs < self.noise_floor:
                self.noise_floor = vabs
            
            vfinal = vabs - self.noise_floor - 2

            dbSPL = PCM_to_dbSPL(vfinal)

            if dbSPL > self.max_dbSPL:
                self.max_dbSPL = dbSPL

            magnitude = numpy.abs(numpy.fft.rfft(pcm))
            freq = numpy.mean(magnitude)
            dbSPLs.append(dbSPL)
            freqs.append(freq)
        return dbSPLs, freqs


    def get_noise_debug(self, fo):        
        # with open('mic.pcm','w') as fpcm:
        #     for val in pcm:
        #         fpcm.write(str(val) + " ")
        #     fpcm.write("\n")

        # numpy.savetxt('data2.csv', pcm, delimiter=',', fmt = "%d")
        # print(pcm)
        pcm = self.record()[int((self.duration-1)*self.sample_rate):]


        vmax = numpy.amax(pcm)
        vmin = numpy.amin(pcm)
        
        # DCoffset = numpy.average(pcm) # sunetul nu e centrat in 0
        DCoffset = (vmax + vmin) / 2
        vmax_noDC = vmax - DCoffset # il centrez
        vmin_noDC = vmin - DCoffset # il centrez
        
        vabs = abs(vmax_noDC) if (abs(vmax_noDC) > abs(vmin_noDC)) else abs(vmin_noDC)  # varful
        # vabs = (vmax - vmin)/2

        if vabs < self.noise_floor:
            self.noise_floor = vabs
        
        vfinal = vabs - self.noise_floor

        dbSPL = PCM_to_dbSPL(vfinal)

        if dbSPL > self.max_dbSPL:
            self.max_dbSPL = dbSPL

        fo.write(',{:+10.0f}'.format(vmin))
        fo.write(',{:+10.0f}'.format(vmax))
        fo.write(',{:+10.0f}'.format(DCoffset))
        fo.write(',{:+10.0f}'.format(vmin_noDC))
        fo.write(',{:+10.0f}'.format(vmax_noDC))
        fo.write(',{:+10.0f}'.format(vabs))
        fo.write(',{:+10.0f}'.format(self.noise_floor))
        fo.write(',{:+10.0f}'.format(vfinal))
        fo.write(',{:4.0f}'.format(dbSPL))
        fo.write(',{:4.0f}'.format(self.max_dbSPL))
        fo.write('\n')

        magnitude = numpy.abs(numpy.fft.rfft(pcm))
        freq = numpy.mean(magnitude)

        print(dbSPL)
        return dbSPL, freq
  

def Signed32_to_Signed18(x):
    return x >> 14


def PCM_to_dbSPL(sample):
    FSdbSPL = 120  # full scale db SPL value
    res = 0.0
    if (sample > 0):
        dbFS = 20 * math.log10(sample/0x1ffff)  # 18 biti
        res = FSdbSPL + dbFS
    return res


# Pentru testare
if __name__ == "__main__":
    import time
    fo = open('SPL-Test.csv','w')
    fo.write('t,vmin,vmax,DCOFFSET,vmin_nodc,vmax_nodc,vabs,noisefloor,vfinal,dbSPL,maxSPL\n')
    # mic = Microphone(duration=10)
    # while True:
    #     mic.get_noise_debug(fo)
    #     time.sleep(0.5)
    
    mic = Microphone(duration=5)
    pcm = mic.record()[int(0*5500):]
    numpy.savetxt("abc.csv", pcm, delimiter =",")