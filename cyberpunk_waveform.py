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
AMPLITUDE_MULTIPLIER = 100.0  # Extreme amplitude boost for 1000 dB-like effect
MAX_DISPLAY_VALUE = 35000 * 10  # Cap display values to prevent overflow

# Create a custom calming color scheme
def create_calm_colormap():
    # Calming colors: ocean blues and forest greens
    colors = [(0, 0.1, 0.2), (0, 0.3, 0.5), (0, 0.5, 0.7), (0.1, 0.6, 0.5), (0.2, 0.7, 0.4)]
    return mpl.colors.LinearSegmentedColormap.from_list("calm", colors)

class UltraAmplifiedWaveform:
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
        
        # Create figure and configure it for ultra-amplified style
        self.fig = plt.figure(figsize=(14, 9), facecolor='#001020')
        self.ax = self.fig.add_subplot(1, 1, 1)
        
        # Set a deep ocean blue background
        self.fig.patch.set_facecolor('#001020')
        self.ax.set_facecolor('#002040')  # Deep blue
        
        # Create buffer for the data
        self.buffer = np.zeros(CHUNK * WINDOW_SIZE)
        
        # Create a line for waveform with calming color
        self.line, = self.ax.plot([], [], lw=3.0, color='#00c8aa')
        
        # Configure grid with subtle accents
        self.ax.grid(True, linestyle='-', alpha=0.2, color='#007070')
        
        # Configure axes - with extreme range to handle 1000 dB effect
        self.ax.set_xlim(0, len(self.buffer))
        self.ax.set_ylim(-MAX_DISPLAY_VALUE, MAX_DISPLAY_VALUE)
        
        # Style the title and labels with calming colors but highlight extreme amplitude
        self.ax.set_title('1K DB OCEAN AMPLIFIER', 
                        fontsize=28, color='#00e8c0', 
                        fontweight='bold', fontname='Verdana')
        
        self.ax.set_xlabel('TIME FLOW', 
                         fontsize=14, color='#20a0a0', 
                         fontname='Verdana')
        
        self.ax.set_ylabel('ULTRA AMPLITUDE (1K DB)', 
                         fontsize=16, color='#00e8c0', 
                         fontname='Verdana')
        
        # Remove tick labels for cleaner look but keep the ticks
        self.ax.set_xticklabels([])
        self.ax.tick_params(axis='both', colors='#00a0a0', labelsize=10)
        
        # Add horizontal indicator lines showing the normal range vs ultra-amplified range
        # Normal range at 32768 (16-bit audio)
        self.ax.axhline(y=32768, color='#20a0a0', linestyle='--', alpha=0.4, lw=1.5)
        self.ax.axhline(y=-32768, color='#20a0a0', linestyle='--', alpha=0.4, lw=1.5)
        
        # Add text indicators for the normal range vs amplified range
        self.ax.text(len(self.buffer)*0.02, 40000, 'NORMAL RANGE', 
                    color='#20a0a0', fontsize=10, alpha=0.7)
        
        # Add gentle horizontal lines for calming effect at the extreme bounds
        self.ax.axhline(y=MAX_DISPLAY_VALUE*0.95, color='#00e8c0', linestyle='-', alpha=0.5, lw=2)
        self.ax.axhline(y=-MAX_DISPLAY_VALUE*0.95, color='#00e8c0', linestyle='-', alpha=0.5, lw=2)
        
        # Add water ripple effect at the bottom of the plot for visual effect
        ripple_x = np.linspace(0, len(self.buffer), 200)
        ripple_y = np.sin(ripple_x/1000) * 5000 - MAX_DISPLAY_VALUE * 0.9
        self.ripple_line, = self.ax.plot(ripple_x, ripple_y, color='#00a0e0', alpha=0.3, lw=2)
        self.ripple_phase = 0
        
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
        
        # Get pre-amplified max for color decisions
        pre_max = np.max(np.abs(audio_data))
        pre_norm = pre_max / 32768  # Normalize to 0-1 range based on original signal
        
        # Amplify the signal with extreme multiplier
        audio_data = audio_data * AMPLITUDE_MULTIPLIER
        
        # Clip extremely high values to prevent overflow in display
        audio_data = np.clip(audio_data, -MAX_DISPLAY_VALUE, MAX_DISPLAY_VALUE)
        
        # Change line color dynamically but stay within calm colors
        # Use the pre-amplified value for smoother color transitions
        if pre_norm > 0.7:  # High amplitude - bright turquoise
            self.line.set_color('#00fff0')
            self.line.set_linewidth(4.0)  # Thicker line for high amplitude
        elif pre_norm > 0.4:  # Medium amplitude - teal
            self.line.set_color('#00d8c0')
            self.line.set_linewidth(3.0)
        else:  # Low amplitude - blue
            self.line.set_color('#0090a0')
            self.line.set_linewidth(2.5)
        
        # Shift buffer and add new data
        self.buffer = np.roll(self.buffer, -len(audio_data))
        self.buffer[-len(audio_data):] = audio_data
        
        # Update the line
        self.line.set_data(range(len(self.buffer)), self.buffer)
        
        # Update ripple effect at the bottom
        self.ripple_phase += 0.1
        ripple_x = np.linspace(0, len(self.buffer), 200)
        # Make the ripple amplitude responsive to audio
        ripple_amp = 5000 + pre_norm * 15000
        ripple_y = np.sin(ripple_x/1000 + self.ripple_phase) * ripple_amp - MAX_DISPLAY_VALUE * 0.9
        self.ripple_line.set_ydata(ripple_y)
        
        # Gentle background pulsing based on volume
        if pre_norm > 0.6:
            # Subtle pulse effect on louder sounds
            self.ax.set_facecolor('#003060')  # More vibrant blue for high amplitude
        else:
            self.ax.set_facecolor('#002040')  # Back to deeper blue
        
        return [self.line, self.ripple_line]
    
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
    ╔═══════════════════════════════════════════════════╗
    ║ 1K DB ULTRA-AMPLIFIED OCEAN WAVE VISUALIZER       ║
    ║ Experience the depths of sound at 1000 decibels    ║
    ╚═══════════════════════════════════════════════════╝
    """)
    print("Initializing ultra-amplified ocean interface...")
    print("Press Ctrl+C in terminal or close window to exit")
    
    try:
        waveform = UltraAmplifiedWaveform()
        waveform.start()
    except KeyboardInterrupt:
        print("Closing the amplified ocean...")
    except Exception as e:
        print(f"Wave error: {e}")
    finally:
        if 'waveform' in locals():
            waveform.stop()
        print("The ocean has returned to normal amplitude.") 