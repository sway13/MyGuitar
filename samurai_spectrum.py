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
CHUNK = 2048  # Larger chunk for better frequency resolution
AMPLITUDE_MULTIPLIER = 3.0  # Amplify the signal
SPECTRUM_HEIGHT = 0.3  # Height of the spectrum display

class SamuraiAudioVisualizer:
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
        
        # Create main figure
        self.fig = plt.figure(figsize=(14, 8), facecolor='black')
        
        # Create main waveform axis (top 70%)
        self.ax_wave = self.fig.add_axes([0.08, 0.35, 0.88, 0.58])
        
        # Create small spectrum axis at the bottom (30%)
        self.ax_spec = self.fig.add_axes([0.08, 0.08, 0.88, 0.20])
        
        # Set background colors
        self.fig.patch.set_facecolor('black')
        self.ax_wave.set_facecolor('#080010')  # Dark purple-black
        self.ax_spec.set_facecolor('#080010')  # Match wave background
        
        # Prepare waveform data
        self.wave_buffer = np.zeros(CHUNK)
        self.line_wave, = self.ax_wave.plot([], [], lw=2.5, color='#ed1100')
        
        # Prepare spectrum data
        self.freq = np.fft.rfftfreq(CHUNK, 1/RATE)
        self.spec_data = np.zeros(len(self.freq))
        self.bars = self.ax_spec.bar(
            self.freq[1:200:4],  # Only show lower frequencies with spaced bars
            np.zeros(len(range(1, 200, 4))),
            width=self.freq[5] - self.freq[1],  # Bar width
            color='#ed1100',
            alpha=0.8
        )
        
        # Configure waveform display
        self.ax_wave.set_xlim(0, CHUNK)
        self.ax_wave.set_ylim(-32768 * AMPLITUDE_MULTIPLIER, 32768 * AMPLITUDE_MULTIPLIER)
        self.ax_wave.set_title('RONIN AUDIO MATRIX', 
                             fontsize=26, 
                             color='#ed1100', 
                             fontweight='bold', 
                             fontname='monospace')
        self.ax_wave.set_ylabel('SIGNAL PATH', 
                              fontsize=14, 
                              color='#ed1100', 
                              fontname='monospace')
        
        # Configure spectrum display
        self.ax_spec.set_xlim(20, 5000)  # Focus on audible range
        self.ax_spec.set_ylim(0, 100)  # Fixed height for bars
        self.ax_spec.set_xlabel('FREQUENCY DOMAIN', 
                              fontsize=14, 
                              color='#ed1100', 
                              fontname='monospace')
        
        # Styling for both plots
        for ax in [self.ax_wave, self.ax_spec]:
            # Red grid with horizontal emphasis
            ax.grid(True, linestyle='-', alpha=0.15, color='#ed1100', which='both')
            ax.grid(True, linestyle='-', alpha=0.25, color='#ed1100', which='major', axis='y')
            
            # Style tick labels
            ax.tick_params(axis='x', colors='#ed1100', labelsize=10)
            ax.tick_params(axis='y', colors='#ed1100', labelsize=10)
            
            # Add red accent border
            for spine in ax.spines.values():
                spine.set_edgecolor('#ed1100')
                spine.set_linewidth(2)
        
        # Remove tick labels from waveform x-axis for cleaner look
        self.ax_wave.set_xticklabels([])
        
        # Add decorative elements
        # Top and bottom accent lines (Samurai sword aesthetic)
        y_val = 32000 * AMPLITUDE_MULTIPLIER
        self.ax_wave.axhline(y=y_val, color='#ed1100', linestyle='-', alpha=0.9, lw=2)
        self.ax_wave.axhline(y=-y_val, color='#ed1100', linestyle='-', alpha=0.9, lw=2)
        
        # Create animation
        self.ani = FuncAnimation(
            self.fig, 
            self.update, 
            interval=20,
            blit=True,
            save_count=100  # Limit saved frames to avoid warning
        )
        
        # Add kanji character for "sound" or "listen" as a watermark
        self.ax_wave.text(0.97, 0.05, '音', 
                        transform=self.ax_wave.transAxes,
                        fontsize=60, color='#ed1100', alpha=0.3,
                        ha='right', va='bottom', fontname='serif')
    
    def update(self, frame):
        # Read audio data
        data = self.stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Amplify the waveform
        amplified_data = audio_data * AMPLITUDE_MULTIPLIER
        
        # Update waveform
        self.line_wave.set_data(range(len(audio_data)), amplified_data)
        
        # Compute FFT with window function
        windowed_data = audio_data * np.hanning(len(audio_data))
        fft_data = np.abs(np.fft.rfft(windowed_data))
        
        # Convert to dB scale
        eps = 1e-10
        fft_data_db = 20 * np.log10(fft_data + eps)
        
        # Normalize to 0-100 range for visualization
        fft_data_normalized = np.interp(fft_data_db, 
                                      [-80, 0], 
                                      [0, 100])
        
        # Update bar heights in spectrum
        for i, bar in enumerate(self.bars):
            idx = 1 + i * 4  # Get the corresponding frequency index
            if idx < len(fft_data_normalized):
                height = fft_data_normalized[idx]
                bar.set_height(height)
                
                # Dynamic coloring based on height
                if height > 70:
                    # Bright red for high amplitude
                    bar.set_color('#ff2200')
                elif height > 40:
                    # Orange-red for medium amplitude
                    bar.set_color('#ed1100')
                else:
                    # Darker red for low amplitude
                    bar.set_color('#850a00')
        
        # Add "pulse" effect on strong beats
        max_amp = np.max(np.abs(audio_data))
        norm_amp = max_amp / 32768  # Normalize to 0-1 range
        
        if norm_amp > 0.7:
            # Flash effect on strong beats
            self.ax_wave.set_facecolor('#120015')  # Lighter background
            self.ax_spec.set_facecolor('#120015')
            
            # Add additional horizontal lines during beats for a "motion" effect
            self.line_wave.set_linewidth(3.0)
        else:
            # Return to normal
            self.ax_wave.set_facecolor('#080010')  # Normal background
            self.ax_spec.set_facecolor('#080010')
            self.line_wave.set_linewidth(2.5)
        
        return [self.line_wave] + list(self.bars)
    
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
    ║  SAMURAI AUDIO MATRIX                     ║
    ║  Neo-Tokyo Spectrum Visualizer            ║
    ╚═══════════════════════════════════════════╝
    """)
    print("Initializing sound katana...")
    print("Press Ctrl+C in terminal or close window to exit")
    
    try:
        visualizer = SamuraiAudioVisualizer()
        visualizer.start()
    except KeyboardInterrupt:
        print("Sheathing blade...")
    except Exception as e:
        print(f"Battle error: {e}")
    finally:
        if 'visualizer' in locals():
            visualizer.stop()
        print("技を終えました (Technique completed.)") 