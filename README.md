# AmazingHand Hackathon Demo

## 项目概述

这是 AmazingHand 机械手项目的黑客松演示案例集合，包含多个完整的控制方案示例。

## 案例列表

| 案例 | 名称 | 说明 | 技术栈 |
|------|------|------|--------|
| [case1](./case1/) | 手势控制与点位重放 | WebSocket + Web手势识别 + PySide6重放 | rustypot, MediaPipe, WebSocket |
| [case2](./case2/) | 舵机监控与示教 | 飞特SDK + 实时监控 + 点位记录 | FTServo SDK, PySide6 |
| [case3](./case3/) | 全自由度动态控制 | WebSocket + 精确控制 + 动态演示 | rustypot, WebSocket |

## 快速开始

### Case 1: 手势控制方案

```bash
cd case1

# 1. 启动WebSocket服务端
python websocket_server.py

# 2. 打开Web控制界面
# 用浏览器打开 gesture_control.html

# 3. (可选) 使用上位机重放点位
python playback_gui.py
```

**适用场景**：需要手势识别、远程Web控制、动作录制重放

### Case 2: 舵机监控方案

```bash
cd case2

# 启动监控上位机
python servo_monitor.py
```

**适用场景**：舵机调试、手动示教、状态监控

### Case 3: 全自由度动态控制方案

```bash
cd case3

# 启动服务端
python fulldof_server.py

# 打开控制界面
# 用浏览器打开 fulldof_control.html
```

**适用场景**：精确控制、动态演示、手势研究

### Tools: 辅助工具集

```bash
cd tools

# 舵机归中工具（支持16个舵机）
python servo_center.py

# 简易归中工具
python simple_center.py
```

**适用场景**：机械手初始化、舵机校准、基础调试

## 硬件支持

三个案例都支持 AmazingHand 机械手：
- 8个舵机 (ID 11-18)
- 4根手指（大拇指、食指、中指、无名指）
- 每根手指2个舵机（弯曲 + 偏摆）

## 技术对比

| 特性 | Case 1 | Case 2 | Case 3 |
|------|--------|--------|--------|
| 舵机SDK | rustypot | FTServo (飞特) | rustypot |
| 控制方式 | WebSocket远程 | 本地串口 | WebSocket远程 |
| 界面 | Web + PySide6 | PySide6 | Web |
| 手势识别 | 支持 (MediaPipe) | 不支持 | 不支持 |
| 实时监控 | 简单 | 详细 | 实时 |
| 精确控制 | 支持 | 支持 | 全支持 |
| 动态演示 | 支持 | 不支持 | 支持 |
| 扭矩控制 | 连接时自动启用 | 手动控制 | 连接时自动启用 |

## 目录结构

```
hackathon_demo/
├── README.md                    # 本文档
├── case1/                       # 手势控制方案
│   ├── README.md
│   ├── websocket_server.py      # WebSocket服务器
│   ├── gesture_control.html     # Web手势控制界面
│   └── playback_gui.py          # 点位重放上位机
├── case2/                       # 舵机监控方案
│   ├── README.md
│   ├── servo_monitor.py         # 舵机监控上位机
│   └── FTServo_Python/          # 飞特舵机SDK
├── case3/                       # 全自由度控制方案
│   ├── README.md
│   ├── fulldof_server.py        # 全自由度服务器
│   └── fulldof_control.html     # 精确控制界面
└── tools/                       # 辅助工具集
    ├── README.md                # 工具使用说明
    ├── servo_center.py          # 舵机归中工具
    └── simple_center.py         # 简易归中工具
```

## 依赖安装

```bash
# 通用依赖
pip install pyside6 numpy pyserial

# Case 1 额外依赖
pip install websockets rustypot

# Case 2 无额外依赖 (SDK已包含)

# Case 3 额外依赖
pip install websockets rustypot

# Tools 额外依赖
pip install rustypot

## 关于 rustypot

[rustypot](https://github.com/pollen-robotics/rustypot) 是 Pollen Robotics 开发的 Python 舵机控制库，支持多种舵机协议，包括 SCS0009 系列。

## 注意事项

1. **串口权限** (Linux)
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```

2. **多个案例使用不同SDK**，不要同时运行

3. **Web界面需要摄像头权限**才能使用手势识别

## License

MIT License
