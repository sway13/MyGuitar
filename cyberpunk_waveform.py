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
AMPLITUDE_MULTIPLIER = 2.5  # Amplify the signal

# Create a custom cyberpunk color scheme
def create_cyberpunk_colormap():
    # Cyberpunk colors: neons against dark background
    colors = [(0, 0, 0.1), (0, 0.5, 1), (0, 1, 1), (1, 0, 0.5), (1, 0, 0.2)]
    return mpl.colors.LinearSegmentedColormap.from_list("cyberpunk", colors)

class CyberpunkWaveform:
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
        
        # Create figure and configure it for cyberpunk style
        self.fig = plt.figure(figsize=(12, 8), facecolor='black')
        self.ax = self.fig.add_subplot(1, 1, 1)
        
        # Set a dark gradient background
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('#050518')  # Dark blue-black
        
        # Create buffer for the data
        self.buffer = np.zeros(CHUNK * WINDOW_SIZE)
        
        # Create a line collection for waveform with gradient
        self.line, = self.ax.plot([], [], lw=2.5, color='#00eeff')
        
        # Configure grid with neon accents
        self.ax.grid(True, linestyle='-', alpha=0.2, color='#ff00aa')
        
        # Configure axes
        self.ax.set_xlim(0, len(self.buffer))
        self.ax.set_ylim(-35000 * AMPLITUDE_MULTIPLIER, 35000 * AMPLITUDE_MULTIPLIER)
        
        # Style the title and labels with neon glow effect
        self.ax.set_title('NEURAL AUDIO INTERFACE', 
                        fontsize=24, color='#00eeff', 
                        fontweight='bold', fontname='monospace')
        
        self.ax.set_xlabel('TEMPORAL SEQUENCE', 
                         fontsize=14, color='#ff00aa', 
                         fontname='monospace')
        
        self.ax.set_ylabel('SIGNAL AMPLITUDE', 
                         fontsize=14, color='#00eeff', 
                         fontname='monospace')
        
        # Remove tick labels for cleaner look but keep the ticks
        self.ax.set_xticklabels([])
        self.ax.tick_params(axis='both', colors='#00eeff', labelsize=10)
        
        # Add a "samurai" touch with red accent lines at the top and bottom
        self.ax.axhline(y=34000 * AMPLITUDE_MULTIPLIER, color='#ff0000', linestyle='-', alpha=0.7, lw=2)
        self.ax.axhline(y=-34000 * AMPLITUDE_MULTIPLIER, color='#ff0000', linestyle='-', alpha=0.7, lw=2)
        
        # Create animation
        self.ani = FuncAnimation(
            self.fig, 
            self.update, 
            interval=20,
            blit=True,
            save_count=100  # Limit saved frames to avoid warning
        )
        
        # Add subtle red vertical grid lines for the "tech" feel
        for x in range(0, CHUNK * WINDOW_SIZE, CHUNK):
            self.ax.axvline(x=x, color='#ff0000', linestyle='-', alpha=0.2, lw=1)
    
    def update(self, frame):
        # Read audio data
        data = self.stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Amplify the signal
        audio_data = audio_data * AMPLITUDE_MULTIPLIER
        
        # Add dynamic color based on amplitude
        max_amp = np.max(np.abs(audio_data))
        norm_amp = max_amp / (32768 * AMPLITUDE_MULTIPLIER)  # Normalize to 0-1 range
        
        # Change line color dynamically based on amplitude
        if norm_amp > 0.7:  # High amplitude - red
            self.line.set_color('#ff0055')
        elif norm_amp > 0.4:  # Medium amplitude - purple
            self.line.set_color('#aa00ff')
        else:  # Low amplitude - cyan
            self.line.set_color('#00eeff')
        
        # Shift buffer and add new data
        self.buffer = np.roll(self.buffer, -len(audio_data))
        self.buffer[-len(audio_data):] = audio_data
        
        # Update the line
        self.line.set_data(range(len(self.buffer)), self.buffer)
        
        # Flash the background slightly based on volume
        if norm_amp > 0.6:
            # Create a flash effect on loud sounds
            self.ax.set_facecolor('#0a0a30')  # Slightly lighter blue
        else:
            self.ax.set_facecolor('#050518')  # Back to darker blue
        
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
    ║ CYBERPUNK AUDIO VISUALIZER                ║
    ║ Inspired by John Wick's neon aesthetics   ║
    ╚═══════════════════════════════════════════╝
    """)
    print("Starting neural audio interface...")
    print("Press Ctrl+C in terminal or close window to exit")
    
    try:
        waveform = CyberpunkWaveform()
        waveform.start()
    except KeyboardInterrupt:
        print("Terminating connection...")
    except Exception as e:
        print(f"System error: {e}")
    finally:
        if 'waveform' in locals():
            waveform.stop()
        print("Neural interface disconnected.") 