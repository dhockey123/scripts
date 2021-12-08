from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

fig, ax = plt.subplots()
sdr = RtlSdr()

## Create slider axes and link with slider values for center freq, gain and fft bin size

center_freq_ax = plt.axes([0.25, 0.18, 0.55, 0.03])
center_freq = Slider(center_freq_ax, "C. Freq.", 7, 1000, valinit=90, valstep=1)

gain_ax = plt.axes([0.25, 0.14, 0.55, 0.03])
gain = Slider(gain_ax, "Gain", 1, 40, valinit=30, valstep=0.5)

bin_ax = plt.axes([0.25, 0.22, 0.55, 0.03])
bin = Slider(bin_ax, "Bins", 64, 4096, valinit=2048, valstep=2)

## Link sliders with click/drag events

center_freq.on_changed(update_center_freq)
gain.on_changed(update_gain)
bin.on_changed(update_bin_size)

# Functions for updating SDR and bin size values
def update_center_freq(val):
    sdr.sample_rate = 2.4e6
    sdr.center_freq = center_freq.val*1e6
    sdr.set_gain(gain.val)
    
def update_gain(val): 
    sdr.sample_rate = 2.4e6
    sdr.center_freq = center_freq.val*1e6
    sdr.set_gain(gain.val)

def update_bin_size(val):
    global bin_size
    bin_size = val

## Initialize SDR 
sdr.sample_rate = 2.4e6
sdr.center_freq = center_freq.val
sdr.set_gain(gain.val)
bin_size = bin.val

# Animate
def animate(i):
    ax.clear()
    samples = sdr.read_samples(2.4e6*0.2)
    ax.psd(samples, NFFT=bin_size, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    ax.set_ylim(-60, -10)

ani = animation.FuncAnimation(fig, animate, interval=50)
plt.show()

