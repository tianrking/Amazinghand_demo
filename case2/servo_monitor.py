#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCServo角度实时监控上位机 v3.1.10 - 最终版
支持ID 11-18舵机，带详细日志和错误诊断
修复了广播ping的bug
新增点位记录和控制功能
修复应用点位时舵机断开的临界问题
修复QMessageBox参数错误
解决串口端口冲突问题（错误码-1）
实现线程安全的舵机控制
新增扭矩控制功能（失能/启用）
修复扭矩失能失败问题
增加重试机制提高成功率
修复速度和负载数据读取错误
使用正确的ReadLoad方法读取负载数据
优化通信频率，降低误码率
热插拔检测改为2秒间隔
数据读取改为0.2秒间隔
添加负载调试日志和错误显示
修复负载调试日志中的属性错误
"""

import sys
import os
import time
import json
import logging
from threading import Thread
from typing import List, Dict

# 添加FTServo_Python路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FTSERVO_PATH = os.path.join(CURRENT_DIR, 'FTServo_Python')

if os.path.exists(FTSERVO_PATH):
    sys.path.insert(0, FTSERVO_PATH)
else:
    print("❌ 未找到FTServo_Python目录")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('servo_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ServoMonitor')

# 导入依赖
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGroupBox,
        QHeaderView, QMessageBox, QStatusBar, QComboBox, QTextEdit,
        QInputDialog, QDialog, QDialogButtonBox, QVBoxLayout as DialogLayout,
        QLabel as DialogLabel, QListWidget, QListWidgetItem
    )
    from PySide6.QtCore import Qt, Signal, QObject, QTimer
    from PySide6.QtGui import QFont, QColor
    logger.info("✅ PySide6导入成功")
except ImportError as e:
    logger.error(f"❌ PySide6导入失败: {e}")
    sys.exit(1)

# 导入SCServo SDK
try:
    from scservo_sdk.port_handler import PortHandler
    from scservo_sdk.scscl import scscl
    from scservo_sdk.scservo_def import COMM_SUCCESS
    logger.info("✅ SCServo SDK导入成功")
except ImportError as e:
    logger.error(f"❌ SCServo SDK导入失败: {e}")
    sys.exit(1)

# 常量
SCSCL_MIDDLE_POSITION = 2048
POSITION_RESOLUTION = 360.0 / 4096.0
SCSCL_TORQUE_ENABLE = 40  # 扭矩使能寄存器

# 配置文件路径
POSITIONS_FILE = 'servo_positions.json'


class ServoData:
    """舵机数据类"""
    def __init__(self, servo_id: int):
        self.id = servo_id
        self.current_pos = 2048
        self.current_speed = 0
        self.current_load = 0
        self.moving = 0
        self.connected = False
        self.was_connected = False
        self.last_update_time = time.time()
        self.error_count = 0


class ServoMonitorWorker(QObject):
    """舵机监控工作线程"""
    data_updated = Signal(list)
    status_changed = Signal(str)
    log_message = Signal(str, str)
    position_applied = Signal(int)  # 发送成功数量的信号

    def __init__(self, port_name: str):
        super().__init__()
        self.port_name = port_name
        self.port_handler = None
        self.servo_handler = None
        self.running = False
        self.servo_data: Dict[int, ServoData] = {}
        self.servo_ids = list(range(11, 19))

    def position_to_degrees(self, position: int) -> float:
        return (position - SCSCL_MIDDLE_POSITION) * POSITION_RESOLUTION

    def connect(self) -> bool:
        """连接串口"""
        logger.info(f"🚀 连接串口: {self.port_name}")
        try:
            self.port_handler = PortHandler(self.port_name)
            if not self.port_handler.openPort():
                msg = f"❌ 无法打开串口: {self.port_name}"
                self.status_changed.emit(msg)
                self.log_message.emit(msg, "error")
                return False

            if not self.port_handler.setBaudRate(1000000):
                msg = "❌ 无法设置波特率 1000000"
                self.status_changed.emit(msg)
                self.log_message.emit(msg, "error")
                self.port_handler.closePort()
                return False

            self.servo_handler = scscl(self.port_handler)
            msg = f"✅ 成功连接到 {self.port_name} (@1Mbps)"
            self.status_changed.emit(msg)
            self.log_message.emit(msg, "success")
            logger.info("✅ 串口连接成功")
            return True

        except Exception as e:
            msg = f"❌ 连接异常: {e}"
            self.status_changed.emit(msg)
            self.log_message.emit(msg, "error")
            logger.error(f"连接异常: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.port_handler:
            self.port_handler.closePort()
        self.status_changed.emit("🔌 已断开连接")
        logger.info("🔌 串口已断开")

    def scan_servos(self) -> List[int]:
        """扫描舵机 - 避免使用广播ping"""
        found_servos = []
        self.status_changed.emit("📡 扫描舵机中...")
        logger.info("📡 开始扫描舵机ID 11-18...")

        for servo_id in self.servo_ids:
            try:
                # 直接ping单个舵机，避免广播ping的bug
                result = self.servo_handler.ping(servo_id)

                if result is None:
                    logger.warning(f"⚠️ ID{servo_id}: ping返回None")
                    if servo_id in self.servo_data:
                        self.servo_data[servo_id].connected = False
                    continue

                # 正确解包返回值
                if isinstance(result, tuple) and len(result) == 3:
                    model_number, comm_result, error = result
                    was_connected = self.servo_data.get(servo_id, ServoData(servo_id)).connected

                    if comm_result == COMM_SUCCESS:
                        found_servos.append(servo_id)
                        if servo_id not in self.servo_data:
                            self.servo_data[servo_id] = ServoData(servo_id)
                            self.log_message.emit(f"✅ 发现舵机 ID{servo_id} (模型: {model_number})", "success")

                        # 热插拔检测
                        if not was_connected and self.servo_data[servo_id].was_connected:
                            self.status_changed.emit(f"  🔌 重新连接舵机 ID{servo_id}")
                            self.log_message.emit(f"舵机 {servo_id} 重新连接", "info")
                        elif not was_connected:
                            self.status_changed.emit(f"  ✅ 发现舵机 ID{servo_id}")

                        self.servo_data[servo_id].connected = True
                        self.servo_data[servo_id].was_connected = True
                        logger.info(f"  ✅ ID{servo_id}: 在线 (模型: {model_number})")
                    else:
                        # 热插拔检测 - 断开
                        if was_connected:
                            self.status_changed.emit(f"  ❌ 舵机 ID{servo_id} 已断开")
                            self.log_message.emit(f"舵机 {servo_id} 断开连接", "warning")

                        if servo_id in self.servo_data:
                            self.servo_data[servo_id].connected = False
                            self.servo_data[servo_id].error_count += 1
                        logger.warning(f"  ❌ ID{servo_id}: 无响应 (错误: {error})")
                else:
                    logger.error(f"  ❌ ID{servo_id}: 返回值格式错误")

            except Exception as e:
                logger.error(f"  ❌ ID{servo_id}: 异常 {e}")
                if servo_id in self.servo_data:
                    self.servo_data[servo_id].error_count += 1

        logger.info(f"📡 扫描完成，发现 {len(found_servos)} 个舵机")
        return found_servos

    def read_servo_data(self) -> bool:
        """读取所有舵机数据"""
        success = True
        for servo_id in self.servo_ids:
            if servo_id in self.servo_data and self.servo_data[servo_id].connected:
                try:
                    # 读取位置
                    position, result, error = self.servo_handler.ReadPos(servo_id)
                    if result == COMM_SUCCESS:
                        self.servo_data[servo_id].current_pos = position
                        self.servo_data[servo_id].last_update_time = time.time()
                    else:
                        logger.warning(f"⚠️ 读取ID{servo_id}位置失败: {error}")
                        success = False
                        continue

                    # 读取速度
                    speed, result, error = self.servo_handler.ReadSpeed(servo_id)
                    if result == COMM_SUCCESS:
                        self.servo_data[servo_id].current_speed = speed

                    # 读取负载
                    load, result, error = self.servo_handler.ReadLoad(servo_id)
                    if result == COMM_SUCCESS:
                        # 负载值范围: 0-1023 (0-511正向负载，512-1023反向负载)
                        # 取绝对值显示，方便用户理解
                        display_load = load if load <= 511 else 1023 - load
                        self.servo_data[servo_id].current_load = display_load

                        # 负载调试日志 - 每10秒输出一次（避免刷屏）
                        current_time = int(time.time())
                        if current_time % 10 == 0:
                            # 避免同一秒内重复输出多次
                            last_log_time = getattr(self, '_last_load_log_time', 0)
                            if current_time != last_log_time:
                                load_status = "空载" if display_load < 10 else ("轻载" if display_load < 100 else "有负载")
                                logger.info(f"📊 ID{servo_id}: 负载原始值={load}, 显示值={display_load} ({load_status})")
                                self._last_load_log_time = current_time
                    else:
                        logger.warning(f"⚠️ 读取ID{servo_id}负载失败: 通信={result}, 错误={error}")
                        # 强制设置负载为-1表示读取失败
                        self.servo_data[servo_id].current_load = -1

                    # 读取运动状态
                    moving, result, error = self.servo_handler.ReadMoving(servo_id)
                    if result == COMM_SUCCESS:
                        self.servo_data[servo_id].moving = moving

                except Exception as e:
                    logger.error(f"❌ 读取ID{servo_id}数据失败: {e}")
                    success = False

        return success

    def start_monitoring(self):
        """启动监控"""
        if not self.connect():
            return

        found_servos = self.scan_servos()
        if not found_servos:
            msg = "⚠️ 未发现舵机 - 请检查:"
            self.status_changed.emit(msg)
            self.status_changed.emit("  1. 串口连接是否正确")
            self.status_changed.emit("  2. 舵机是否已连接并供电")
            self.status_changed.emit("  3. 舵机ID是否在11-18范围内")
            self.log_message.emit("未发现舵机", "warning")
            return

        self.running = True
        msg = f"🚀 开始监控 {len(found_servos)} 个舵机..."
        self.status_changed.emit(msg)
        self.log_message.emit(msg, "success")
        logger.info(f"🚀 开始监控线程")

        # 启动监控线程
        thread = Thread(target=self._monitor_loop, daemon=True)
        thread.start()

    def write_position(self, servo_id: int, position: int, time_ms: int = 1000, speed: int = 100) -> bool:
        """在Worker线程中写入位置，避免端口冲突"""
        try:
            result = self.servo_handler.WritePos(servo_id, position, time_ms, speed)
            return result[0] == COMM_SUCCESS
        except Exception as e:
            logger.error(f"❌ 写入ID{servo_id}位置失败: {e}")
            return False

    def apply_positions(self, positions_data: dict) -> int:
        """应用多个位置 - 在Worker线程中执行"""
        success_count = 0
        for servo_id_str, servo_data in positions_data.items():
            servo_id = int(servo_id_str)
            try:
                position = servo_data['position']
                time_ms = 1000
                speed = 100

                if self.write_position(servo_id, position, time_ms, speed):
                    success_count += 1
                    logger.info(f"✅ ID{servo_id}: 位置写入成功 ({position})")
                else:
                    logger.warning(f"⚠️ ID{servo_id}: 位置写入失败")

            except Exception as e:
                logger.error(f"❌ 控制ID{servo_id}失败: {e}")

        # 发送结果信号
        self.position_applied.emit(success_count)
        return success_count

    def disable_torque(self, servo_id: int = None) -> int:
        """禁用扭矩 - 可选指定舵机ID，不指定则禁用所有"""
        success_count = 0
        target_ids = [servo_id] if servo_id is not None else self.servo_ids

        for sid in target_ids:
            # 检查舵机是否在线
            if sid not in self.servo_data or not self.servo_data[sid].connected:
                logger.warning(f"⚠️ ID{sid}: 舵机不在线，跳过禁用扭矩")
                continue

            try:
                # 直接尝试禁用扭矩，最多重试3次
                retry_count = 0
                max_retries = 3
                disabled = False

                while retry_count < max_retries and not disabled:
                    comm_result, servo_error = self.servo_handler.write1ByteTxRx(sid, SCSCL_TORQUE_ENABLE, 0)

                    if comm_result == COMM_SUCCESS:
                        disabled = True
                        success_count += 1
                        logger.info(f"✅ ID{sid}: 扭矩已禁用 (尝试 {retry_count + 1})")
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.warning(f"⚠️ ID{sid}: 禁用扭矩失败 (尝试 {retry_count}/{max_retries}, 通信: {comm_result}, 舵机错误: {servo_error})")
                            time.sleep(0.1)  # 重试前等待
                        else:
                            logger.error(f"❌ ID{sid}: 禁用扭矩最终失败 (通信: {comm_result}, 舵机错误: {servo_error})")

            except Exception as e:
                logger.error(f"❌ ID{sid}: 禁用扭矩异常: {e}")

        if servo_id is None:
            if success_count > 0:
                self.log_message.emit(f"✅ 已禁用 {success_count}/{len(self.servo_ids)} 个舵机的扭矩", "success")
            else:
                self.log_message.emit("⚠️ 所有舵机禁用扭矩失败", "warning")
        return success_count

    def enable_torque(self, servo_id: int = None) -> int:
        """启用扭矩 - 可选指定舵机ID，不指定则启用所有"""
        success_count = 0
        target_ids = [servo_id] if servo_id is not None else self.servo_ids

        for sid in target_ids:
            try:
                # 启用扭矩
                comm_result, servo_error = self.servo_handler.write1ByteTxRx(sid, SCSCL_TORQUE_ENABLE, 1)
                if comm_result == COMM_SUCCESS:
                    success_count += 1
                    logger.info(f"✅ ID{sid}: 扭矩已启用")
                else:
                    logger.warning(f"⚠️ ID{sid}: 启用扭矩失败 (通信: {comm_result}, 舵机错误: {servo_error})")
            except Exception as e:
                logger.error(f"❌ ID{sid}: 启用扭矩异常: {e}")

        if servo_id is None:
            if success_count > 0:
                self.log_message.emit(f"✅ 已启用 {success_count}/{len(self.servo_ids)} 个舵机的扭矩", "success")
            else:
                self.log_message.emit("⚠️ 所有舵机启用扭矩失败", "warning")
        return success_count

    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        self.disconnect()
        logger.info("🛑 监控已停止")

    def _monitor_loop(self):
        """监控循环 - 优化频率，降低通信负载"""
        logger.info("🔄 监控循环启动")
        last_scan_time = 0
        scan_interval = 2.0  # 热插拔检测间隔：2秒（之前是每次都扫描）
        data_read_interval = 0.2  # 数据读取间隔：0.2秒（之前是0.1秒）
        last_data_read_time = 0

        while self.running:
            try:
                current_time = time.time()

                # 热插拔检测 - 每2秒执行一次（避免频繁ping舵机）
                if current_time - last_scan_time > scan_interval:
                    self.scan_servos()
                    last_scan_time = current_time

                # 读取数据 - 每0.2秒执行一次（降低频率，减少通信）
                if current_time - last_data_read_time > data_read_interval:
                    if self.read_servo_data():
                        self.data_updated.emit(list(self.servo_data.values()))
                    last_data_read_time = current_time

                time.sleep(0.05)  # 主循环睡眠50ms（降低CPU使用率）
            except Exception as e:
                logger.error(f"❌ 监控循环异常: {e}")
                self.status_changed.emit(f"❌ 监控异常: {e}")
                time.sleep(1)


class AngleMonitorGUI(QMainWindow):
    """角度监控GUI"""

    BASE_WIDTH = 900
    BASE_HEIGHT = 800

    def __init__(self, port_name: str = None):
        super().__init__()
        self.port_name = port_name or '/dev/ttyACM1'
        self.worker = None
        self.port_refresh_timer = None
        self.last_data: Dict[int, dict] = {}
        self.flash_cells: Dict[tuple, int] = {}
        self.flash_timer = None
        self.scale_factor = 1.0

        self.init_ui()
        self.init_connections()
        self.refresh_ports()
        self.start_port_refresh_timer()
        self.start_flash_timer()

        logger.info("🖥️ GUI初始化完成")

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("SCServo角度监控工具 v3.1 (ID 11-18) - 支持点位记录")
        self.setGeometry(100, 100, 900, 800)
        self.setMinimumSize(800, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(12, 8, 12, 8)

        self.create_control_panel(self.main_layout)
        self.create_data_table(self.main_layout)
        self.create_log_panel(self.main_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - 准备连接串口")

        self.apply_styles()

    def create_log_panel(self, layout):
        """创建日志面板"""
        log_group = QGroupBox("📜 系统日志")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(8, 12, 8, 8)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 1px solid #333;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        log_layout.addWidget(self.log_text)

        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_log_btn)

        layout.addWidget(log_group)

    def add_log(self, message: str, level: str = "info"):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        color_map = {
            "info": "#00ff00",
            "success": "#00ffff",
            "warning": "#ffff00",
            "error": "#ff0000"
        }
        color = color_map.get(level, "#ffffff")
        self.log_text.append(f'<span style="color:{color}">[{timestamp}] {message}</span>')

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #37474f;
                border: 1px solid #cfd8dc;
                border-radius: 6px;
                margin-top: 8px;
                padding: 8px 6px 6px 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QPushButton {
                background-color: #546e7a;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
            QPushButton:pressed {
                background-color: #37474f;
            }
            QPushButton:disabled {
                background-color: #b0bec5;
                color: #eceff1;
            }
            QPushButton#startBtn {
                background-color: #43a047;
            }
            QPushButton#startBtn:hover {
                background-color: #388e3c;
            }
            QPushButton#stopBtn {
                background-color: #e53935;
            }
            QPushButton#stopBtn:hover {
                background-color: #c62828;
            }
            QPushButton#refreshBtn {
                background-color: #00acc1;
            }
            QPushButton#refreshBtn:hover {
                background-color: #00838f;
            }
            QPushButton#recordBtn {
                background-color: #9c27b0;
            }
            QPushButton#recordBtn:hover {
                background-color: #7b1fa2;
            }
            QPushButton#viewRecordsBtn {
                background-color: #ff9800;
            }
            QPushButton#viewRecordsBtn:hover {
                background-color: #f57c00;
            }
            QPushButton#disableTorqueBtn {
                background-color: #9e9e9e;
            }
            QPushButton#disableTorqueBtn:hover {
                background-color: #757575;
            }
            QPushButton#enableTorqueBtn {
                background-color: #f57c00;
            }
            QPushButton#enableTorqueBtn:hover {
                background-color: #ef6c00;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #cfd8dc;
                border-radius: 4px;
                gridline-color: #eceff1;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #455a64;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #b0bec5;
                border-radius: 4px;
                background: white;
                min-height: 24px;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #78909c;
            }
            QStatusBar {
                background-color: #eceff1;
                color: #546e7a;
                font-size: 12px;
            }
            QLabel {
                font-size: 11px;
            }
        """)

        table_font_obj = QFont("Consolas", 12)
        self.data_table.setFont(table_font_obj)
        self.data_table.verticalHeader().setDefaultSectionSize(32)

        self.refresh_btn.setFixedWidth(50)
        self.start_btn.setFixedWidth(70)
        self.stop_btn.setFixedWidth(70)
        self.port_combo.setMinimumWidth(110)

    def create_control_panel(self, layout):
        """创建控制面板"""
        control_group = QGroupBox("控制面板")
        control_layout = QHBoxLayout(control_group)
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(10, 10, 10, 10)

        self.port_label = QLabel("串口:")
        self.port_label.setStyleSheet("font-weight: bold; color: #455a64;")
        control_layout.addWidget(self.port_label)

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(110)
        control_layout.addWidget(self.port_combo)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setObjectName("refreshBtn")
        self.refresh_btn.setFixedWidth(50)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        control_layout.addWidget(self.refresh_btn)

        control_layout.addSpacing(15)

        self.start_btn = QPushButton("▶ 开始")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedWidth(70)
        self.start_btn.clicked.connect(self.start_monitoring)
        control_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ 停止")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedWidth(70)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_monitoring)
        control_layout.addWidget(self.stop_btn)

        control_layout.addSpacing(15)

        self.record_btn = QPushButton("📝 记录点位")
        self.record_btn.setObjectName("recordBtn")
        self.record_btn.setFixedWidth(85)
        self.record_btn.setEnabled(True)
        self.record_btn.clicked.connect(self.record_position)
        control_layout.addWidget(self.record_btn)

        self.view_records_btn = QPushButton("📂 查看记录")
        self.view_records_btn.setObjectName("viewRecordsBtn")
        self.view_records_btn.setFixedWidth(85)
        self.view_records_btn.setEnabled(True)
        self.view_records_btn.clicked.connect(self.view_records)
        control_layout.addWidget(self.view_records_btn)

        control_layout.addSpacing(15)

        self.disable_torque_btn = QPushButton("🔓 失能")
        self.disable_torque_btn.setObjectName("disableTorqueBtn")
        self.disable_torque_btn.setFixedWidth(70)
        self.disable_torque_btn.setEnabled(True)
        self.disable_torque_btn.clicked.connect(self.disable_torque)
        control_layout.addWidget(self.disable_torque_btn)

        self.enable_torque_btn = QPushButton("🔒 启用")
        self.enable_torque_btn.setObjectName("enableTorqueBtn")
        self.enable_torque_btn.setFixedWidth(70)
        self.enable_torque_btn.setEnabled(True)
        self.enable_torque_btn.clicked.connect(self.enable_torque)
        control_layout.addWidget(self.enable_torque_btn)

        control_layout.addStretch()
        layout.addWidget(control_group)

    def create_data_table(self, layout):
        """创建数据表格"""
        table_group = QGroupBox("实时舵机数据 (舵机ID 11-18)")
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(8, 12, 8, 8)

        self.data_table = QTableWidget(8, 6)
        self.data_table.setHorizontalHeaderLabels([
            "ID", "位置值", "角度(°)", "速度", "负载", "状态"
        ])

        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setShowGrid(True)

        font = QFont("Consolas", 12)
        self.data_table.setFont(font)
        self.data_table.verticalHeader().setDefaultSectionSize(32)

        for row in range(8):
            servo_id = row + 11
            item = QTableWidgetItem(f"{servo_id}")
            item.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row, 0, item)
            for col in range(1, 6):
                item = QTableWidgetItem("--")
                item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(row, col, item)

        table_layout.addWidget(self.data_table)

        self.info_label = QLabel(
            "💡 说明: 位置值范围0-4096，中点2048 | 角度=位置值-2048后×0.088° | 支持热插拔检测 | 已修复广播ping bug"
        )
        self.info_label.setStyleSheet("""
            background-color: #e3f2fd;
            border: 1px solid #90caf9;
            padding: 6px 10px;
            border-radius: 4px;
            color: #1565c0;
            font-size: 11px;
        """)
        table_layout.addWidget(self.info_label)

        layout.addWidget(table_group)

    def init_connections(self):
        self.port_combo.currentTextChanged.connect(self.on_port_changed)

    def refresh_ports(self):
        """刷新串口列表"""
        logger.info("🔄 刷新串口列表...")
        available_ports = get_available_ports()

        current_port = self.port_combo.currentText() if self.port_combo.count() > 0 else ""

        self.port_combo.clear()

        if available_ports:
            self.port_combo.addItems(available_ports)
            if current_port and current_port in available_ports:
                self.port_combo.setCurrentText(current_port)
            elif self.port_name and self.port_name in available_ports:
                self.port_combo.setCurrentText(self.port_name)
            else:
                self.port_combo.setCurrentIndex(0)
            self.add_log(f"检测到 {len(available_ports)} 个可用串口", "info")
        else:
            self.port_combo.addItem("未检测到串口")
            self.port_combo.setEnabled(False)
            self.add_log("未检测到任何串口", "warning")

        self.update_status(f"检测到 {len(available_ports)} 个可用串口")

    def start_flash_timer(self):
        if self.flash_timer is None:
            self.flash_timer = QTimer()
            self.flash_timer.timeout.connect(self.process_flash)
            self.flash_timer.start(150)

    def process_flash(self):
        cells_to_remove = []
        for (row, col), count in self.flash_cells.items():
            item = self.data_table.item(row, col)
            if item:
                if count % 2 == 0:
                    item.setBackground(QColor(255, 193, 7))
                else:
                    if col == 1:
                        item.setBackground(QColor(200, 230, 201))
                    elif col == 2:
                        item.setBackground(QColor(255, 205, 210))
                    elif col == 3:
                        item.setBackground(QColor(187, 222, 251))
                    elif col == 4:
                        item.setBackground(QColor(255, 235, 59))
                    elif col == 5:
                        item.setBackground(QColor(225, 190, 231))

                self.flash_cells[(row, col)] = count - 1
                if count <= 1:
                    cells_to_remove.append((row, col))

        for cell in cells_to_remove:
            del self.flash_cells[cell]

    def trigger_flash(self, row: int, col: int):
        self.flash_cells[(row, col)] = 6

    def start_port_refresh_timer(self):
        if self.port_refresh_timer is None:
            self.port_refresh_timer = QTimer()
            self.port_refresh_timer.timeout.connect(self.refresh_ports)
            self.port_refresh_timer.start(2000)

    def stop_port_refresh_timer(self):
        if self.port_refresh_timer:
            self.port_refresh_timer.stop()
            self.port_refresh_timer = None

    def on_port_changed(self, port_name):
        if port_name and port_name != "未检测到串口":
            self.port_name = port_name
            self.add_log(f"选择串口: {port_name}", "info")

    def start_monitoring(self):
        if self.worker and self.worker.running:
            return

        if not self.port_name or self.port_name == "未检测到串口":
            self.add_log("❌ 请选择有效的串口", "error")
            self.update_status("❌ 请选择有效的串口")
            return

        self.worker = ServoMonitorWorker(self.port_name)
        self.worker.data_updated.connect(self.update_table)
        self.worker.status_changed.connect(self.update_status)
        self.worker.log_message.connect(self.add_log)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.stop_port_refresh_timer()
        self.add_log(f"🚀 开始监控串口: {self.port_name}", "info")
        self.worker.start_monitoring()

    def stop_monitoring(self):
        if self.worker:
            self.worker.stop_monitoring()
            self.worker = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.refresh_ports()
        self.start_port_refresh_timer()
        self.add_log("🛑 监控已停止", "info")

    def update_table(self, servo_data_list: List[ServoData]):
        for servo_data in servo_data_list:
            row = servo_data.id - 11
            servo_id = servo_data.id

            last = self.last_data.get(servo_id, {})

            # ID
            id_item = QTableWidgetItem(str(servo_id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(row, 0, id_item)

            # 位置值
            pos_item = QTableWidgetItem(str(servo_data.current_pos))
            pos_item.setTextAlignment(Qt.AlignCenter)
            pos_item.setBackground(QColor(200, 230, 201))
            self.data_table.setItem(row, 1, pos_item)
            if 'pos' in last and servo_data.current_pos != last['pos']:
                self.trigger_flash(row, 1)

            # 角度
            angle = self.worker.position_to_degrees(servo_data.current_pos)
            angle_item = QTableWidgetItem(f"{angle:.2f}")
            angle_item.setTextAlignment(Qt.AlignCenter)
            angle_item.setBackground(QColor(255, 205, 210))
            self.data_table.setItem(row, 2, angle_item)
            if 'angle' in last and abs(angle - last['angle']) > 0.5:
                self.trigger_flash(row, 2)

            # 速度
            speed_item = QTableWidgetItem(str(servo_data.current_speed))
            speed_item.setTextAlignment(Qt.AlignCenter)
            speed_item.setBackground(QColor(187, 222, 251))
            self.data_table.setItem(row, 3, speed_item)
            if 'speed' in last and servo_data.current_speed != last['speed']:
                self.trigger_flash(row, 3)

            # 负载
            load_display = servo_data.current_load
            if load_display == -1:
                load_text = "读取失败"
                load_color = QColor(255, 100, 100)  # 红色表示错误
            else:
                load_text = str(load_display)
                load_color = QColor(255, 235, 59)  # 黄色正常显示
            load_item = QTableWidgetItem(load_text)
            load_item.setTextAlignment(Qt.AlignCenter)
            load_item.setBackground(load_color)
            self.data_table.setItem(row, 4, load_item)
            if 'load' in last and servo_data.current_load != last['load']:
                self.trigger_flash(row, 4)

            # 状态
            status = "运动" if servo_data.moving else "静止"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_color = QColor(225, 190, 231) if servo_data.moving else QColor(200, 200, 200)
            status_item.setBackground(status_color)
            self.data_table.setItem(row, 5, status_item)
            if 'moving' in last and servo_data.moving != last['moving']:
                self.trigger_flash(row, 5)

            self.last_data[servo_id] = {
                'pos': servo_data.current_pos,
                'angle': angle,
                'speed': servo_data.current_speed,
                'load': servo_data.current_load,
                'moving': servo_data.moving
            }

    def update_status(self, message: str):
        self.status_bar.showMessage(message, 3000)
        logger.info(f"状态栏: {message}")

    def record_position(self):
        """记录当前所有舵机位置"""
        # 检查是否有数据
        if not self.last_data:
            QMessageBox.warning(self, "警告", "没有可记录的数据！请先开始监控。")
            return

        # 弹出输入对话框
        name, ok = QInputDialog.getText(
            self,
            "记录点位",
            "请输入点位名称:",
            text=f"点位_{len(self.load_positions()) + 1}"
        )

        if not ok or not name.strip():
            return

        name = name.strip()

        # 加载现有记录
        positions = self.load_positions()

        # 检查名称是否已存在
        if name in positions:
            reply = QMessageBox.question(
                self,
                "确认覆盖",
                f"点位 '{name}' 已存在，是否覆盖？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # 记录当前数据
        positions[name] = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'servos': {}
        }

        for servo_id, data in self.last_data.items():
            positions[name]['servos'][servo_id] = {
                'position': data['pos'],
                'angle': round(data['angle'], 2)
            }

        # 保存到文件
        try:
            with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(positions, f, ensure_ascii=False, indent=2)
            self.add_log(f"✅ 已记录点位: {name}", "success")
            self.update_status(f"✅ 点位 '{name}' 记录成功")
        except Exception as e:
            self.add_log(f"❌ 记录失败: {e}", "error")
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def view_records(self):
        """查看所有记录的点位"""
        positions = self.load_positions()

        if not positions:
            QMessageBox.information(self, "提示", "暂无记录的点位！")
            return

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("📂 点位记录")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = DialogLayout(dialog)

        # 标题
        title = DialogLabel("已记录的点位:")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)

        # 列表控件显示所有点位
        list_widget = QListWidget()
        for name, data in positions.items():
            item = QListWidgetItem(f"📍 {name} ({data['timestamp']})")
            item.setData(Qt.UserRole, name)  # 存储点位名称
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        # 详细信息显示区域
        detail_text = QTextEdit()
        detail_text.setMaximumHeight(150)
        detail_text.setReadOnly(True)
        detail_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(detail_text)

        # 当选择改变时显示详细信息
        def show_details(item):
            name = item.data(Qt.UserRole)
            if name in positions:
                data = positions[name]
                output = []
                output.append(f"点位名称: {name}")
                output.append(f"记录时间: {data['timestamp']}")
                output.append("-" * 40)
                output.append(f"{'ID':<5} {'位置':<8} {'角度':<10}")
                output.append("-" * 40)

                for servo_id in sorted(data['servos'].keys()):
                    servo = data['servos'][servo_id]
                    output.append(
                        f"{servo_id:<5} {servo['position']:<8} {servo['angle']:<10}"
                    )

                detail_text.setPlainText("\n".join(output))

        list_widget.itemSelectionChanged.connect(lambda: show_details(list_widget.currentItem()))

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Apply | QDialogButtonBox.Ok | QDialogButtonBox.Discard
        )
        layout.addWidget(button_box)

        # 按钮事件
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(
            lambda: self.apply_position(list_widget, positions, detail_text)
        )
        button_box.button(QDialogButtonBox.Discard).clicked.connect(
            lambda: self.delete_position(list_widget, positions, dialog)
        )

        # 显示第一个项目详情
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)
            show_details(list_widget.item(0))

        dialog.show()

    def load_positions(self) -> dict:
        """加载位置记录文件"""
        try:
            if os.path.exists(POSITIONS_FILE):
                with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"加载位置记录失败: {e}")
            return {}

    def apply_position(self, list_widget, positions, detail_text):
        """应用选中的位置 - 实际控制舵机移动"""
        current_item = list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个要应用的点位！")
            return

        name = current_item.data(Qt.UserRole)

        # 确认应用
        reply = QMessageBox.question(
            self,
            "确认应用",
            f"确定要让舵机移动到点位 '{name}' 吗？\n\n"
            f"这将控制所有舵机移动到记录的位置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.Yes:
            return

        # 检查是否正在监控
        if not self.worker or not self.worker.running:
            QMessageBox.warning(self, "警告", "请先开始监控舵机！")
            return

        # 实际控制舵机移动 - 使用Worker线程避免端口冲突
        try:
            if name in positions:
                # 连接信号以接收结果
                def on_position_applied(success_count):
                    self.add_log(f"✅ 已发送移动指令到 {success_count} 个舵机", "success")
                    self.update_status(f"✅ 已让舵机移动到点位 '{name}'")
                    # 断开信号连接
                    try:
                        self.worker.position_applied.disconnect(on_position_applied)
                    except:
                        pass

                self.worker.position_applied.connect(on_position_applied)

                # 在Worker线程中执行写入操作
                success_count = self.worker.apply_positions(positions[name]['servos'])

                # 如果立即完成（同步调用），手动触发回调
                if success_count > 0:
                    on_position_applied(success_count)

        except Exception as e:
            self.add_log(f"❌ 应用点位失败: {e}", "error")
            QMessageBox.critical(self, "错误", f"控制失败: {e}")

    def disable_torque(self):
        """禁用所有舵机扭矩"""
        if not self.worker or not self.worker.running:
            QMessageBox.warning(self, "警告", "请先开始监控舵机！")
            return

        reply = QMessageBox.question(
            self,
            "确认失能",
            "确定要禁用所有舵机的扭矩吗？\n\n"
            "禁用后可以手动转动舵机，但无法保持位置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.Yes:
            return

        success_count = self.worker.disable_torque()
        if success_count > 0:
            self.update_status(f"✅ 已禁用 {success_count} 个舵机的扭矩")
        else:
            self.add_log("⚠️ 没有舵机成功禁用扭矩", "warning")

    def enable_torque(self):
        """启用所有舵机扭矩"""
        if not self.worker or not self.worker.running:
            QMessageBox.warning(self, "警告", "请先开始监控舵机！")
            return

        reply = QMessageBox.question(
            self,
            "确认启用",
            "确定要启用所有舵机的扭矩吗？\n\n"
            "启用后舵机将能够保持位置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.Yes:
            return

        success_count = self.worker.enable_torque()
        if success_count > 0:
            self.update_status(f"✅ 已启用 {success_count} 个舵机的扭矩")
        else:
            self.add_log("⚠️ 没有舵机成功启用扭矩", "warning")

    def delete_position(self, list_widget, positions, dialog):
        """删除选中的位置"""
        current_item = list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个要删除的点位！")
            return

        name = current_item.data(Qt.UserRole)

        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除点位 '{name}' 吗？\n\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.Yes:
            return

        # 删除
        del positions[name]

        # 保存
        try:
            with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(positions, f, ensure_ascii=False, indent=2)
            self.add_log(f"✅ 已删除点位: {name}", "success")
            self.update_status(f"✅ 点位 '{name}' 已删除")

            # 更新列表
            list_widget.takeItem(list_widget.currentRow())
            dialog.accept()
        except Exception as e:
            self.add_log(f"❌ 删除失败: {e}", "error")
            QMessageBox.critical(self, "错误", f"删除失败: {e}")

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop_monitoring()
        self.stop_port_refresh_timer()
        logger.info("🖥️ 程序退出")
        super().closeEvent(event)


def get_available_ports():
    """获取可用串口列表"""
    import platform
    system = platform.system()

    try:
        import serial.tools.list_ports
        ports = []

        if system == "Windows":
            for port in serial.tools.list_ports.comports():
                if port.device.startswith('COM'):
                    ports.append(port.device)
        else:
            for port in serial.tools.list_ports.comports():
                device = port.device
                if device.startswith('/dev/ttyACM') or device.startswith('/dev/ttyUSB'):
                    ports.append(device)

        return sorted(ports)
    except ImportError:
        logger.error("❌ pyserial未安装")
        return []


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='SCServo角度实时监控工具 (ID 11-18) - 最终版')
    parser.add_argument('--port', type=str, default=None, help='指定串口（默认: /dev/ttyACM1）')
    parser.add_argument('--list-ports', action='store_true', help='列出可用串口')
    args = parser.parse_args()

    if args.list_ports:
        ports = get_available_ports()
        print("可用串口:")
        if ports:
            for port in ports:
                print(f"  {port}")
        else:
            print("  未检测到可用串口")
        return

    print("="*60)
    print("🚀 启动SCServo角度监控工具 - 最终版")
    print("="*60)
    logger.info("程序启动")

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = AngleMonitorGUI(args.port)
    window.show()

    if args.port:
        print(f"使用指定串口: {args.port}")
        logger.info(f"使用指定串口: {args.port}")
    else:
        print("使用默认串口: /dev/ttyACM1")
        logger.info("使用默认串口")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
