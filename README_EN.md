# AmazingHand Hackathon Demo

<div align="center">

<a href="https://www.seeedstudio.com/Amazing-Hand-Right-Hand-The-Open-Source-Robotic-Hand-Developer-Kit.html" target="_blank">
<img src="./buyone.png" alt="Buy AmazingHand" width="600"/>
</a>

### 🔥 [🛒 Buy AmazingHand Developer Kit Now](https://www.seeedstudio.com/Amazing-Hand-Right-Hand-The-Open-Source-Robotic-Hand-Developer-Kit.html) 🔥

![AmazingHand Logo](https://img.shields.io/badge/AmazingHand-Hackathon%20Demo-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

## 🌐 Language / 语言 / Idioma
**[🇺🇸 English](README_EN.md)** | **[🇨🇳 中文](README.md)** | **[🇪🇸 Español](README_ES.md)**

## 🤖 Project Overview

This is a hackathon demo collection for the AmazingHand robotic hand project, featuring multiple complete control solutions.

</div>

## 📸 Project Showcase

### Case 1: Gesture Control & Point Playback
<table>
<tr>
<td><img src="./case1/case_1_1.png" alt="Gesture Control Interface" width="400"/></td>
<td><img src="./case1/case_1_2.png" alt="Point Playback GUI" width="400"/></td>
</tr>
<tr>
<td align="center">Web Gesture Control Interface</td>
<td align="center">Point Playback GUI</td>
</tr>
</table>

### Case 2: Servo Monitor & Teaching
<table>
<tr>
<td><img src="./case2/case_2_1.png" alt="Servo Monitor Interface" width="600"/></td>
</tr>
<tr>
<td align="center">Real-time Servo Monitor Interface</td>
</tr>
</table>

### Case 3: Full DOF Dynamic Control
<table>
<tr>
<td><img src="./case3/case_3_1.png" alt="Full DOF Control Interface" width="600"/></td>
</tr>
<tr>
<td align="center">Web Precision Control Interface</td>
</tr>
</table>

### Case 4: MuJoCo Simulation Control
<table>
<tr>
<td><img src="./case4/case_4_1.png" alt="MuJoCo Simulation" width="400"/></td>
<td><img src="./case4/case_4_2.png" alt="Single Hand Control" width="400"/></td>
<td><img src="./case4/case_4_3.png" alt="Dual Hand Control" width="400"/></td>
</tr>
<tr>
<td align="center">MuJoCo Physics Simulation</td>
<td align="center">Single Hand Web Control</td>
<td align="center">Dual Hand Cooperative Control</td>
</tr>
</table>

### Case 5: ESP32-C3 Embedded Control
<table>
<tr>
<td><img src="./case5/case_5_1.png" alt="ESP32 Hardware" width="400"/></td>
<td><img src="./case5/case_5_2.png" alt="WiFi Control Interface" width="400"/></td>
<td><img src="./case5/case_5_3.png" alt="Mobile Control" width="400"/></td>
<td><img src="./case5/case_5_4.png" alt="Standalone Operation" width="400"/></td>
</tr>
<tr>
<td align="center">ESP32-C3 Hardware</td>
<td align="center">WiFi Web Control</td>
<td align="center">Mobile Adaptation</td>
<td align="center">Standalone Portable Operation</td>
</tr>
</table>

## 📋 Case List

| Case | Name | Description | Tech Stack |
|------|------|-------------|------------|
| [**case1**](./case1/) | 🖐️ Gesture Control & Point Playback | WebSocket + Web gesture recognition + PySide6 playback | rustypot, MediaPipe, WebSocket |
| [**case2**](./case2/) | 📊 Servo Monitor & Teaching | FTServo SDK + Real-time monitoring + Point recording | FTServo SDK, PySide6 |
| [**case3**](./case3/) | 🎯 Full DOF Dynamic Control | WebSocket + Precise control + Dynamic demo | rustypot, WebSocket |
| [**case4**](./case4/) | 🧮 MuJoCo Simulation Control | Physics simulation + Web control + 3D visualization | MuJoCo, FastAPI, HTML5 |
| [**case5**](./case5/) | 📡 ESP32-C3 Embedded Control | Microcontroller + WiFi control + Standalone | ESP32-C3, Arduino, WiFi |

## 🚀 Quick Start

### 📌 Case 1: Gesture Control Solution

```bash
cd case1

# 1. Start WebSocket server
python websocket_server.py

# 2. Open Web control interface
# Open gesture_control.html in browser

# 3. (Optional) Use GUI for point playback
python playback_gui.py
```

> 💡 **Best for**: Gesture recognition, remote web control, motion recording & playback

---

### 📌 Case 2: Servo Monitor Solution

```bash
cd case2

# Start monitoring GUI
python servo_monitor.py
```

> 💡 **Best for**: Servo debugging, manual teaching, status monitoring

---

### 📌 Case 3: Full DOF Dynamic Control Solution

```bash
cd case3

# Start server
python fulldof_server.py

# Open control interface
# Open fulldof_control.html in browser
```

> 💡 **Best for**: Precise control, dynamic demonstration, gesture research

---

### 📌 Case 4: MuJoCo Simulation Control Solution

```bash
cd case4

# Single hand simulation
python simulation_server.py

# Dual hand simulation (optional)
python dual_hand_simulation.py --mode both

# Open control interface
# Open single_hand_control.html or dual_hand_control.html in browser
```

> 💡 **Best for**: Algorithm validation, educational demonstration, hardware-free prototype development

---

### 📌 Case 5: ESP32-C3 Embedded Control Solution

```bash
cd case5

# Arduino IDE approach
# Open esp32_controller.ino
# Select board: XIAO ESP32-C3
# Compile and upload

# PlatformIO approach (recommended)
pio run --target upload
pio device monitor

# WiFi control
# After uploading src/esp32_main.cpp
# Connect to WiFi hotspot "AmazingHand"
# Visit http://192.168.4.1
```

> 💡 **Best for**: Standalone demonstration, portable control, embedded applications

---

### 📌 Tools: Utility Collection

```bash
cd tools

# Servo centering tool (supports 16 servos)
python servo_center.py

# Simple centering tool
python simple_center.py
```

> 💡 **Best for**: Robotic hand initialization, servo calibration, basic debugging

## ⚙️ Hardware Support

| Case | Hardware Requirement | Description |
|------|---------------------|-------------|
| Case 1-3 | ✅ AmazingHand Robotic Hand | 8 servos (ID 11-18), 4 fingers, 2 servos per finger (bend + swing) |
| Case 4 | ❌ No Hardware Required | Pure software simulation |
| Case 5 | ✅ ESP32-C3 | Microcontroller hardware with WiFi control support |

### 🦾 Robotic Hand Specifications
- **Servo Count**: 8 servos (ID 11-18)
- **Finger Configuration**: 4 fingers (Thumb, Index, Middle, Ring)
- **DOF**: 2 degrees of freedom per finger (bend + swing)

## 📊 Technical Comparison

| Feature | Case 1 | Case 2 | Case 3 | Case 4 | Case 5 |
|---------|--------|--------|--------|--------|--------|
| **Servo SDK** | rustypot | FTServo (FEETECH) | rustypot | None (pure simulation) | SCServo |
| **Control Method** | 🌐 WebSocket Remote | 🔌 Local Serial | 🌐 WebSocket Remote | 📡 HTTP API | 📶 Embedded Control |
| **User Interface** | 🌐 Web + 💻 PySide6 | 💻 PySide6 | 🌐 Web | 🌐 Web | 📶 WiFi Web |
| **Gesture Recognition** | ✅ (MediaPipe) | ❌ | ❌ | ❌ | ❌ |
| **Real-time Monitoring** | ⚡ Basic | 📊 Detailed | ⚡ Real-time | ⚡ Real-time | ⚡ Real-time |
| **Precise Control** | ✅ | ✅ | ✅ Full Support | ✅ | ✅ |
| **Dynamic Demo** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Physics Simulation** | ❌ | ❌ | ❌ | ✅ (MuJoCo) | ❌ |
| **Hardware Requirement** | 🔧 Required | 🔧 Required | 🔧 Required | 💻 Not Required | 🔧 Required (ESP32) |
| **Standalone Operation** | ❌ | ❌ | ❌ | ❌ | ✅ |

## 📁 Directory Structure

```bash
hackathon_demo/
├── 📄 README.md                    # This document
├── 📄 README_EN.md                 # English version
├── 📄 README_ES.md                 # Spanish version
├── 📂 case1/                       # 🖐️ Gesture control solution
│   ├── 📄 README.md
│   ├── 🐍 websocket_server.py      # WebSocket server
│   ├── 🌐 gesture_control.html     # Web gesture control interface
│   ├── 💻 playback_gui.py          # Point playback GUI
│   └── 📸 case_1_1.png, case_1_2.png # Interface screenshots
├── 📂 case2/                       # 📊 Servo monitor solution
│   ├── 📄 README.md
│   ├── 🐍 servo_monitor.py         # Servo monitor GUI
│   ├── 📂 FTServo_Python/          # FEETECH servo SDK
│   └── 📸 case_2_1.png             # Interface screenshot
├── 📂 case3/                       # 🎯 Full DOF control solution
│   ├── 📄 README.md
│   ├── 🐍 fulldof_server.py        # Full DOF server
│   ├── 🌐 fulldof_control.html     # Precision control interface
│   └── 📸 case_3_1.png             # Interface screenshot
├── 📂 case4/                       # 🧮 MuJoCo simulation solution
│   ├── 📄 README.md
│   ├── 🐍 simulation_server.py     # Single hand simulation server
│   ├── 🐍 dual_hand_simulation.py  # Dual hand simulation server
│   ├── 🌐 single_hand_control.html # Single hand control interface
│   ├── 🌐 single_hand_control_en.html # Single hand control interface(English)
│   ├── 🌐 dual_hand_control.html   # Dual hand control interface
│   ├── 📂 AHSimulation/            # Simulation models
│   │   ├── 📂 AH_Right/           # Right hand model
│   │   └── 📂 AH_Left/            # Left hand model
│   ├── 📄 dual_hand_model.xml     # Dual hand model file
│   └── 📸 case_4_1.png, case_4_2.png, case_4_3.png # Interface screenshots
├── 📂 case5/                       # 📡 ESP32-C3 embedded solution
│   ├── 📄 README.md                # Detailed documentation
│   ├── 📄 esp32_controller.ino     # Arduino main program
│   ├── 📄 servo_scanner.ino        # Servo scanner utility
│   ├── 📂 src/esp32_main.cpp       # PlatformIO main program
│   ├── 📄 platformio.ini           # PlatformIO configuration
│   ├── 📂 lib/                     # Dependencies
│   ├── 📄 WIFI_SETUP_GUIDE.md      # WiFi setup guide
│   ├── 📄 FINGER_CONTROL_GUIDE.md  # Control guide
│   └── 📸 case_5_1.png ~ case_5_4.png # Hardware and interface screenshots
└── 📂 tools/                       # 🔧 Utility collection
    ├── 📄 README.md                # Tool usage documentation
    ├── 🐍 servo_center.py          # Servo centering tool
    └── 🐍 simple_center.py         # Simple centering tool
```

## 🛠️ Dependencies Installation

### 📦 Common Dependencies
```bash
pip install pyside6 numpy pyserial
```

### 📦 Case 1 & 3 Additional Dependencies
```bash
pip install websockets rustypot
```

### 📦 Case 2 No Additional Dependencies
> (SDK already included)

### 📦 Case 4 Additional Dependencies
```bash
pip install mujoco fastapi uvicorn pydantic
```

### 📦 Case 5 Development Environment
- Arduino IDE or PlatformIO
- SCServo library

### 📦 Tools Additional Dependencies
```bash
pip install rustypot
```

## 🔗 Related Links

### 📚 About rustypot
[rustypot](https://github.com/pollen-robotics/rustypot) is a Python servo control library developed by Pollen Robotics, supporting multiple servo protocols including the SCS0009 series.

### 📚 About MuJoCo
[MuJoCo](https://mujoco.readthedocs.io/) is a high-performance physics engine designed for fields like robot simulation and game development. Case 4 uses MuJoCo to provide precise physics simulation environments.

## ⚠️ Important Notes

> 🔔 **Important Reminders**:
>
> 1. **Serial Port Permissions** (Linux)
>    ```bash
>    sudo chmod 666 /dev/ttyACM0
>    ```
>
> 2. **Multiple cases use different SDKs**, do not run simultaneously
>
> 3. **Web interface requires camera permissions** for gesture recognition (Case 1 only)
>
> 4. **Case 4 requires OpenGL support**, ensure your system supports 3D rendering
>
> 5. **Case 5 requires ESP32-C3 hardware** with WiFi control functionality

## 📜 License

<div align="center">

![License](https://img.shields.io/badge/License-MIT-green.svg)
![GitHub stars](https://img.shields.io/github/stars/tianrking/AmazingHand?style=social)
![GitHub forks](https://img.shields.io/github/forks/tianrking/AmazingHand?style=social)

MIT License

</div>

---

<div align="center">

---

**[⬆️ Back to Top](#amazinghand-hackathon-demo)** |
**[📖 View Documentation](./docs/)** |
**[🐛 Report Issues](https://github.com/tianrking/AmazingHand/issues)** |
**[💡 Suggest Features](https://github.com/tianrking/AmazingHand/discussions)** |

## 🔗 Official Project Link

**[🏠 AmazingHand Official Project](https://github.com/pollen-robotics/AmazingHand/)** |

</div>