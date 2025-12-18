# Case 5: ESP32-C3 嵌入式控制系统

## 项目简介

基于 Seeed XIAO ESP32-C3 微控制器的 AmazingHand 嵌入式控制系统，提供独立的硬件控制方案，支持 WiFi 远程控制。

## 核心特性

1. **嵌入式控制** - 基于 ESP32-C3 微控制器的独立控制方案
2. **WiFi 远程控制** - 支持网页端远程控制
3. **预设手势库** - 内置多种手势动作
4. **实时响应** - 低延迟的电机控制
5. **便携式设计** - 无需电脑，独立运行

## 文件说明

| 文件 | 说明 |
|------|------|
| `esp32_controller.ino` | Arduino 主程序（基础控制） |
| `servo_scanner.ino` | 舵机扫描工具（调试用） |
| `src/esp32_main.cpp` | PlatformIO 主程序（完整功能） |
| `platformio.ini` | PlatformIO 配置文件 |
| `lib/` | 依赖库目录 |
| `README_Basic.md` | 基础使用说明 |
| `WIFI_SETUP_GUIDE.md` | WiFi 设置指南 |
| `FINGER_CONTROL_GUIDE.md` | 手指控制详细说明 |
| `WORKSHOP_GUIDE.md` | 工作坊教学指南 |

## 硬件要求

- Seeed XIAO ESP32-C3 开发板
- SCServo 舵机（8个，ID 11-18）
- 舵机控制器或转接板
- USB-C 编程线

## 软件依赖

### Arduino IDE 方式
```bash
# 安装 SCServo 库
# 在 Arduino IDE 库管理器中搜索 "SCServo" 并安装
```

### PlatformIO 方式
```bash
# 安装 PlatformIO CLI
pip install platformio

# 编译上传
pio run --target upload
```

## 使用流程

### 方式一：Arduino IDE

#### Step 1: 准备环境
1. 安装 Arduino IDE
2. 安装 ESP32 开发板支持
3. 安装 SCServo 库

#### Step 2: 上传基础程序
```bash
# 打开 Arduino IDE
# 选择开发板：XIAO ESP32-C3
# 上传 esp32_controller.ino
```

#### Step 3: 测试控制
程序会自动执行预设动作序列：
1. 握拳
2. 张开
3. 左摆
4. 右摆
5. 单指动作演示

### 方式二：PlatformIO（推荐）

#### Step 1: 编译上传
```bash
# 编译项目
pio run

# 上传固件
pio run --target upload

# 监控串口
pio device monitor
```

#### Step 2: WiFi 控制模式
1. 上传 `src/esp32_main.cpp`（支持 WiFi）
2. 连接到 "AmazingHand" WiFi 热点
3. 密码：12345678
4. 访问 http://192.168.4.1
5. 使用网页控制界面

## 控制功能

### 预设手势
- **握拳** - 所有手指弯曲
- **张开** - 所有手指伸直
- **剪刀** - 食指和中指伸出
- **点赞** - 大拇指向上
- **指向** - 食指指向
- **OK** - 食指和大拇指组成圆圈

### 控制参数
- **位置范围**: 0-1023（10位精度）
- **弯曲角度**: 20°（张开）- 160°（握拳）
- **摆动角度**: -100°（左）- 100°（右）

## 代码结构

### 核心控制函数

```cpp
// 单指控制
setFinger(id_left, id_right, bend, yaw, isThumb)

// 整手控制
setFullHand(bend, yaw)
```

### 控制逻辑

**普通手指**（食指、中指、无名指）：
```cpp
posLeft  = CENTER_POS + offsetBend + offsetYaw;
posRight = CENTER_POS - offsetBend + offsetYaw;
```

**大拇指**（反向控制）：
```cpp
posLeft  = CENTER_POS - offsetBend + offsetYaw;
posRight = CENTER_POS + offsetBend + offsetYaw;
```

## 引脚配置

| 功能 | 引脚 | 说明 |
|------|------|------|
| TX | D4 (GPIO4) | 串行发送 |
| RX | D5 (GPIO3) | 串行接收 |
| LED | GPIO8 | 状态指示 |

## WiFi 控制界面

访问 http://192.168.4.1 后可以看到：

1. **预设动作按钮** - 一键执行各种手势
2. **实时控制滑块** - 精确控制每个手指
3. **状态监控** - 实时显示舵机状态
4. **游戏模式** - 石头剪刀布游戏

## 调试工具

### 舵机扫描器
使用 `servo_scanner.ino` 来：
- 检测连接的舵机ID
- 测试单个舵机响应
- 调整中心位置

### 串口调试
连接串口监控器（115200波特率）查看：
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
```

## 应用场景

- **独立演示** - 无需电脑的便携式展示
- **教学实验** - 嵌入式系统教学
- **产品原型** - 快速原型验证
- **比赛项目** - 机器人比赛控制

## 技术优势

1. **低功耗** - ESP32-C3 深度睡眠模式
2. **高集成度** - 单板完整控制方案
3. **WiFi 支持** - 无线远程控制
4. **实时性好** - 本地控制，无网络延迟
5. **易于部署** - 即插即用

## 故障排除

### 无法识别舵机
1. 检查串口连接（TX/RX）
2. 确认波特率设置为 1,000,000
3. 使用扫描工具检测舵机ID

### WiFi 连接失败
1. 检查热点是否创建成功
2. 确认密码：12345678
3. 尝试手动访问 192.168.4.1

### 舵机无响应
1. 检查电源供电是否足够
2. 确认舵机ID配置正确
3. 查看串口输出的错误信息

## 扩展开发

### 添加新动作
```cpp
void customAction() {
  // 自定义动作序列
  setFullHand(90.0, 0.0);    // 半握拳
  delay(1000);
  setFinger(13, 14, 160.0, 0.0, false);  // 食指弯曲
  delay(1000);
}
```

### 修改参数
```cpp
const int CENTER_POS = 512;        // 中心位置
const float BEND_STRENGTH = 200.0; // 弯曲强度
const float YAW_STRENGTH = 100.0;  // 摆动强度
```

## License

MIT License