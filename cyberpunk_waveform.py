import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
from matplotlib import cm
import colorsys
import scipy.signal as signal
from collections import Counter

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096  # Larger chunk for better frequency resolution
WINDOW_SIZE = 8  # Number of chunks to display in the window
AMPLITUDE_MULTIPLIER = 100.0  # Extreme amplitude boost for 1000 dB-like effect
MAX_DISPLAY_VALUE = 35000 * 10  # Cap display values to prevent overflow

# Musical key detection parameters
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
MIN_KEY_CONFIDENCE = 0.4  # Minimum confidence to display a key

# Create a custom calming color scheme
def create_calm_colormap():
    # Calming colors: ocean blues and forest greens
    colors = [(0, 0.1, 0.2), (0, 0.3, 0.5), (0, 0.5, 0.7), (0.1, 0.6, 0.5), (0.2, 0.7, 0.4)]
    return mpl.colors.LinearSegmentedColormap.from_list("calm", colors)

# Function to detect the musical key
def detect_musical_key(fft_data, freqs):
    # Map frequencies to musical notes using A4 = 440Hz as reference
    # We only look at frequencies between 60Hz and 1000Hz (most musical content)
    # A0 is 27.5 Hz, C8 is 4186 Hz, we'll cover just this range
    
    # Initialize note strengths for all 12 chromatic notes
    note_strengths = [0] * 12
    
    # Only look at frequencies between 60Hz and 5000Hz (most musical content)
    freq_min, freq_max = 60, 5000
    indices = np.where((freqs >= freq_min) & (freqs <= freq_max))[0]
    
    # Extract the magnitudes corresponding to these frequencies
    mags = fft_data[indices]
    freq_subset = freqs[indices]
    
    # Threshold to only consider significant frequency peaks
    threshold = np.mean(mags) + 1.5 * np.std(mags)
    strong_indices = np.where(mags > threshold)[0]
    
    # Bail out if we don't have enough strong frequencies
    if len(strong_indices) < 3:
        return None, 0
    
    # First, find the note bins for each frequency
    for idx in strong_indices:
        freq = freq_subset[idx]
        # Calculate note from frequency using A4 = 440Hz as reference
        # Note = 12 * log2(f/440) + 69
        note_num = int(round(12 * np.log2(freq/440) + 69)) % 12
        # Add the magnitude as the strength of this note
        note_strengths[note_num] += mags[idx]
    
    # Normalize note strengths
    if sum(note_strengths) > 0:
        note_strengths = [ns / sum(note_strengths) for ns in note_strengths]
    
    # Calculate key scores for all possible keys (major and minor)
    key_scores = []
    
    # For each possible root note (C through B)
    for root in range(12):
        # Calculate major key score
        major_score = sum(note_strengths[(root + interval) % 12] for interval in MAJOR_SCALE)
        key_scores.append((f"{NOTE_NAMES[root]} major", major_score))
        
        # Calculate minor key score
        minor_score = sum(note_strengths[(root + interval) % 12] for interval in MINOR_SCALE)
        key_scores.append((f"{NOTE_NAMES[root]} minor", minor_score))
    
    # Sort by score in descending order
    key_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Get the top key and its confidence score
    top_key, confidence = key_scores[0]
    
    # Only return a key if confidence is above threshold
    if confidence > MIN_KEY_CONFIDENCE:
        return top_key, confidence
    else:
        return None, 0

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
        
        # Create waveform axis (top)
        self.ax = self.fig.add_axes([0.08, 0.25, 0.84, 0.68])
        
        # Create key detection display area (bottom)
        self.ax_key = self.fig.add_axes([0.08, 0.05, 0.84, 0.12])
        self.ax_key.set_facecolor('#001530')
        self.ax_key.set_xlim(0, 1)
        self.ax_key.set_ylim(0, 1)
        self.ax_key.axis('off')
        
        # Add text for key display
        self.key_text = self.ax_key.text(
            0.5, 0.5, "Detecting Key...", 
            ha='center', va='center',
            fontsize=28, fontweight='bold', fontname='Verdana',
            color='#00e8c0'
        )
        
        # Add confidence bar
        self.conf_bar = self.ax_key.barh(
            0.2, 0, height=0.15, color='#00e8c0', 
            left=0.1, alpha=0.7
        )[0]
        
        # Initialize key detection history
        self.detected_keys = []
        self.current_key = None
        self.key_confidence = 0
        self.key_stable_count = 0
        
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
        self.ax.set_title('1K DB OCEAN AMPLIFIER + KEY DETECTION', 
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
            interval=50,  # Slower update rate to allow for key detection processing
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
        audio_data_amplified = audio_data * AMPLITUDE_MULTIPLIER
        
        # Clip extremely high values to prevent overflow in display
        audio_data_amplified = np.clip(audio_data_amplified, -MAX_DISPLAY_VALUE, MAX_DISPLAY_VALUE)
        
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
        self.buffer = np.roll(self.buffer, -len(audio_data_amplified))
        self.buffer[-len(audio_data_amplified):] = audio_data_amplified
        
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
        
        # Every few frames, perform key detection
        if frame % 3 == 0:  # Only detect key every 3 frames to reduce CPU load
            # Perform FFT for key detection (using original, non-amplified data)
            windowed_data = audio_data * np.hanning(len(audio_data))
            fft_data = np.abs(np.fft.rfft(windowed_data))
            freqs = np.fft.rfftfreq(len(audio_data), 1/RATE)
            
            # Detect musical key
            detected_key, confidence = detect_musical_key(fft_data, freqs)
            
            # If we detected a key, add it to history
            if detected_key:
                self.detected_keys.append(detected_key)
                # Keep only the last 10 detections
                if len(self.detected_keys) > 10:
                    self.detected_keys.pop(0)
                
                # Find the most common key in recent history
                if self.detected_keys:
                    key_counts = Counter(self.detected_keys)
                    common_key, count = key_counts.most_common(1)[0]
                    
                    # If we have enough stability, update the displayed key
                    if count >= 3:  # Key must appear at least 3 times to be considered stable
                        if common_key == self.current_key:
                            self.key_stable_count += 1
                        else:
                            self.current_key = common_key
                            self.key_stable_count = 1
                            self.key_confidence = confidence
            
            # Update key display
            if self.current_key and self.key_stable_count >= 2:
                # Show detected key with large text
                self.key_text.set_text(f"Detected Key: {self.current_key}")
                
                # Change color based on confidence
                if self.key_confidence > 0.7:
                    self.key_text.set_color('#00ff80')  # High confidence - brighter green
                    key_color = '#00ff80'
                elif self.key_confidence > 0.5:
                    self.key_text.set_color('#00d8c0')  # Medium confidence
                    key_color = '#00d8c0'
                else:
                    self.key_text.set_color('#00a0a0')  # Low confidence
                    key_color = '#00a0a0'
                
                # Update confidence bar
                self.conf_bar.set_width(0.8 * self.key_confidence)
                self.conf_bar.set_color(key_color)
            else:
                self.key_text.set_text("Detecting Key...")
                self.key_text.set_color('#00a0a0')  # Default color
                self.conf_bar.set_width(0.1)  # Minimal bar when no key is detected
        
        return [self.line, self.ripple_line, self.key_text, self.conf_bar]
    
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
    ╔════════════════════════════════════════════════════════════╗
    ║ 1K DB OCEAN AMPLIFIER WITH MUSICAL KEY DETECTION           ║
    ║ Experience the depths of sound & identify musical keys      ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    print("Initializing ultra-amplified ocean interface with key detection...")
    print("Play a musical instrument or sing to detect the key")
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