# AmazingHand 控制Demo

## 安装辅助工具

**文件**: `cus_tomiddle.py`

**功能**: 安装时将所有舵机归中位（0度位置）

**用途**: 机械手安装或调试时，让所有舵机回到中间位置，便于校准和装配

**运行**:
```bash
python cus_tomiddle.py
```
程序会每3秒发送一次归中指令，按Ctrl+C退出

---

## 第一组Demo：全自由度机械手控制

**文件**: `amazinghand_server_fulldof.py` + `amazinghand_server_fulldof.html`

**功能**: 8自由度独立控制 + 预设手势 + 动态演示

**运行**:
```bash
# 终端1: 启动后端
python amazinghand_server_fulldof.py

# 终端2: 启动HTTP服务器
python -m http.server 8000

# 浏览器打开
http://localhost:8000/amazinghand_server_fulldof.html
```

## 第二组Demo：集成调试版本

**文件**: `all_in_one_debug.py` + `all_in_one.html` 或 `all_in_one_i18n.html`

**功能**: 集成调试功能（包含视觉识别等扩展功能）

**运行**:
```bash
# 终端1: 启动后端
python all_in_one_debug.py

# 终端2: 启动HTTP服务器
python -m http.server 8000

# 浏览器打开（选择其一）
http://localhost:8000/all_in_one.html      # 英文版
http://localhost:8000/all_in_one_i18n.html # 多语言版
```

## 硬件配置

- **舵机ID**: 11-18（Thumb: 11-12, Index: 13-14, Middle: 15-16, Ring: 17-18）
- **串口**: `/dev/ttyACM0`
- **WebSocket**: `ws://localhost:8765`

## 注意事项

1. 先启动Python后端，再打开前端界面
2. 修改舵机ID：编辑对应`.py`文件中的`FINGERS`配置
3. 关闭顺序：先关浏览器，再按Ctrl+C停止后端

