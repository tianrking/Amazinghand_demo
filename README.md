# Amazing Hand 仿真控制 - 简化版

这是一个简单易用的 Amazing Hand 机械手仿真前后端项目。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install mujoco fastapi uvicorn pydantic numpy

# 或者使用 uv
uv add mujoco fastapi uvicorn pydantic numpy
```

### 2. 运行仿真

```bash
# 在当前目录运行
python fastapi_hand.py
```

### 3. 打开浏览器

在浏览器中打开 `fastapi_hand.html` 文件，即可看到仿真界面和控制面板。

## 📁 项目结构

```
Demo/
├── fastapi_hand.py          # 后端 API 服务器 + MuJoCo 仿真
├── fastapi_hand.html        # 前端控制界面
├── README.md               # 说明文档
└── AHSimulation/
    ├── AH_Right/           # 右手模型
    │   └── mjcf/
    │       ├── scene.xml
    │       └── assets/
    └── AH_Left/            # 左手模型
        └── mjcf/
            ├── scene.xml
            └── assets/
```

## 🎮 使用方法

1. **启动后端**：运行 `python fastapi_hand.py`
   - 会在端口 8000 启动 FastAPI 服务器
   - 打开 MuJoCo 仿真窗口

2. **打开前端**：双击 `fastapi_hand.html` 在浏览器中打开

3. **控制机械手**：
   - 使用滑块调整 8 个关节的角度
   - 实时查看仿真窗口中的机械手响应
   - 点击"重置"按钮恢复初始姿态

## 🔌 API 接口

### GET /status
获取当前电机状态

### POST /control
控制电机角度
```json
{
  "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
}
```

## 🛠️ 技术栈

- **后端**：Python + MuJoCo + FastAPI
- **前端**：HTML + JavaScript
- **仿真**：MuJoCo 物理引擎
- **通信**：HTTP REST API

## 📝 说明

这是一个简化版本，移除了复杂的 IK 求解和手势跟踪功能，专注于：
- 简单的关节角度控制
- 实时仿真显示
- Web 界面控制

适合学习 MuJoCo 仿真和 Web API 集成。

## 🔧 故障排除

### 错误：找不到模型文件
确保 `AHSimulation/AH_Right/mjcf/scene.xml` 路径正确

### 错误：端口被占用
修改 `fastapi_hand.py` 中的 `PORT` 变量

