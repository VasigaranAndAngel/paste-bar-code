# Paste Bar Code

A Python desktop application for real-time barcode detection and automated text input. Built with PySide6 and OpenCV, this application captures video from cameras or other sources, detects barcodes/QR codes, and automatically types the decoded content.

## Download

[![Download Latest Release](https://img.shields.io/github/release/vasigaranandangel/paste-bar-code.svg?label=Download&style=for-the-badge)](https://github.com/vasigaranandangel/paste-bar-code/releases/latest)

## Features

### Core Functionality
- **Real-time Barcode Detection**: Detects and decodes barcodes and QR codes from video feeds
- **Automatic Text Input**: Automatically types detected codes into any active application
- **Visual Feedback**: Shows video feed with highlighted detected barcodes
- **Audio Feedback**: Optional beep sound when codes are detected

### Capture Sources
- **Camera Capture**: Direct capture from webcams and cameras
- **Flask Web Interface**: Capture from web-based camera feeds *Not implemented yet (need help)*

### Configuration Options
- **Lock Interval**: Configurable delay between code detections (default: 1.5 seconds)
- **Auto-Press Enter**: Option to automatically press Enter after typing codes
- **Audio Feedback**: Toggle beep sound on/off *Not implemented in UI yet*
- **Type Codes**: Toggle automatic typing of detected codes *Not implemented in UI yet*
- **Window Management**: Always-on-top mode and position memory *Not implemented in UI yet*
- **Video Settings**: Frame flipping and capture source selection

## Usage

### Quick Start
1. **Download the latest release** from the GitHub releases page (see download button above)
2. **Run the executable** - No installation required, just double-click the `.exe` file
3. **Start scanning** - The application will open with camera feed ready for barcode detection

### How to Use
1. **Launch the application** - The main window will open showing the camera feed
2. **Select capture source** - Choose from the dropdown menu
3. **Configure settings** - Adjust lock interval, enable/disable features as needed
4. **Scan barcodes** - Point camera at barcodes/QR codes
5. **Automatic input** - Detected codes will be typed automatically into the active application

## Development

### Prerequisites
- Python 3.13

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd paste-bar-code
```

2. Install dependencies using UV:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

### Running the Application
```bash
python src/main.py
```

Or use UV to run:
```bash
uv run python src/main.py
```

### Command Line Options
- `--version`: Display version information and exit

### Building Executable

Install PyInstaller and build:
```bash
uv sync --group setup
uv run pyinstaller main.spec
```

The executable will be created in the `dist/` directory.

## Dependencies

- **PySide6**: Qt-based GUI framework
- **OpenCV**: Computer vision and image processing
- **pyzbar**: Barcode/QR code decoding
- **PyAutoGUI**: Automated keyboard input
- **Flask**: Web interface for camera streaming
- **eventlet**: WebSocket support for Flask

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
