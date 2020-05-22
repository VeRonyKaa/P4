import numpy as np
import scipy.io.wavfile as wave
import scipy.signal as sig


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

def paramEqFilterCoefficients(digCenterFreq, digBandwidth, gain, level=1):
    if gain == level:
        feedforwardParams = np.array([1, 0, 0])
        feedbackParams = np.array([0, 0])
    else:
        cutoffGain = np.sqrt((gain**2+level**2)/2) # could also be the geometric mean instead
        alpha = np.sqrt((cutoffGain**2-level**2)/(gain**2-cutoffGain**2))*np.tan(digBandwidth/2)
        b0 = (level+gain*alpha)/(1+alpha)
        b1 = -2*level*np.cos(digCenterFreq)/(1+alpha)
        b2 = (level-gain*alpha)/(1+alpha)
        a1 = 2*np.cos(digCenterFreq)/(1+alpha)
        a2 = -(1-alpha)/(1+alpha)
        feedforwardParams = np.array([b0, b1, b2])
        feedbackParams = np.array([a1, a2])
    return feedforwardParams, feedbackParams



samplingFreq, signal = wave.read('/Users/veronikanemcova/PycharmProjects/PitchShift/sentence_5.wav')
inputsignal = signal[:,0]/2**15 # normalise


# low shelving filter
centerFreq = 0
cutoffFreq = 8000 # Hz
gain = 4
nDtft = 2048
feedforwardParams, feedbackParams = paramEqFilterCoefficients(centerFreq*2*np.pi/samplingFreq, \
    np.pi-cutoffFreq*2*np.pi/samplingFreq, gain)
shelvSignal = sig.lfilter(feedforwardParams, np.r_[1,-feedbackParams], inputsignal)


#vibrato
maxDelay = 0.0001*samplingFreq # samples
digModFreq = 2*np.pi*8.5/samplingFreq # rad/sample
output = addVibrato(shelvSignal, maxDelay, digModFreq)

wave.write(filename='angry.wav', rate=samplingFreq, data=output)