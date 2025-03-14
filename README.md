# Mac Microphone Waveform Visualizer

This project provides tools to capture audio from your Mac's microphone and visualize it in real-time with various styles.

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- virtualenvwrapper (for environment management)

## Setup

1. Create and activate a virtual environment:

```bash
mkvirtualenv guitar
workon guitar
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Note: On macOS, you may need to install PortAudio first if PyAudio installation fails:

```bash
# Using Homebrew
brew install portaudio

# Then install PyAudio with the correct paths
CFLAGS="-I/opt/homebrew/include" LDFLAGS="-L/opt/homebrew/lib" pip install pyaudio
```

## Available Visualizers

### 1. Basic Waveform Visualizer

A simple application that displays the audio waveform in real-time.

```bash
python audio_waveform.py
```

### 2. Audio Spectrum Analyzer

A visualization that shows both the waveform and frequency spectrum.

```bash
python spectrum_analyzer.py
```

### 3. Cyberpunk Waveform Visualizer

A stylized neon-themed waveform visualizer inspired by cyberpunk aesthetics, featuring dynamic color changes and amplified waveform.

```bash
python cyberpunk_waveform.py
```

### 4. Samurai Audio Matrix

A John Wick-inspired visualizer with red samurai aesthetics, featuring a main waveform display and a stylized spectrum visualization.

```bash
python samurai_spectrum.py
```

## Features

### Basic Waveform Visualizer
- Real-time audio capture from the microphone
- Simple waveform visualization

### Audio Spectrum Analyzer
- Dual display with both time domain (waveform) and frequency domain (spectrum)
- Logarithmic frequency scale for better visualization of the entire audio spectrum
- dB scale for frequency magnitudes

### Cyberpunk Waveform Visualizer
- Amplified waveform for better visibility
- Neon cyan/pink color scheme on dark background
- Dynamic color changes based on audio intensity
- Background effects that respond to sound
- Stylized grid and accent lines

### Samurai Audio Matrix
- John Wick inspired color scheme with red accents
- Main waveform display with amplified signal
- Stylized frequency bars that change color with intensity
- Japanese kanji character watermark
- Samurai sword-inspired design elements
- Pulse effects on strong beats

## Usage

- All visualizers will display the audio from your Mac's microphone in real-time
- To stop any visualizer, close the visualization window or press Ctrl+C in the terminal

## Troubleshooting

- If you encounter permission issues with accessing the microphone, make sure your terminal or IDE has microphone access enabled in System Preferences/Settings > Security & Privacy > Privacy > Microphone.
- If the visualizations appear too small or too large, you can adjust the figure size in the code by modifying the `figsize` parameter.
- For the spectrum analyzer, you can adjust the frequency range and dB range by modifying the `set_xlim` and `set_ylim` values in the code. 