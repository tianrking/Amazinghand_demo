#!/usr/bin/env python3
"""
AmazingHand 点位重放上位机
使用PySide6实现，可读取保存的点位并重放
"""
import sys
import json
import os
import numpy as np
import traceback
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QGroupBox,
    QTextEdit, QMessageBox, QFileDialog, QSpinBox, QSlider, QFrame,
    QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QPalette, QColor
from rustypot import Scs0009PyController

# --- 配置 ---
FINGERS = [
    {'name': 'Thumb',   'm1_id': 11, 'm2_id': 12},
    {'name': 'Ring',    'm1_id': 13, 'm2_id': 14},
    {'name': 'Middle',  'm1_id': 15, 'm2_id': 16},
    {'name': 'Index',   'm1_id': 17, 'm2_id': 18},
]

DEFAULT_POSITION_FILE = "/home/w0x7ce/Desktop/AmazingHand/PythonExample/points_record.json"
SERVO_CONTROLLER_PORT = "/dev/ttyACM0"

# --- 现代化样式表 ---
STYLE_SHEET = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
    font-size: 13px;
    color: #e0e0e0;
}

QGroupBox {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 10px;
    margin-top: 12px;
    padding: 15px;
    font-weight: bold;
    font-size: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 8px;
    color: #00d9ff;
}

QPushButton {
    background-color: #0f3460;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1a5276;
}

QPushButton:pressed {
    background-color: #0a2647;
}

QPushButton:disabled {
    background-color: #2d2d44;
    color: #666666;
}

QPushButton#connectBtn {
    background-color: #1e6f5c;
}

QPushButton#connectBtn:hover {
    background-color: #289672;
}

QPushButton#disconnectBtn {
    background-color: #c0392b;
}

QPushButton#disconnectBtn:hover {
    background-color: #e74c3c;
}

QPushButton#playBtn {
    background-color: #27ae60;
}

QPushButton#playBtn:hover {
    background-color: #2ecc71;
}

QPushButton#playBtn:disabled {
    background-color: #2d2d44;
}

QPushButton#stopBtn {
    background-color: #e74c3c;
}

QPushButton#stopBtn:hover {
    background-color: #c0392b;
}

QListWidget {
    background-color: #0f0f23;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 5px;
    outline: none;
}

QListWidget::item {
    background-color: #16213e;
    border-radius: 5px;
    padding: 10px;
    margin: 3px;
}

QListWidget::item:selected {
    background-color: #0f3460;
    border: 1px solid #00d9ff;
}

QListWidget::item:hover {
    background-color: #1a3a5c;
}

QTextEdit {
    background-color: #0f0f23;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 8px;
    color: #b0b0b0;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 12px;
}

QLabel {
    color: #e0e0e0;
}

QLabel#statusConnected {
    color: #2ecc71;
    font-weight: bold;
    font-size: 14px;
}

QLabel#statusDisconnected {
    color: #e74c3c;
    font-weight: bold;
    font-size: 14px;
}

QLabel#detailLabel {
    background-color: #0f0f23;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 10px;
    color: #a0a0a0;
}

QSlider::groove:horizontal {
    border: 1px solid #0f3460;
    height: 8px;
    background: #0f0f23;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #00d9ff;
    border: none;
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #33e5ff;
}

QSlider::sub-page:horizontal {
    background: #0f3460;
    border-radius: 4px;
}

QSpinBox {
    background-color: #0f0f23;
    border: 1px solid #0f3460;
    border-radius: 5px;
    padding: 5px 10px;
    color: #e0e0e0;
    min-width: 80px;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #0f3460;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #1a5276;
}

