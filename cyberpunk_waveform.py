import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
from matplotlib import cm
import colorsys

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WINDOW_SIZE = 12  # Number of chunks to display in the window
AMPLITUDE_MULTIPLIER = 4.0  # Increased amplitude for better visibility

# Create a custom calming color scheme
def create_calm_colormap():
    # Calming colors: ocean blues and forest greens
    colors = [(0, 0.1, 0.2), (0, 0.3, 0.5), (0, 0.5, 0.7), (0.1, 0.6, 0.5), (0.2, 0.7, 0.4)]
    return mpl.colors.LinearSegmentedColormap.from_list("calm", colors)

class CalmingWaveform:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Set the style to dark background
        plt.style.use('dark_background')
        
        # Create figure and configure it for calming style
        self.fig = plt.figure(figsize=(12, 8), facecolor='#001020')
        self.ax = self.fig.add_subplot(1, 1, 1)
        
        # Set a deep ocean blue background
        self.fig.patch.set_facecolor('#001020')
        self.ax.set_facecolor('#002040')  # Deep blue
        
        # Create buffer for the data
        self.buffer = np.zeros(CHUNK * WINDOW_SIZE)
        
        # Create a line for waveform with calming color
        self.line, = self.ax.plot([], [], lw=2.5, color='#00c8aa')
        
        # Configure grid with subtle accents
        self.ax.grid(True, linestyle='-', alpha=0.2, color='#007070')
        
        # Configure axes
        self.ax.set_xlim(0, len(self.buffer))
        self.ax.set_ylim(-35000 * AMPLITUDE_MULTIPLIER, 35000 * AMPLITUDE_MULTIPLIER)
        
        # Style the title and labels with calming colors
        self.ax.set_title('OCEAN WAVE AUDIO VISUALIZATION', 
                        fontsize=24, color='#00c8aa', 
                        fontweight='bold', fontname='Verdana')
        
        self.ax.set_xlabel('TIME FLOW', 
                         fontsize=14, color='#20a0a0', 
                         fontname='Verdana')
        
        self.ax.set_ylabel('WAVE AMPLITUDE', 
                         fontsize=14, color='#00c8aa', 
                         fontname='Verdana')
        
        # Remove tick labels for cleaner look but keep the ticks
        self.ax.set_xticklabels([])
        self.ax.tick_params(axis='both', colors='#00a0a0', labelsize=10)
        
        # Add gentle horizontal lines for calming effect
        self.ax.axhline(y=34000 * AMPLITUDE_MULTIPLIER, color='#004060', linestyle='-', alpha=0.4, lw=2)
        self.ax.axhline(y=-34000 * AMPLITUDE_MULTIPLIER, color='#004060', linestyle='-', alpha=0.4, lw=2)
        
        # Create animation
        self.ani = FuncAnimation(
            self.fig, 
            self.update, 
            interval=30,
            blit=True,
            save_count=100  # Limit saved frames to avoid warning
        )
        
        # Add subtle vertical grid lines
        for x in range(0, CHUNK * WINDOW_SIZE, CHUNK):
            self.ax.axvline(x=x, color='#006060', linestyle='-', alpha=0.15, lw=1)
    
    def update(self, frame):
        # Read audio data
        data = self.stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Amplify the signal
        audio_data = audio_data * AMPLITUDE_MULTIPLIER
        
        # Add dynamic color based on amplitude but keep it within calming palette
        max_amp = np.max(np.abs(audio_data))
        norm_amp = max_amp / (32768 * AMPLITUDE_MULTIPLIER)  # Normalize to 0-1 range
        
        # Change line color dynamically but stay within calm colors
        if norm_amp > 0.7:  # High amplitude - turquoise
            self.line.set_color('#00e8c0')
        elif norm_amp > 0.4:  # Medium amplitude - teal
            self.line.set_color('#00c8aa')
        else:  # Low amplitude - blue
            self.line.set_color('#0090a0')
        
        # Shift buffer and add new data
        self.buffer = np.roll(self.buffer, -len(audio_data))
        self.buffer[-len(audio_data):] = audio_data
        
        # Update the line
        self.line.set_data(range(len(self.buffer)), self.buffer)
        
        # Gentle background pulsing based on volume
        if norm_amp > 0.6:
            # Subtle pulse effect on louder sounds
            self.ax.set_facecolor('#002850')  # Slightly lighter blue
        else:
            self.ax.set_facecolor('#002040')  # Back to deeper blue
        
        return [self.line]
    
    def start(self):
        plt.tight_layout()
        plt.show()
    
    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        plt.close()

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║ OCEAN WAVE AUDIO VISUALIZER               ║
    ║ A calming audio experience                ║
    ╚═══════════════════════════════════════════╝
    """)
    print("Initializing calming wave interface...")
    print("Press Ctrl+C in terminal or close window to exit")
    
    try:
        waveform = CalmingWaveform()
        waveform.start()
    except KeyboardInterrupt:
        print("Closing the ocean...")
    except Exception as e:
        print(f"Wave error: {e}")
    finally:
        if 'waveform' in locals():
            waveform.stop()
        print("Ocean waves have calmed.") 