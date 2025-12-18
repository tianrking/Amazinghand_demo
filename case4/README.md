# 🧮 Case 4: AmazingHand MuJoCo 仿真控制系统

<div align="center">

![MuJoCo Simulation](./case_4_1.png)

**基于 MuJoCo 物理引擎的高精度机械手仿真系统**

</div>

## 📋 项目简介

这是一个基于 MuJoCo 物理引擎的 AmazingHand 机械手仿真控制系统，支持单手和双手的实时仿真控制。

## ✨ 核心特性

1. **🔬 物理仿真** - 基于 MuJoCo 高精度物理引擎
2. **⚡ 实时控制** - FastAPI 提供 RESTful API 接口
3. **👁️ 可视化** - 实时 3D 仿真窗口显示
4. **🌐 Web 界面** - 简洁的 HTML 控制界面
5. **🤝 双手支持** - 支持左手、右手或双手同时仿真

## 🖼️ 功能展示

<table>
<tr>
<td><img src="./case_4_1.png" alt="MuJoCo物理仿真" width="400"/></td>
<td><img src="./case_4_2.png" alt="单手控制界面" width="400"/></td>
<td><img src="./case_4_3.png" alt="双手控制界面" width="400"/></td>
</tr>
<tr>
<td align="center">🔬 MuJoCo物理仿真窗口</td>
<td align="center">🎯 单手Web控制界面</td>
<td align="center">🤝 双手协同控制界面</td>
</tr>
</table>

## 文件说明

| 文件 | 说明 |
|------|------|
| `simulation_server.py` | 单手仿真服务器（基础版） |
| `dual_hand_simulation.py` | 双手仿真服务器（高级版） |
| `single_hand_control.html` | 单手控制界面（中文） |
| `single_hand_control_en.html` | 单手控制界面（英文） |
| `dual_hand_control.html` | 双手控制界面 |
| `dual_hand_model.xml` | 双手 MuJoCo 模型文件 |
| `AHSimulation/` | 仿真模型目录 |
|   ├─ `AH_Right/` | 右手模型 |
|   └─ `AH_Left/` | 左手模型 |

## 硬件要求

- 无需硬件（纯仿真）
- 支持 OpenGL 的显卡（用于 3D 渲染）

## 软件依赖

```bash
# 安装 Python 依赖
pip install mujoco fastapi uvicorn pydantic numpy

# 或使用 uv
uv add mujoco fastapi uvicorn pydantic numpy
```

## 使用流程

### 单手仿真

#### Step 1: 启动单手仿真服务器

```bash
python simulation_server.py
```

服务器启动后会：
- 在端口 8000 启动 FastAPI 服务
- 打开 MuJoCo 3D 仿真窗口
- 加载右手模型

#### Step 2: 打开控制界面

用浏览器打开 `single_hand_control.html`

#### Step 3: 控制机械手

- 使用滑块调整 8 个关节的角度
- 实时查看仿真窗口中的机械手响应
- 点击"重置"按钮恢复初始姿态

### 双手仿真

#### Step 1: 启动双手仿真服务器

```bash
# 右手仿真
python dual_hand_simulation.py --mode right

# 左手仿真
python dual_hand_simulation.py --mode left

# 双手同时仿真
python dual_hand_simulation.py --mode both
```

#### Step 2: 打开双手控制界面

用浏览器打开 `dual_hand_control.html`

#### Step 3: 控制双手

- 左右分栏分别控制左右手
- 支持 16 个关节独立控制
- 实时物理仿真显示

## API 接口

### GET /status
获取当前关节状态

**响应示例：**
```json
{
  "status": "running",
  "joint_positions": [0.1, 0.2, ...],
  "motor_count": 8
}
```

### POST /control
控制关节角度

**请求体：**
```json
{
  "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
}
```

## 技术架构

```
┌─────────────────────────────────────────────────────┐
│                   Web Browser                        │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │  Control UI     │  │  3D Viewer      │          │
│  │  (HTML/JS)      │  │  (MuJoCo)       │          │
│  └─────────────────┘  └─────────────────┘          │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────┐
│              FastAPI Server                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  API Routes │  │  CORS Mw    │  │  State Mgmt │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│              MuJoCo Physics                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Simulation │  │  Dynamics   │  │  Rendering  │ │
│  │  Loop       │  │  Solver     │  │  Engine     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 模型结构

### 关节配置（单手）
- 8 个可控关节
- 每个关节角度范围：[-π, π]
- 支持位置控制和速度控制

### 模型文件
- `scene.xml` - 主场景定义
- `robot.xml` - 机器人模型
- `assets/` - 模型资源文件（ meshes、textures 等）

## 使用场景

- **算法验证** - 在仿真中测试控制算法
- **教育演示** - 直观展示机械手原理
- **快速原型** - 无需硬件即可开发
- **批量测试** - 自动化测试控制方案

## 故障排除

### 错误：找不到模型文件
确保 `AHSimulation/AH_Right/mjcf/scene.xml` 路径正确

### 错误：端口被占用
修改 Python 文件中的 `PORT` 变量

### 错误：OpenGL 不可用
- Linux: 安装 `mesa-utils`
- Windows: 更新显卡驱动
- macOS: 确保 OpenGL 支持

### 错误：MuJoCo 许可证
本项目使用 MuJoCo 免费版本，满足学习和研究用途

## 高级功能

### 自定义控制器
可以通过继承 `SharedState` 类实现自定义控制逻辑

### 数据记录
仿真数据可保存为 JSON 格式用于后续分析

### 批量仿真
支持脚本化批量运行仿真实验

## License

MIT License

## 参考

- [MuJoCo 官方文档](https://mujoco.readthedocs.io/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [AHSimulation 原项目](https://github.com/tianrking/AHSimulation)