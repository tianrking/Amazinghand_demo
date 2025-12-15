#!/usr/bin/env python3
"""
Amazing Hand Backend - FastAPI with CORS
功能：MuJoCo 仿真核心 + HTTP API 服务器
"""

import threading
import uvicorn
import numpy as np
import mujoco
import mujoco.viewer
from pathlib import Path
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ================= 配置 =================
PORT = 8000
ROOT_PATH = Path(__file__).parent / "AHSimulation"
# =======================================

# 1. 全局状态 (用于线程间通信)
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.targets = [0.0] * 8  # 8个电机的控制目标
        self.joint_pos = [0.0] * 8 # (可选) 读取当前关节角度回传给前端

state = SharedState()

# 2. FastAPI 定义
app = FastAPI()

# --- 关键：允许跨域 (CORS) ---
# 这样你的 html 文件直接打开也能访问 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MotorData(BaseModel):
    values: List[float]

@app.get("/status")
def get_status():
    """前端轮询此接口，获取当前状态"""
    import time
    with state.lock:
        return {
            "targets": state.targets,
            "sim_time": time.time()
        }

@app.post("/control")
def control_motors(data: MotorData):
    """前端发送控制指令"""
    if len(data.values) != 8:
        return {"error": "Need 8 values"}

    # 简单的安全限制
    safe_values = [max(min(x, 1.57), -1.57) for x in data.values]

    with state.lock:
        state.targets = safe_values
    return {"status": "ok", "set_to": safe_values}

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="error")

# 3. 仿真主程序
class SimApp:
    def __init__(self):
        print(f"Loading model from: {ROOT_PATH}/AH_Right/mjcf/scene.xml")
        self.model = mujoco.MjModel.from_xml_path(f"{ROOT_PATH}/AH_Right/mjcf/scene.xml")
        self.data = mujoco.MjData(self.model)

        # 启动 API 线程
        self.api_thread = threading.Thread(target=run_server, daemon=True)
        self.api_thread.start()

    def run(self):
        print(f"\n🚀 后端服务已启动! 端口: {PORT}")
        print("等待前端连接...\n")

        with mujoco.viewer.launch_passive(self.model, self.data) as viewer:
            import time
            while viewer.is_running():
                step_start = time.time()

                # --- 核心逻辑：读取 API 数据 -> 写入 仿真 ---
                with state.lock:
                    self.data.ctrl[:] = state.targets

                # 物理步进
                mujoco.mj_step(self.model, self.data)
                viewer.sync()

                # 简单的频率控制 (60Hz)
                elapsed = time.time() - step_start
                if elapsed < 0.016:
                    time.sleep(0.016 - elapsed)

if __name__ == "__main__":
    import time
    app_sim = SimApp()
    app_sim.run()
