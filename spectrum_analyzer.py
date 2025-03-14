import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2048  # Larger chunk for better frequency resolution

class AudioAnalyzer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Set up the plot with two subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Time domain plot (waveform)
        self.line_time, = self.ax1.plot(np.zeros(CHUNK), 'b-')
        self.ax1.set_title('Microphone Waveform')
        self.ax1.set_xlabel('Sample')
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_ylim(-35000, 35000)
        self.ax1.set_xlim(0, CHUNK)
        self.ax1.grid(True)
        
        # Frequency domain plot (spectrum)
        # FFT produces CHUNK/2 unique frequency bins
        self.line_freq, = self.ax2.semilogx(np.zeros(CHUNK//2), 'r-')
        self.ax2.set_title('Frequency Spectrum')
        self.ax2.set_xlabel('Frequency (Hz)')
        self.ax2.set_ylabel('Magnitude (dB)')
        self.ax2.set_ylim(-120, 0)
        self.ax2.set_xlim(20, RATE//2)
        self.ax2.grid(True)
        
        # For frequency domain
        self.freq = np.fft.rfftfreq(CHUNK, 1/RATE)
        
        # Adjust layout
        plt.tight_layout()
        
        # Create animation
        self.ani = FuncAnimation(
            self.fig, 
            self.update, 
            interval=30,
            blit=True
        )
    
    def update(self, frame):
        # Read audio data
        data = self.stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Update time domain plot
        self.line_time.set_ydata(audio_data)
        
        # Compute FFT and update frequency domain plot
        # Apply window function to reduce spectral leakage
        windowed_data = audio_data * np.hanning(len(audio_data))
        fft_data = np.abs(np.fft.rfft(windowed_data))
        
        # Convert to dB scale (with protection against log(0))
        eps = 1e-10
        fft_data_db = 20 * np.log10(fft_data + eps)
        
        self.line_freq.set_ydata(fft_data_db)
        
        return [self.line_time, self.line_freq]
    
    def setup_plots(self):
        # Initialize plots with zeros
        self.line_time.set_xdata(np.arange(0, CHUNK))
        self.line_time.set_ydata(np.zeros(CHUNK))
        
        self.line_freq.set_xdata(self.freq)
        self.line_freq.set_ydata(np.zeros(len(self.freq)))
    
    def start(self):
        self.setup_plots()
        plt.show()
    
    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        plt.close()

if __name__ == "__main__":
    print("Starting audio analyzer...")
    print("Press Ctrl+C in the terminal or close the graph window to exit")
    
    try:
        analyzer = AudioAnalyzer()
        analyzer.start()
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'analyzer' in locals():
            analyzer.stop()
        print("Exited safely") 