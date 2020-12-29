import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from biosppy.signals import ecg
import librosa
import warnings


# ECG R-peak segmentation
def segment(array, p, f):
    count = 1
    # signals = []
    peaks = ecg.christov_segmenter(signal=array, sampling_rate=500)[0]
    for i in (peaks[1:-1]):
        diff1 = abs(peaks[count - 1] - i)
        diff2 = abs(peaks[count + 1] - i)
        x = peaks[count - 1] + diff1 // 2
        y = peaks[count + 1] - diff2 // 2
        seg = array[x:y]
        augment(seg, p, f, count)
        # sigToImage(sig, p, f, augmentType, count)
        # signals.append(sig)  # can delete this
        count += 1


# Convert segmented signals into grayscale images, nparray
def sigToImage(array, p, f, augmentType, peakCount):
    fig = plt.figure(frameon=False)  # plt.figure(figsize=(20, 4))
    plt.plot(array, color='gray')
    plt.xticks([]), plt.yticks([])
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    folder = 'processedData/augmentDummy/' + f'{p:02}' + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = folder + f'{p:02}' + '_' + f'{f:02}' + '_' + f'{augmentType:02}' + '_' + f'{peakCount:02}' + '.png'
    fig.savefig(filename)
    plt.cla()
    plt.clf()
    plt.close('all')


# Plot all corresponding segments on one graph
def plotAll(array, p, f, i):
    fig = plt.figure(frameon=False)  # plt.figure(figsize=(20, 4))
    plt.plot(array[0], color='gray')
    plt.plot(array[1], color='blue')
    plt.plot(array[2], color='black')
    plt.plot(array[3], color='green')
    plt.plot(array[4], color='red')
    plt.xticks([]), plt.yticks([])
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    folder = 'processedData/augmentDummy/' + f'{p:02}' + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = folder + f'{p:02}' + '_' + f'{f:02}' + '_' + f'{i:02}' + '.png'
    fig.savefig(filename)
    plt.cla()
    plt.clf()
    plt.close('all')


# Augment each signal and convert call fucntion to convert it to image
def augment(array, p, f, count):
    sigToImage(array, p, f, 1, count)

    # Noise addition using normal distribution with mean = 0 and std =1
    # Permissible noise factor value = x > 0.004
    noiseAdding = array + 0.009 * np.random.normal(0, 1, len(array))
    sigToImage(noiseAdding, p, f, 2, count)

    # Permissible factor values = samplingRate / 10
    timeShifting = np.roll(array, int(500 / 10))
    sigToImage(timeShifting, p, f, 3, count)

    # Disable warnings such as below from librosa
    # UserWarning: n_fft=2048 is too small for input signal of length=371
    # See https://github.com/librosa/librosa/issues/1194
    warnings.filterwarnings('ignore', category=UserWarning)

    # Permissible factor values = -5 <= x <= 5
    pitchShifting = librosa.effects.pitch_shift(array, 500, n_steps=-5.0)
    sigToImage(pitchShifting, p, f, 4, count)

    # Permissible factor values = 0 < x < 1.0
    factor = 0.99  # Yields the best reults without losing ecg wave shape
    timeStretching = librosa.effects.time_stretch(array, factor)
    sigToImage(timeStretching, p, f, 5, count)

    signals = [list(i) for i in zip(array, noiseAdding, timeShifting, pitchShifting,
                                    timeStretching)]

    signalsDF = pd.DataFrame(signals)
    signals2D = signalsDF.to_numpy()
    # plotAll(signals2D, p, f, count)

    # print('Exporting original + augmented signals to csv...')
    # signalsDF.to_csv(os.path.join('processedData/augmentDummy', 'signals.csv'), index=False)


print('Starting...')
person = 10
fileNum = 2
with open('dataset/Person_10/rec_2.csv', 'r') as file:
    # read csv data for each person from col=1 (filtered sig)
    features = pd.read_csv(file)
    filteredData = []

    for row in range(len(features)):
        filteredData.append(features.iat[row, 1])

    segment(np.asarray(filteredData), person, fileNum)
    print('Complete.')
