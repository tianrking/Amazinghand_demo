# XIAO ESP32-C3 灵巧手控制项目

## 📋 项目简介

基于 Seeed XIAO ESP32-C3 开发的5指灵巧手控制系统，支持多电机协同控制，实现握拳、张开、摆动等复杂手势动作。

## 🎯 主要特性

- **完整五指控制**: 支持8个电机（11-18 ID）控制5根手指
- **智能手势系统**: 预设握拳、张开、挥手、单指动作
- **精准位置控制**: 10位精度（0-1023范围）
- **双电机协同**: 每根手指由两个电机协同控制弯曲和摆动
- **安全限位保护**: 自动限制电机运动范围防止损坏

## 🔧 硬件配置

### 主控板
- **开发板**: Seeed XIAO ESP32-C3
- **处理器**: RISC-V 单核 160MHz
- **内存**: 320KB RAM + 4MB Flash

### 舵机配置
- **通信协议**: SCServo 串行舵机
- **波特率**: 1,000,000 bps
- **位置精度**: 0-1023 (10位)
- **控制引脚**:
  - TX: D4 (GPIO4)
  - RX: D5 (GPIO3)

### 电机分配
| 手指 | 左电机ID | 右电机ID | 功能说明 |
|------|----------|----------|----------|
| 大拇指 | 11 | 12 | 特殊逻辑控制 |
| 食指 | 13 | 14 | 标准手指逻辑 |
| 中指 | 15 | 16 | 标准手指逻辑 |
| 无名指 | 17 | 18 | 基准验证手指 |
| 小指 | 预留 | 预留 | 扩展功能 |

## 📝 软件架构

### 核心控制函数

#### `setFinger(id_left, id_right, bend, yaw, isThumb)`
通用手指控制函数，支持：
- **弯曲控制** (bend): 20.0(张开) ~ 160.0(握拳)
- **摆动控制** (yaw): -100.0(左) ~ 100.0(右)
- **特殊逻辑**: 大拇指使用反转逻辑

#### `setFullHand(bend, yaw)`
整只手协同控制函数，同时控制所有手指执行统一动作。

### 控制逻辑

**普通手指逻辑**（食指、中指、无名指、小指）：
```cpp
posLeft  = CENTER_POS + offsetBend + offsetYaw;
posRight = CENTER_POS - offsetBend + offsetYaw;
```

**大拇指逻辑**（反向控制）：
```cpp
posLeft  = CENTER_POS - offsetBend + offsetYaw;
posRight = CENTER_POS + offsetBend + offsetYaw;
```

## 🚀 预设动作

### 1. 基础动作
- **握拳**: `setFullHand(160.0, 0.0)`
- **张开**: `setFullHand(20.0, 0.0)`

### 2. 摆动动作
- **左摆**: `setFullHand(90.0, -100.0)`
- **右摆**: `setFullHand(90.0, 100.0)`

### 3. 精细动作
- **食指弯曲**: `setFinger(13, 14, 160.0, 0.0, false)`
- **食指伸直**: `setFinger(13, 14, 20.0, 0.0, false)`

## 🛠️ 开发环境

### 依赖库
- **SCServo**: 舵机控制库


## 📚 使用说明

### 1. 硬件连接
```
XIAO ESP32-C3    →    舵机控制器
D4 (GPIO4)      →    TX
D5 (GPIO3)      →    RX
GND             →    GND
5V              →    VCC (如果需要)
```

### 2. 编译上传
```bash
# 安装 PlatformIO
pip install platformio

# 编译项目
pio run

# 上传固件
pio run --target upload

# 监控串口
pio device monitor
```

### 3. 自定义动作
```cpp
// 自定义新动作
void customAction() {
  // 半握拳 + 左摆
  setFullHand(100.0, -50.0);
  delay(2000);

  // 只弯曲中指和食指
  setFinger(13, 14, 120.0, 0.0, false);  // 食指
  setFinger(15, 16, 120.0, 0.0, false);  // 中指
  delay(2000);
}
```

## 🔍 调试信息

项目包含详细的串口调试输出：
```
==========================
AmazingHand Full Control
Range: 0-1023
==========================
Init: OPEN HAND
>>> FIST (160)
>>> OPEN (20)
>>> WAVE LEFT
>>> WAVE RIGHT
>>> Index Finger Demo
```

## ⚙️ 参数调优

### 关键参数
```cpp
const int CENTER_POS = 512;        // 中心位置
const float BEND_STRENGTH = 200.0; // 弯曲幅度
const float YAW_STRENGTH = 100.0;  // 摆动幅度
```

### 动作范围
- **弯曲**: 20.0 (完全张开) ~ 160.0 (完全握拳)
- **摆动**: -100.0 (最左) ~ 100.0 (最右)
- **位置**: 100 ~ 900 (安全范围限制)


**注意**: 本项目需要配合相应硬件使用，请确保硬件连接正确后再上电测试。