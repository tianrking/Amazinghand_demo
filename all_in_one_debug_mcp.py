# 文件名: hand_mcp.py (或 all_in_one_debug_mcp.py)
from mcp.server.fastmcp import FastMCP
import asyncio
import websockets
import json

# 1. 创建 MCP 服务器
mcp = FastMCP("AmazingHand")

# 2. 配置底层连接
# 使用 127.0.0.1 比 localhost 更稳定，防止 IPv6 解析错误
HAND_SERVER_URL = "ws://127.0.0.1:8765"

# 硬件参数配置 (保持与底层驱动一致)
HW_MIN, HW_MAX = 20, 160     # 弯曲范围
YAW_MIN, YAW_MAX = -100, 100 # 侧摆范围

# --- 辅助函数 ---
def map_val(val, min_v, max_v):
    """映射 0.0-1.0 到电机角度"""
    # 如果是 None，默认为 0.0 (张开)
    if val is None: val = 0.0
    val = max(0.0, min(1.0, float(val)))
    return int(val * (max_v - min_v) + min_v)

def map_yaw(val, min_v, max_v):
    """映射 -1.0-1.0 到侧摆角度"""
    # 如果是 None，默认为 0.0 (居中)
    if val is None: val = 0.0
    val = max(-1.0, min(1.0, float(val)))
    return int(((val + 1) / 2) * (max_v - min_v) + min_v)

# --- 3. 定义工具 (核心部分) ---
# 这里的文档字符串是写给 AI 看的“说明书”，越详细，AI 越不容易出错。
@mcp.tool()
async def adjust_hand_posture(
    thumb: float = None, 
    index: float = None, 
    middle: float = None, 
    ring: float = None,
    thumb_yaw: float = None, 
    index_yaw: float = None
) -> str:
    """
    【必须调用此工具来控制机械手】。严禁在不调用此工具的情况下回复“动作已完成”。
    
    用于控制灵巧手的四个手指。
    数值范围：0.0 代表伸直/张开，1.0 代表弯曲/握紧。
    
    参数与手指的对应关系（请严格遵守）：
    - 大拇指 (Thumb)  -> 参数名: thumb
    - 食指   (Index)  -> 参数名: index
    - 中指   (Middle) -> 参数名: middle
    - 无名指 (Ring)   -> 参数名: ring
    
    Args:
        thumb: 大拇指弯曲度 (0.0=直, 1.0=弯)
        index: 食指弯曲度 (0.0=直, 1.0=弯)
        middle: 中指弯曲度 (0.0=直, 1.0=弯)
        ring: 无名指弯曲度 (0.0=直, 1.0=弯)。注意：ring 指的是无名指。
        thumb_yaw: 大拇指旋转 (-1.0=左, 1.0=右)
        index_yaw: 食指旋转 (-1.0=左, 1.0=右)
    """
    
    # 构造发给底层 Python 脚本的数据包
    # 我们将 None (AI没提到的手指) 默认映射为 0.0 (张开)，或者你可以根据需求修改逻辑
    payload = {
        "thumb": map_val(thumb, HW_MIN, HW_MAX),
        "index": map_val(index, HW_MIN, HW_MAX),
        "middle": map_val(middle, HW_MIN, HW_MAX),
        "ring": map_val(ring, HW_MIN, HW_MAX),
        "thumb_yaw": map_yaw(thumb_yaw, YAW_MIN, YAW_MAX),
        "index_yaw": map_yaw(index_yaw, YAW_MIN, YAW_MAX),
        # 补全其他默认值
        "middle_yaw": map_yaw(0, YAW_MIN, YAW_MAX),
        "ring_yaw": map_yaw(0, YAW_MIN, YAW_MAX),
    }

    print(f"📥 MCP 收到并转发请求: {payload}")

    try:
        # 建立连接 -> 发送 -> 等待确认 -> 关闭
        async with websockets.connect(HAND_SERVER_URL) as ws:
            # 1. 发送指令
            await ws.send(json.dumps(payload))
            
            # 2. 【关键修复】等待服务器回应 (ACK)
            # 这行代码能防止 "1000 OK" 错误，并确保动作已下发
            response = await ws.recv() 
            
            # 返回给 AI 的结果
            return f"成功: 机械手动作已执行。状态: {payload}"
            
    except ConnectionRefusedError:
        return f"❌ 失败: 无法连接到底层服务器 ({HAND_SERVER_URL})。请检查 amazinghand_server_fused.py 是否运行。"
    except Exception as e:
        return f"❌ 通信错误: {str(e)}"

if __name__ == "__main__":
    # 默认使用 stdio 模式，Claude 和 mcp run 都能用
    mcp.run()