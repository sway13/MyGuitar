import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WINDOW_SIZE = 10  # Number of chunks to display in the window

class MicrophoneWaveform:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Set up the plot
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.line, = self.ax.plot([], [], lw=2)
        
        # Set up the data buffer
        self.buffer = np.zeros(CHUNK * WINDOW_SIZE)
        
        # Configure plot
        self.ax.set_ylim(-32768, 32768)  # 16-bit audio range
        self.ax.set_xlim(0, len(self.buffer))
        self.ax.set_title('Microphone Waveform')
        self.ax.set_xlabel('Sample')
        self.ax.set_ylabel('Amplitude')
        self.ax.grid(True)
        
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
        
        # Shift buffer and add new data
        self.buffer = np.roll(self.buffer, -len(audio_data))
        self.buffer[-len(audio_data):] = audio_data
        
        # Update the line
        self.line.set_data(range(len(self.buffer)), self.buffer)
        
        return [self.line]
    
    def start(self):
        plt.show()
    
    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        plt.close()

if __name__ == "__main__":
    print("Starting microphone waveform visualization...")
    print("Press Ctrl+C in the terminal or close the graph window to exit")
    
    try:
        waveform = MicrophoneWaveform()
        waveform.start()
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'waveform' in locals():
            waveform.stop()
        print("Exited safely") 