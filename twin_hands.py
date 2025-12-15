#!/usr/bin/env python3
"""
Amazing Hand Backend V13 - 终极修复版 (Final Fix)
功能：
1. 补全 site1/site2 等缺失的引用属性，彻底解决 equality constraint 报错
2. 保持对空格、括号等特殊命名字符的完美支持
3. 包含路径自适应、物理完整性等所有此前修复
"""

import threading
import uvicorn
import mujoco
import mujoco.viewer
import argparse
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ================= 配置 =================
PORT = 8000

# 路径自适应检测
CURRENT_DIR = Path(__file__).parent
path_candidate_1 = CURRENT_DIR / "AHSimulation" / "AHSimulation"
path_candidate_2 = CURRENT_DIR / "AHSimulation"

if (path_candidate_1 / "AH_Right").exists():
    ROOT_PATH = path_candidate_1
    print(f"📂 检测到双层目录结构: {ROOT_PATH}")
elif (path_candidate_2 / "AH_Right").exists():
    ROOT_PATH = path_candidate_2
    print(f"📂 检测到单层目录结构: {ROOT_PATH}")
else:
    print("❌ 严重错误: 找不到 AH_Right 文件夹！请确认 AHSimulation 目录位置。")
    ROOT_PATH = path_candidate_2 
# =======================================

parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="right", choices=["left", "right", "both"])
args = parser.parse_args()

MOTOR_COUNT = 16 if args.mode == "both" else 8

class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.targets = [0.0] * MOTOR_COUNT 

state = SharedState()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MotorData(BaseModel):
    values: List[float]

@app.get("/status")
def get_status():
    with state.lock:
        return {"mode": args.mode, "motor_count": MOTOR_COUNT, "targets": state.targets}

@app.post("/control")
def control_motors(data: MotorData):
    if len(data.values) != MOTOR_COUNT:
        return {"error": f"Need {MOTOR_COUNT} values"}
    safe_values = [max(min(x, 2.0), -2.0) for x in data.values]
    with state.lock:
        state.targets = safe_values
    return {"status": "ok"}

