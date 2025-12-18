# AmazingHand Hackathon Demo

<div align="center">

<a href="https://www.seeedstudio.com/Amazing-Hand-Right-Hand-The-Open-Source-Robotic-Hand-Developer-Kit.html" target="_blank">
<img src="./buyone.png" alt="购买 AmazingHand" width="600"/>
</a>

### 🔥 [🛒 立即购买 AmazingHand 开发套件](https://www.seeedstudio.com/Amazing-Hand-Right-Hand-The-Open-Source-Robotic-Hand-Developer-Kit.html) 🔥

![AmazingHand Logo](https://img.shields.io/badge/AmazingHand-Hackathon%20Demo-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

## 🌐 语言 / Language / Idioma
**[🇨🇳 中文](README.md)** | **[🇺🇸 English](README_EN.md)** | **[🇪🇸 Español](README_ES.md)**

## 🤖 项目概述

这是 AmazingHand 机械手项目的黑客松演示案例集合，包含多个完整的控制方案示例。

</div>

## 📸 项目展示

### Case 1: 手势控制与点位重放
<table>
<tr>
<td><img src="./case1/case_1_1.png" alt="手势控制界面" width="400"/></td>
<td><img src="./case1/case_1_2.png" alt="点位重放上位机" width="400"/></td>
</tr>
<tr>
<td align="center">Web手势控制界面</td>
<td align="center">点位重放上位机</td>
</tr>
</table>

### Case 2: 舵机监控与示教
<table>
<tr>
<td><img src="./case2/case_2_1.png" alt="舵机监控界面" width="600"/></td>
</tr>
<tr>
<td align="center">舵机实时监控界面</td>
</tr>
</table>

### Case 3: 全自由度动态控制
<table>
<tr>
<td><img src="./case3/case_3_1.png" alt="全自由度控制界面" width="600"/></td>
</tr>
<tr>
<td align="center">Web精确控制界面</td>
</tr>
</table>

### Case 4: MuJoCo 仿真控制
<table>
<tr>
<td><img src="./case4/case_4_1.png" alt="MuJoCo仿真" width="400"/></td>
<td><img src="./case4/case_4_2.png" alt="单手控制" width="400"/></td>
<td><img src="./case4/case_4_3.png" alt="双手控制" width="400"/></td>
</tr>
<tr>
<td align="center">MuJoCo物理仿真</td>
<td align="center">单手Web控制</td>
<td align="center">双手协同控制</td>
</tr>
</table>

### Case 5: ESP32-C3嵌入式控制
<table>
<tr>
<td><img src="./case5/case_5_1.png" alt="ESP32硬件" width="400"/></td>
<td><img src="./case5/case_5_2.png" alt="WiFi控制界面" width="400"/></td>
<td><img src="./case5/case_5_3.png" alt="移动端控制" width="400"/></td>
<td><img src="./case5/case_5_4.png" alt="独立运行" width="400"/></td>
</tr>
<tr>
<td align="center">ESP32-C3硬件</td>
<td align="center">WiFi Web控制</td>
<td align="center">移动端适配</td>
<td align="center">独立便携运行</td>
</tr>
</table>

## 📋 案例列表

| 案例 | 名称 | 说明 | 技术栈 |
|------|------|------|--------|
| [**case1**](./case1/) | 🖐️ 手势控制与点位重放 | WebSocket + Web手势识别 + PySide6重放 | rustypot, MediaPipe, WebSocket |
| [**case2**](./case2/) | 📊 舵机监控与示教 | 飞特SDK + 实时监控 + 点位记录 | FTServo SDK, PySide6 |
| [**case3**](./case3/) | 🎯 全自由度动态控制 | WebSocket + 精确控制 + 动态演示 | rustypot, WebSocket |
| [**case4**](./case4/) | 🧮 MuJoCo 仿真控制 | 物理仿真 + Web控制 + 3D可视化 | MuJoCo, FastAPI, HTML5 |
| [**case5**](./case5/) | 📡 ESP32-C3嵌入式控制 | 微控制器 + WiFi控制 + 独立运行 | ESP32-C3, Arduino, WiFi |

## 🚀 快速开始

### 📌 Case 1: 手势控制方案

```bash
cd case1

# 1. 启动WebSocket服务端
python websocket_server.py

# 2. 打开Web控制界面
# 用浏览器打开 gesture_control.html

# 3. (可选) 使用上位机重放点位
python playback_gui.py
```

> 💡 **适用场景**：需要手势识别、远程Web控制、动作录制重放

---

### 📌 Case 2: 舵机监控方案

```bash
cd case2

# 启动监控上位机
python servo_monitor.py
```

> 💡 **适用场景**：舵机调试、手动示教、状态监控

---

### 📌 Case 3: 全自由度动态控制方案

```bash
cd case3

# 启动服务端
python fulldof_server.py

# 打开控制界面
# 用浏览器打开 fulldof_control.html
```

> 💡 **适用场景**：精确控制、动态演示、手势研究

---

### 📌 Case 4: MuJoCo 仿真控制方案

```bash
cd case4

# 单手仿真
python simulation_server.py

# 双手仿真（可选）
python dual_hand_simulation.py --mode both

# 打开控制界面
# 用浏览器打开 single_hand_control.html 或 dual_hand_control.html
```

> 💡 **适用场景**：算法验证、教育演示、无需硬件的原型开发

---

### 📌 Case 5: ESP32-C3 嵌入式控制方案

```bash
cd case5

# Arduino IDE 方式
# 打开 esp32_controller.ino
# 选择开发板：XIAO ESP32-C3
# 编译并上传

# PlatformIO 方式（推荐）
pio run --target upload
pio device monitor

# WiFi 控制
# 上传 src/esp32_main.cpp 后
# 连接 WiFi 热点 "AmazingHand"
# 访问 http://192.168.4.1
```

> 💡 **适用场景**：独立演示、便携控制、嵌入式应用

---

### 📌 Tools: 辅助工具集

```bash
cd tools

# 舵机归中工具（支持16个舵机）
python servo_center.py

# 简易归中工具
python simple_center.py
```

> 💡 **适用场景**：机械手初始化、舵机校准、基础调试

## ⚙️ 硬件支持

| 案例 | 硬件需求 | 说明 |
|------|----------|------|
| Case 1-3 | ✅ AmazingHand 机械手 | 8个舵机 (ID 11-18)，4根手指，每根手指2个舵机（弯曲 + 偏摆） |
| Case 4 | ❌ 无需硬件 | 纯软件仿真 |
| Case 5 | ✅ ESP32-C3 | 微控制器硬件，支持WiFi控制 |

### 🦾 机械手规格
- **舵机数量**: 8个 (ID 11-18)
- **手指配置**: 4根手指（大拇指、食指、中指、无名指）
- **自由度**: 每根手指2个自由度（弯曲 + 偏摆）

## 📊 技术对比

| 特性 | Case 1 | Case 2 | Case 3 | Case 4 | Case 5 |
|------|--------|--------|--------|--------|--------|
| **舵机SDK** | rustypot | FTServo (飞特) | rustypot | 无（纯仿真） | SCServo |
| **控制方式** | 🌐 WebSocket远程 | 🔌 本地串口 | 🌐 WebSocket远程 | 📡 HTTP API | 📶 嵌入式控制 |
| **用户界面** | 🌐 Web + 💻 PySide6 | 💻 PySide6 | 🌐 Web | 🌐 Web | 📶 WiFi Web |
| **手势识别** | ✅ (MediaPipe) | ❌ | ❌ | ❌ | ❌ |
| **实时监控** | ⚡ 简单 | 📊 详细 | ⚡ 实时 | ⚡ 实时 | ⚡ 实时 |
| **精确控制** | ✅ | ✅ | ✅ 全支持 | ✅ | ✅ |
| **动态演示** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **物理仿真** | ❌ | ❌ | ❌ | ✅ (MuJoCo) | ❌ |
| **硬件需求** | 🔧 需要 | 🔧 需要 | 🔧 需要 | 💻 不需要 | 🔧 需要（ESP32） |
| **独立运行** | ❌ | ❌ | ❌ | ❌ | ✅ |

## 📁 目录结构

```bash
hackathon_demo/
├── 📄 README.md                    # 本文档
├── 📂 case1/                       # 🖐️ 手势控制方案
│   ├── 📄 README.md
│   ├── 🐍 websocket_server.py      # WebSocket服务器
│   ├── 🌐 gesture_control.html     # Web手势控制界面
│   ├── 💻 playback_gui.py          # 点位重放上位机
│   └── 📸 case_1_1.png, case_1_2.png # 界面截图
├── 📂 case2/                       # 📊 舵机监控方案
│   ├── 📄 README.md
│   ├── 🐍 servo_monitor.py         # 舵机监控上位机
│   ├── 📂 FTServo_Python/          # 飞特舵机SDK
│   └── 📸 case_2_1.png             # 界面截图
├── 📂 case3/                       # 🎯 全自由度控制方案
│   ├── 📄 README.md
│   ├── 🐍 fulldof_server.py        # 全自由度服务器
│   ├── 🌐 fulldof_control.html     # 精确控制界面
│   └── 📸 case_3_1.png             # 界面截图
├── 📂 case4/                       # 🧮 MuJoCo仿真方案
│   ├── 📄 README.md
│   ├── 🐍 simulation_server.py     # 单手仿真服务器
│   ├── 🐍 dual_hand_simulation.py  # 双手仿真服务器
│   ├── 🌐 single_hand_control.html # 单手控制界面
│   ├── 🌐 single_hand_control_en.html # 单手控制界面(英文)
│   ├── 🌐 dual_hand_control.html   # 双手控制界面
│   ├── 📂 AHSimulation/            # 仿真模型
│   │   ├── 📂 AH_Right/           # 右手模型
│   │   └── 📂 AH_Left/            # 左手模型
│   ├── 📄 dual_hand_model.xml     # 双手模型文件
│   └── 📸 case_4_1.png, case_4_2.png, case_4_3.png # 界面截图
├── 📂 case5/                       # 📡 ESP32-C3嵌入式方案
│   ├── 📄 README.md                # 详细说明
│   ├── 📄 esp32_controller.ino     # Arduino主程序
│   ├── 📄 servo_scanner.ino        # 舵机扫描工具
│   ├── 📂 src/esp32_main.cpp       # PlatformIO主程序
│   ├── 📄 platformio.ini           # PlatformIO配置
│   ├── 📂 lib/                     # 依赖库
│   ├── 📄 WIFI_SETUP_GUIDE.md      # WiFi设置指南
│   ├── 📄 FINGER_CONTROL_GUIDE.md  # 控制指南
│   └── 📸 case_5_1.png ~ case_5_4.png # 硬件和界面截图
└── 📂 tools/                       # 🔧 辅助工具集
    ├── 📄 README.md                # 工具使用说明
    ├── 🐍 servo_center.py          # 舵机归中工具
    └── 🐍 simple_center.py         # 简易归中工具
```

## 🛠️ 依赖安装

### 📦 通用依赖
```bash
pip install pyside6 numpy pyserial
```

### 📦 Case 1 & 3 额外依赖
```bash
pip install websockets rustypot
```

### 📦 Case 2 无额外依赖
> (SDK已包含)

### 📦 Case 4 额外依赖
```bash
pip install mujoco fastapi uvicorn pydantic
```

### 📦 Case 5 开发环境
- Arduino IDE 或 PlatformIO
- SCServo 库

### 📦 Tools 额外依赖
```bash
pip install rustypot
```

## 🔗 相关链接

### 📚 关于 rustypot
[rustypot](https://github.com/pollen-robotics/rustypot) 是 Pollen Robotics 开发的 Python 舵机控制库，支持多种舵机协议，包括 SCS0009 系列。

### 📚 关于 MuJoCo
[MuJoCo](https://mujoco.readthedocs.io/) 是一个高性能的物理引擎，专为机器人仿真、游戏开发等领域设计。Case 4 使用 MuJoCo 提供精确的物理仿真环境。

## ⚠️ 注意事项

> 🔔 **重要提醒**：
>
> 1. **串口权限** (Linux)
>    ```bash
>    sudo chmod 666 /dev/ttyACM0
>    ```
>
> 2. **多个案例使用不同SDK**，不要同时运行
>
> 3. **Web界面需要摄像头权限**才能使用手势识别（仅 Case 1）
>
> 4. **Case 4 需要 OpenGL 支持**，确保系统支持 3D 渲染
>
> 5. **Case 5 需要ESP32-C3硬件**，支持WiFi控制功能

## 📜 License

<div align="center">

![License](https://img.shields.io/badge/License-MIT-green.svg)
![GitHub stars](https://img.shields.io/github/stars/tianrking/AmazingHand?style=social)
![GitHub forks](https://img.shields.io/github/forks/tianrking/AmazingHand?style=social)

MIT License

</div>

<div align="center">

---

**[⬆️ 返回顶部](#amazinghand-hackathon-demo)** |
**[📖 查看文档](./docs/)** |
**[🐛 报告问题](https://github.com/tianrking/AmazingHand/issues)** |
**[💡 提出建议](https://github.com/tianrking/AmazingHand/discussions)**

Made with ❤️ by the AmazingHand Team

</div>