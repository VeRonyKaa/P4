import numpy as np
import scipy.io.wavfile as wave


def addVibrato(inputSignal, modDepth, digModFreq, offset=0):
    nData = np.size(inputSignal)
    outputSignal = np.zeros(nData)
    tmpSignal = np.zeros(nData)
    for n in np.arange(nData):
        # calculate delay
        delay = offset + (modDepth/2)*(1-np.cos(digModFreq*n))
        # calculate filter output
        if n < delay:
            outputSignal[n] = 0
        else:
            intDelay = np.int(np.floor(delay))
            tmpSignal[n] = inputSignal[n-intDelay]
            fractionalDelay = delay-intDelay
            apParameter = (1-fractionalDelay)/(1+fractionalDelay)
            outputSignal[n] = apParameter*tmpSignal[n]+tmpSignal[n-1]-apParameter*outputSignal[n-1]
    return outputSignal


samplingFreq, signal = wave.read('/Users/veronikanemcova/PycharmProjects/PitchShift/sentence_5.wav')
inputSignal = signal[:,0]/2**15 # normalise

#vibrato
maxDelay = 0.0015*samplingFreq # samples
digModFreq = 2*np.pi*8.5/samplingFreq # rad/sample
output = addVibrato(inputSignal, maxDelay, digModFreq)

wave.write(filename='afraid.wav', rate=samplingFreq, data=output)