def run_server():
    print(f"📡 API 服务启动: {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="error")

# ================= 核心：XML 处理逻辑 =================

def expand_includes(file_path: Path) -> str:
    if not file_path.exists():
        print(f"⚠️ Warning: File not found {file_path}")
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    parent_dir = file_path.parent
    def replace_include(match):
        inc_file = match.group(1)
        inc_path = parent_dir / inc_file
        return expand_includes(inc_path)
    pattern = re.compile(r'<include\s+file=["\'](.*?)["\']\s*/>')
    expanded_content = pattern.sub(replace_include, content)
    expanded_content = re.sub(r'<\?xml.*?\?>', '', expanded_content)
    return expanded_content

def process_hand_xml(side: str, prefix: str):
    base_dir = ROOT_PATH / side / "mjcf"
    entry_xml = base_dir / "robot.xml"
    
    raw_xml_str = expand_includes(entry_xml)
    raw_xml_str = f"<root>{raw_xml_str}</root>"
    raw_xml_str = raw_xml_str.replace('<mujoco', '<group').replace('</mujoco>', '</group>')
    
    try:
        root = ET.fromstring(raw_xml_str)
    except ET.ParseError:
        print(f"❌ Critical XML Parse Error in {side}")
        return None

    extracted_data = {
        "asset": [], "default": [], "worldbody": [],
        "actuator": [], "sensor": [], "contact": [],
        "equality": [], "tendon": []
    }

    # === 关键修正：补全所有可能的引用属性 ===
    # site1, site2 是 equality constraint 常用的属性
    # geom1, geom2 是 contact/collision 常用的属性
    ref_attribs = [
        'mesh', 'material', 'texture', 'class', 'childclass', 
        'joint', 'parent', 'actuator', 
        'body1', 'body2', 
        'joint1', 'joint2', 
        'site', 'site1', 'site2',  # <--- 补全这里
        'geom', 'geom1', 'geom2',  # <--- 补全这里
        'tendon', 'tendon1', 'tendon2'
    ]
    
    for elem in root.iter():
        # A. 路径修正
        if 'file' in elem.attrib:
            original_file = elem.attrib['file']
            if not Path(original_file).is_absolute():
                candidate_1 = base_dir / original_file
                candidate_2 = base_dir / "assets" / Path(original_file).name
                final_path = candidate_1
                if candidate_1.exists(): final_path = candidate_1
                elif candidate_2.exists(): final_path = candidate_2
                elem.set('file', final_path.resolve().as_posix())

        # B. 强制命名
        if elem.tag in ['mesh', 'texture', 'skin']:
            if 'name' not in elem.attrib and 'file' in elem.attrib:
                stem = Path(elem.attrib['file']).stem
                elem.set('name', stem)

        # C. 定义加前缀
        if 'name' in elem.attrib:
            elem.set('name', f"{prefix}{elem.attrib['name']}")

        # D. 引用加前缀 (不切分字符串，保持整体性)
        for attr in ref_attribs:
            if attr in elem.attrib:
                val = elem.attrib[attr]
                if val:
                    elem.set(attr, f"{prefix}{val}")

    # 提取各个 Section
    for node in root.findall('.//asset'):
        extracted_data["asset"].extend(list(node))
        
    def extract_defaults_recursive(parent_element):
        extracted = []
        for child in parent_element:
            if child.tag == 'default':
                extracted.extend(list(child))
            elif child.tag == 'group': 
                extracted.extend(extract_defaults_recursive(child))
        return extracted
    extracted_data["default"] = extract_defaults_recursive(root)
        
    wb = root.find('.//worldbody')
    if wb is not None:
        extracted_data["worldbody"].extend(list(wb))
    else:
        for child in root:
            if child.tag == 'body':
                extracted_data["worldbody"].append(child)
            elif child.tag == 'group':
                 for sub in child:
                     if sub.tag == 'body':
                         extracted_data["worldbody"].append(sub)

    target_tags = ["actuator", "sensor", "contact", "equality", "tendon"]
    for tag in target_tags:
        nodes = []
        for group in root.findall(f'.//{tag}'):
             nodes.extend(list(group))
        extracted_data[tag] = nodes

    return extracted_data

def get_model_loader():
    if args.mode == "left":
        return mujoco.MjModel.from_xml_path(str(ROOT_PATH / "AH_Left/mjcf/scene.xml"))
    elif args.mode == "right":
        return mujoco.MjModel.from_xml_path(str(ROOT_PATH / "AH_Right/mjcf/scene.xml"))

    print("🛠️  构建双臂场景 V13 (Final Attribute Fix)...")

    new_root = ET.Element('mujoco', {'model': 'Dual_Hands_Scene'})
    ET.SubElement(new_root, 'compiler', {'angle': 'radian', 'meshdir': ROOT_PATH.as_posix(), 'balanceinertia': 'true'})
    ET.SubElement(new_root, 'option', {'timestep': '0.002', 'gravity': '0 0 -9.81', 'integrator': 'implicitfast', 'tolerance': '1e-8', 'noslip_iterations': '3'})

    visual = ET.SubElement(new_root, 'visual')
    ET.SubElement(visual, 'headlight', {'diffuse': '0.6 0.6 0.6', 'ambient': '0.3 0.3 0.3'})
    ET.SubElement(visual, 'rgba', {'haze': '0.15 0.25 0.35 1'})
    ET.SubElement(visual, 'global', {'azimuth': '120', 'elevation': '-20'})

    sections = {
        "asset": ET.SubElement(new_root, 'asset'),
        "default": ET.SubElement(new_root, 'default'),
        "worldbody": ET.SubElement(new_root, 'worldbody'),
        "actuator": ET.SubElement(new_root, 'actuator'),
        "sensor": ET.SubElement(new_root, 'sensor'),
        "contact": ET.SubElement(new_root, 'contact'),
        "equality": ET.SubElement(new_root, 'equality'),
        "tendon": ET.SubElement(new_root, 'tendon')
    }

    ET.SubElement(sections["asset"], 'texture', {'type': 'skybox', 'builtin': 'gradient', 'rgb1': '0.3 0.5 0.7', 'rgb2': '0 0 0', 'width': '512', 'height': '3072'})
    ET.SubElement(sections["asset"], 'texture', {'type': '2d', 'name': 'groundplane', 'builtin': 'checker', 'rgb1': '0.2 0.3 0.4', 'rgb2': '0.1 0.2 0.3', 'width': '300', 'height': '300'})
    ET.SubElement(sections["asset"], 'material', {'name': 'groundplane', 'texture': 'groundplane', 'texuniform': 'true', 'texrepeat': '5 5', 'reflectance': '0.2'})
    ET.SubElement(sections["worldbody"], 'light', {'pos': '0 0 1.5', 'dir': '0 0 -1', 'directional': 'true'})
    ET.SubElement(sections["worldbody"], 'geom', {'name': 'floor', 'size': '0 0 0.05', 'type': 'plane', 'material': 'groundplane'})

    print("Processing Left Hand...")
    l_data = process_hand_xml("AH_Left", prefix="L_")
    if l_data:
        sections["asset"].extend(l_data["asset"])
        l_master = ET.SubElement(sections["default"], 'default', {'class': 'L_Master'})
        l_master.extend(l_data["default"])
        sections["actuator"].extend(l_data["actuator"])
        sections["sensor"].extend(l_data["sensor"])
        sections["contact"].extend(l_data["contact"])
        sections["equality"].extend(l_data["equality"])
        sections["tendon"].extend(l_data["tendon"])
        l_mount = ET.SubElement(sections["worldbody"], 'body', {'name': 'mount_left', 'pos': '0 -0.2 0.1', 'childclass': 'L_Master'})
        l_mount.extend(l_data["worldbody"])

    print("Processing Right Hand...")
    r_data = process_hand_xml("AH_Right", prefix="R_")
    if r_data:
        sections["asset"].extend(r_data["asset"])
        r_master = ET.SubElement(sections["default"], 'default', {'class': 'R_Master'})
        r_master.extend(r_data["default"])
        sections["actuator"].extend(r_data["actuator"])
        sections["sensor"].extend(r_data["sensor"])
        sections["contact"].extend(r_data["contact"])
        sections["equality"].extend(r_data["equality"])
        sections["tendon"].extend(r_data["tendon"])
        r_mount = ET.SubElement(sections["worldbody"], 'body', {'name': 'mount_right', 'pos': '0 0.2 0.1', 'childclass': 'R_Master'})
        r_mount.extend(r_data["worldbody"])

    final_xml_str = ET.tostring(new_root, encoding='unicode')
    with open("final_dual_hand.xml", "w") as f:
        f.write(final_xml_str)
    
    try:
        model = mujoco.MjModel.from_xml_string(final_xml_str)
    except Exception as e:
        print(f"\n❌ XML生成成功，但 MuJoCo 加载失败。可能是约束冲突。")
        print(f"错误信息: {e}")
        exit(1)

    print(f"✅ 模型构建完成! Actuators: {model.nu}, Equality: {model.neq}")
    return model

class SimApp:
    def __init__(self):
        try:
            self.model = get_model_loader()
            self.data = mujoco.MjData(self.model)
            mujoco.mj_step(self.model, self.data)
        except Exception as e:
            print(f"\n❌ 仿真初始化失败: {e}")
            exit(1)
        
        self.api_thread = threading.Thread(target=run_server, daemon=True)
        self.api_thread.start()

    def run(self):
        print(f"\n🚀 仿真已启动 | 模式: {args.mode.upper()}")
        print(f"👉 API: http://localhost:{PORT}")
        
        with mujoco.viewer.launch_passive(self.model, self.data) as viewer:
            while viewer.is_running():
                step_start = time.time()
                with state.lock:
                    num_ctrl = self.model.nu
                    limit = min(len(state.targets), num_ctrl)
                    if limit > 0:
                        self.data.ctrl[:limit] = state.targets[:limit]

                mujoco.mj_step(self.model, self.data)
                viewer.sync()
                
                elapsed = time.time() - step_start
                if elapsed < 0.016:
                    time.sleep(0.016 - elapsed)

if __name__ == "__main__":
    app_sim = SimApp()
    app_sim.run()