QMessageBox {
    background-color: #16213e;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""


class ServoController:
    """伺服电机控制器封装"""

    def __init__(self):
        self.controller = None
        self.all_servo_ids = [id for finger in FINGERS for id in (finger['m1_id'], finger['m2_id'])]
        self.connected = False

    def connect(self):
        """连接到伺服控制器"""
        try:
            self.controller = Scs0009PyController(
                serial_port=SERVO_CONTROLLER_PORT,
                baudrate=1000000,
                timeout=0.5,
            )
            # 启动扭矩
            self.controller.sync_write_torque_enable(self.all_servo_ids, [1] * len(self.all_servo_ids))
            # 设置速度
            self.controller.sync_write_goal_speed(self.all_servo_ids, [6] * len(self.all_servo_ids))
            self.connected = True
            return True, "连接成功"
        except Exception as e:
            self.connected = False
            return False, f"连接失败: {e}"

    def disconnect(self):
        """断开连接并关闭扭矩"""
        if self.controller and self.connected:
            try:
                self.controller.sync_write_torque_enable(self.all_servo_ids, [0] * len(self.all_servo_ids))
            except:
                pass
        self.connected = False

    def move_to_position(self, servo_data):
        """移动到指定点位"""
        if not self.connected or not self.controller:
            return False, "未连接控制器"

        try:
            ids = []
            positions_rad = []

            for servo_id_str, data in servo_data.items():
                servo_id = int(servo_id_str)
                # position是脉冲值(0-4096, 中心2048)，需要转回弧度
                raw_pos = data['position']
                position_rad = (raw_pos - 2048) / 4096 * (2 * np.pi)
                ids.append(servo_id)
                positions_rad.append(position_rad)

            # 按ID排序确保顺序正确
            sorted_pairs = sorted(zip(ids, positions_rad), key=lambda x: x[0])
            ids = [p[0] for p in sorted_pairs]
            positions_rad = [p[1] for p in sorted_pairs]

            self.controller.sync_write_goal_position(ids, positions_rad)
            return True, "移动成功"
        except Exception as e:
            return False, f"移动失败: {e}"

    def set_speed(self, speed):
        """设置电机速度"""
        if self.connected and self.controller:
            try:
                self.controller.sync_write_goal_speed(self.all_servo_ids, [speed] * len(self.all_servo_ids))
            except:
                pass


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AmazingHand 点位重放上位机")
        self.setMinimumSize(700, 600)

        self.points_data = {}
        self.servo_controller = ServoController()
        self.auto_play_timer = QTimer()
        self.auto_play_timer.timeout.connect(self.auto_play_next)
        self.auto_play_index = 0

        self.init_ui()
        self.load_default_file()

    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- 标题 ---
        title_label = QLabel("🤖 AmazingHand 点位重放系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #00d9ff;
            padding: 10px;
        """)
        main_layout.addWidget(title_label)

        # --- 连接控制区 ---
        conn_group = QGroupBox("📡 连接控制")
        conn_layout = QHBoxLayout(conn_group)
        conn_layout.setSpacing(15)

        self.conn_status_label = QLabel("● 未连接")
        self.conn_status_label.setObjectName("statusDisconnected")
        conn_layout.addWidget(self.conn_status_label)

        self.connect_btn = QPushButton("🔌 连接")
        self.connect_btn.setObjectName("connectBtn")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        conn_layout.addWidget(self.connect_btn)

        conn_layout.addStretch()

        # 速度控制
        speed_label = QLabel("⚡ 速度:")
        conn_layout.addWidget(speed_label)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 20)
        self.speed_slider.setValue(6)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        conn_layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("6")
        self.speed_label.setStyleSheet("color: #00d9ff; font-weight: bold; min-width: 25px;")
        conn_layout.addWidget(self.speed_label)

        main_layout.addWidget(conn_group)

        # --- 文件操作区 ---
        file_group = QGroupBox("📁 文件操作")
        file_layout = QHBoxLayout(file_group)
        file_layout.setSpacing(10)

        self.load_btn = QPushButton("📂 加载JSON文件")
        self.load_btn.clicked.connect(self.load_file)
        self.load_btn.setCursor(Qt.PointingHandCursor)
        file_layout.addWidget(self.load_btn)

        self.reload_btn = QPushButton("🔄 重新加载")
        self.reload_btn.clicked.connect(self.load_default_file)
        self.reload_btn.setCursor(Qt.PointingHandCursor)
        file_layout.addWidget(self.reload_btn)

        file_layout.addStretch()
        main_layout.addWidget(file_group)

        # --- 点位列表区 ---
        list_group = QGroupBox("📍 点位列表")
        list_layout = QVBoxLayout(list_group)

        self.point_list = QListWidget()
        self.point_list.itemDoubleClicked.connect(self.on_point_double_clicked)
        self.point_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.point_list.setMinimumHeight(150)
        list_layout.addWidget(self.point_list)

        # 点位详情
        self.detail_label = QLabel("选择点位查看详情")
        self.detail_label.setObjectName("detailLabel")
        self.detail_label.setWordWrap(True)
        self.detail_label.setMinimumHeight(60)
        list_layout.addWidget(self.detail_label)

        main_layout.addWidget(list_group)

        # --- 控制按钮区 ---
        ctrl_group = QGroupBox("🎮 控制面板")
        ctrl_layout = QHBoxLayout(ctrl_group)
        ctrl_layout.setSpacing(15)

        self.play_btn = QPushButton("▶ 执行选中")
        self.play_btn.setObjectName("playBtn")
        self.play_btn.clicked.connect(self.play_selected)
        self.play_btn.setEnabled(False)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        ctrl_layout.addWidget(self.play_btn)

        self.play_all_btn = QPushButton("⏩ 连续播放")
        self.play_all_btn.clicked.connect(self.toggle_auto_play)
        self.play_all_btn.setCursor(Qt.PointingHandCursor)
        ctrl_layout.addWidget(self.play_all_btn)

        ctrl_layout.addWidget(QLabel("间隔:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 5000)
        self.interval_spin.setValue(1000)
        self.interval_spin.setSingleStep(100)
        self.interval_spin.setSuffix(" ms")
        ctrl_layout.addWidget(self.interval_spin)

        ctrl_layout.addStretch()
        main_layout.addWidget(ctrl_group)

        # --- 日志区 ---
        log_group = QGroupBox("📋 运行日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setPlaceholderText("日志信息将显示在这里...")
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_group)

    def log(self, msg):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {msg}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def toggle_connection(self):
        """切换连接状态"""
        if self.servo_controller.connected:
            # 断开连接前先停止自动播放
            if self.auto_play_timer.isActive():
                self.auto_play_timer.stop()
                self.play_all_btn.setText("⏩ 连续播放")
                self.log("自动播放已停止")

            self.servo_controller.disconnect()
            self.conn_status_label.setText("● 未连接")
            self.conn_status_label.setObjectName("statusDisconnected")
            self.conn_status_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
            self.connect_btn.setText("🔌 连接")
            self.connect_btn.setObjectName("connectBtn")
            self.connect_btn.setStyleSheet("")  # 重置让样式表生效
            self.log("已断开连接")
        else:
            success, msg = self.servo_controller.connect()
            if success:
                self.conn_status_label.setText("● 已连接")
                self.conn_status_label.setObjectName("statusConnected")
                self.conn_status_label.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px;")
                self.connect_btn.setText("⏏ 断开")
                self.connect_btn.setObjectName("disconnectBtn")
                self.connect_btn.setStyleSheet("")
                self.log(f"✓ {msg}")
            else:
                self.log(f"✗ {msg}")
                QMessageBox.warning(self, "连接失败", msg)

    def on_speed_changed(self, value):
        """速度变化"""
        self.speed_label.setText(str(value))
        self.servo_controller.set_speed(value)

    def load_default_file(self):
        """加载默认文件"""
        if os.path.exists(DEFAULT_POSITION_FILE):
            self.load_json_file(DEFAULT_POSITION_FILE)
        else:
            self.log(f"默认文件不存在: {DEFAULT_POSITION_FILE}")

    def load_file(self):
        """选择并加载文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择点位JSON文件",
            os.path.dirname(DEFAULT_POSITION_FILE),
            "JSON文件 (*.json)"
        )
        if file_path:
            self.load_json_file(file_path)

    def load_json_file(self, file_path):
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.points_data = json.load(f)

            self.point_list.clear()
            for point_name in self.points_data.keys():
                item = QListWidgetItem(f"  📌 {point_name}")
                self.point_list.addItem(item)

            self.log(f"✓ 已加载 {len(self.points_data)} 个点位")
        except Exception as e:
            self.log(f"✗ 加载失败: {e}")
            QMessageBox.warning(self, "加载失败", str(e))

    def on_selection_changed(self):
        """选择变化"""
        items = self.point_list.selectedItems()
        self.play_btn.setEnabled(len(items) > 0)

        if items:
            display_text = items[0].text()
            point_name = display_text.replace("  📌 ", "")
            point_data = self.points_data.get(point_name, {})
            timestamp = point_data.get('timestamp', 'N/A')
            servos = point_data.get('servos', {})

            detail = f"📍 点位: {point_name}\n"
            detail += f"🕐 时间: {timestamp}\n"
            detail += "🔧 伺服角度: "
            angles = [f"ID{k}={v.get('angle', 0):.1f}°" for k, v in servos.items()]
            detail += ", ".join(angles)

            self.detail_label.setText(detail)

    def on_point_double_clicked(self, item):
        """双击点位执行"""
        self.play_selected()

    def play_selected(self):
        """执行选中的点位"""
        items = self.point_list.selectedItems()
        if not items:
            return

        if not self.servo_controller.connected:
            QMessageBox.warning(self, "提示", "请先连接控制器")
            return

        display_text = items[0].text()
        point_name = display_text.replace("  📌 ", "")
        point_data = self.points_data.get(point_name, {})
        servo_data = point_data.get('servos', {})

        if servo_data:
            success, msg = self.servo_controller.move_to_position(servo_data)
            if success:
                self.log(f"✓ 执行: {point_name}")
            else:
                self.log(f"✗ 失败: {msg}")

    def toggle_auto_play(self):
        """切换自动播放"""
        if self.auto_play_timer.isActive():
            self.auto_play_timer.stop()
            self.play_all_btn.setText("⏩ 连续播放")
            self.play_all_btn.setObjectName("")
            self.log("停止自动播放")
        else:
            if not self.servo_controller.connected:
                QMessageBox.warning(self, "提示", "请先连接控制器")
                return

            if self.point_list.count() == 0:
                QMessageBox.warning(self, "提示", "没有可播放的点位")
                return

            self.auto_play_index = 0
            self.auto_play_timer.start(self.interval_spin.value())
            self.play_all_btn.setText("⏹ 停止播放")
            self.play_all_btn.setObjectName("stopBtn")
            self.log("开始自动播放")
            self.auto_play_next()

    def auto_play_next(self):
        """播放下一个点位"""
        if self.auto_play_index >= self.point_list.count():
            self.auto_play_index = 0  # 循环播放

        self.point_list.setCurrentRow(self.auto_play_index)
        self.play_selected()
        self.auto_play_index += 1

    def closeEvent(self, event):
        """关闭窗口时断开连接"""
        self.auto_play_timer.stop()
        self.servo_controller.disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
