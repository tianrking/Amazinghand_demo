import asyncio
import websockets
import json
import pyaudio
import base64
import os
import sys

# ================= 配置区域 =================
# ⚠️ 必须以 sk- 开头，不要带中文
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx" 

# 机械手服务端地址 (你的 amazinghand_server_fused.py 监听的地址)
HAND_SERVER_URL = "ws://localhost:8765"

# 音频配置 (OpenAI Realtime 推荐格式)
CHANNELS = 1
RATE = 24000
CHUNK = 2400  # 每次发送 0.1秒 的音频
FORMAT = pyaudio.paInt16

# 硬件映射参数 (必须与机械手代码一致)
HW_MIN, HW_MAX = 20, 160
YAW_MIN, YAW_MAX = -100, 100
# ===========================================

# 本地状态记忆 (防止动一个手指其他复位)
local_state = {
    "thumb": 0.0, "index": 0.0, "middle": 0.0, "ring": 0.0,
    "thumb_yaw": 0.0, "index_yaw": 0.0, "middle_yaw": 0.0, "ring_yaw": 0.0
}

def map_value(val_01, out_min, out_max):
    """将 0.0-1.0 映射到 硬件数值"""
    clamped = max(0.0, min(1.0, float(val_01)))
    return int(clamped * (out_max - out_min) + out_min)

def map_yaw(val_11, out_min, out_max):
    """将 -1.0-1.0 映射到 硬件数值"""
    clamped = max(-1.0, min(1.0, float(val_11)))
    # 归一化到 0-1
    normalized = (clamped + 1) / 2
    return int(normalized * (out_max - out_min) + out_min)

async def send_to_hand(ws_hand):
    """将当前 local_state 发送给机械手"""
    payload = {
        "thumb": map_value(local_state["thumb"], HW_MIN, HW_MAX),
        "index": map_value(local_state["index"], HW_MIN, HW_MAX),
        "middle": map_value(local_state["middle"], HW_MIN, HW_MAX),
        "ring": map_value(local_state["ring"], HW_MIN, HW_MAX),
        "thumb_yaw": map_yaw(local_state["thumb_yaw"], YAW_MIN, YAW_MAX),
        "index_yaw": map_yaw(local_state["index_yaw"], YAW_MIN, YAW_MAX),
        "middle_yaw": map_yaw(local_state["middle_yaw"], YAW_MIN, YAW_MAX),
        "ring_yaw": map_yaw(local_state["ring_yaw"], YAW_MIN, YAW_MAX),
    }
    if ws_hand and ws_hand.open:
        await ws_hand.send(json.dumps(payload))
        # print(f"🖐️ 发送硬件指令: {payload}")

async def audio_stream_task(ws_openai):
    """从麦克风读取音频并发送给 OpenAI"""
    p = pyaudio.PyAudio()
    
    # 获取默认输入设备 (请确保 AudioRelay 是默认输入)
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"❌ 麦克风打开失败: {e}")
        print("请检查电脑的声音设置 -> 输入设备 是否选了 AudioRelay")
        return

    print("🎙️ 正在录音... (请对着手机说话)")
    
    try:
        while True:
            # 读取原始 PCM 数据
            data = stream.read(CHUNK, exception_on_overflow=False)
            # 转 Base64
            base64_audio = base64.b64encode(data).decode("utf-8")
            
            # 发送给 OpenAI
            event = {
                "type": "input_audio_buffer.append",
                "audio": base64_audio
            }
            await ws_openai.send(json.dumps(event))
            await asyncio.sleep(0.01) # 让出一点 CPU
    except asyncio.CancelledError:
        print("停止录音")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

async def main():
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    print(f"🔌 正在连接机械手: {HAND_SERVER_URL}")
    try:
        ws_hand = await websockets.connect(HAND_SERVER_URL)
        print("✅ 机械手连接成功")
    except Exception as e:
        print(f"❌ 无法连接机械手: {e}")
        return

    print("☁️ 正在连接 OpenAI Realtime API...")
    try:
        async with websockets.connect(url, extra_headers=headers) as ws_openai:
            print("✅ OpenAI 连接成功！对话开始。")

            # 1. 初始化会话 (定义工具)
            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "instructions": "你是机械手控制助手。接收用户的语音指令，控制手指弯曲。用户说'弯一点'时，请基于常识在当前状态上增加数值。Adjust parameters continuously.",
                    "voice": "verse",
                    "input_audio_format": "pcm16", # 对应 pyaudio paInt16
                    "output_audio_format": "pcm16",
                    "turn_detection": {
                        "type": "server_vad", # OpenAI 服务器自动检测你什么时候说完话
                    },
                    "tools": [{
                        "type": "function",
                        "name": "adjust_hand_posture",
                        "description": "Control hand fingers. 0.0=open, 1.0=closed.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "thumb": { "type": "number" }, "index": { "type": "number" },
                                "middle": { "type": "number" }, "ring": { "type": "number" },
                                "thumb_yaw": { "type": "number" }, "index_yaw": { "type": "number" }
                            }
                        }
                    }],
                    "tool_choice": "auto"
                }
            }
            await ws_openai.send(json.dumps(session_update))

            # 2. 启动录音任务 (后台运行)
            audio_task = asyncio.create_task(audio_stream_task(ws_openai))

            # 3. 主循环：接收 OpenAI 的回复
            async for message in ws_openai:
                event = json.loads(message)
                event_type = event.get("type")

                # 处理函数调用 (Core Logic)
                if event_type == "response.done":
                    output_items = event.get("response", {}).get("output", [])
                    for item in output_items:
                        if item.get("type") == "function_call" and item.get("name") == "adjust_hand_posture":
                            try:
                                args = json.loads(item["arguments"])
                                print(f"🤖 AI 指令: {args}")

                                # 更新本地状态
                                for k, v in args.items():
                                    if k in local_state:
                                        local_state[k] = v
                                
                                # 立即驱动机械手
                                await send_to_hand(ws_hand)

                                # 告诉 OpenAI 完成了 (构建回复链)
                                call_id = item["call_id"]
                                function_output_event = {
                                    "type": "conversation.item.create",
                                    "item": {
                                        "type": "function_call_output",
                                        "call_id": call_id,
                                        "output": json.stringify({"status": "moved"}) 
                                    }
                                }
                                await ws_openai.send(json.dumps(function_output_event))
                                await ws_openai.send(json.dumps({"type": "response.create"})) # 让AI可能会回复"好的"

                            except Exception as e:
                                print(f"解析参数错误: {e}")

                # 打印 AI 的错误信息 (方便调试)
                if event_type == "error":
                    print(f"❌ OpenAI 错误: {event.get('error', {}).get('message')}")

    except Exception as e:
        print(f"❌ 连接断开或错误: {e}")
    finally:
        if 'ws_hand' in locals(): await ws_hand.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")