// #include <SCServo.h>

// SCSCL sc;

// // --- 引脚定义 ---
// #define SERVO_TX_PIN D9
// #define SERVO_RX_PIN D10

// void setup() {
//   Serial.begin(115200);
//   Serial1.begin(1000000, SERIAL_8N1, SERVO_RX_PIN, SERVO_TX_PIN);
//   sc.pSerial = &Serial1;
//   delay(1000);

//   Serial.println("=== ID 1 单独测试 (范围 0-1023) ===");
  
//   // 开启 ID 1 扭矩
//   sc.EnableTorque(17, 1);
//   delay(500);
// }

// void loop() {
//   // 1. 先去中心 (512)
//   Serial.println(">>> 去中心 (512)");
//   sc.WritePos(17, 512, 0, 1000);
//   delay(2000);

//   // 2. 变小 (200)
//   Serial.println(">>> 变小 -> 200");
//   sc.WritePos(17, 200, 0, 1000);
//   delay(2000);

//   // 3. 回中心 (512)
//   Serial.println(">>> 回中心 (512)");
//   sc.WritePos(17, 512, 0, 1000);
//   delay(2000);

//   // 4. 变大 (800) -- 请观察这里是顺时针还是逆时针！
//   Serial.println(">>> 变大 -> 800 (请观察方向!)");
//   sc.WritePos(17, 800, 0, 1000);
//   delay(2000);
// }

#include <SCServo.h>

SCSCL sc;

// --- 硬件定义 ---
#define SERVO_TX_PIN D9
#define SERVO_RX_PIN D10

// ==========================================
// [最终配置: 10位精度 0-1023]
// ==========================================
const int ID_LEFT = 17;   // 你的无名指电机1
const int ID_RIGHT = 18;  // 你的无名指电机2

// 核心修正：中心点是 512
const int CENTER_POS = 512;

// 动作幅度 (总范围只有1024，所以幅度设小一点)
const float BEND_STRENGTH = 200.0; // 弯曲幅度 (±200)
const float YAW_STRENGTH  = 100.0; // 摆动幅度 (±100)

// 你的观测结论：
// 张开时 -> 17 变小 (逆时针)
// 张开时 -> 18 变大 (顺时针)

// 输入范围
const float IN_BEND_MIN = 20.0;   // 张开
const float IN_BEND_MAX = 160.0;  // 握拳
const float IN_YAW_MIN = -100.0;
const float IN_YAW_MAX = 100.0;

// ==========================================

float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// --- 核心控制函数 ---
void controlFinger(float inputBend, float inputYaw) {
  
  inputBend = constrain(inputBend, IN_BEND_MIN, IN_BEND_MAX);
  inputYaw = constrain(inputYaw, IN_YAW_MIN, IN_YAW_MAX);

  // 1. 计算系数
  // 张开(20) -> -1.0
  // 握拳(160) -> 1.0
  float factorBend = mapFloat(inputBend, IN_BEND_MIN, IN_BEND_MAX, -1.0, 1.0);
  float factorYaw  = mapFloat(inputYaw, IN_YAW_MIN, IN_YAW_MAX, -1.0, 1.0);

  // 2. 计算偏移量
  float offsetBend = factorBend * BEND_STRENGTH;
  float offsetYaw  = factorYaw * YAW_STRENGTH;

  // 3. [根据你的观测计算]
  // 当张开 (factorBend = -1.0, offsetBend = -200) 时：
  
  // ID 17 需要变小 -> 加上 offsetBend (512 + (-200) = 312)
  int pos17 = CENTER_POS + (int)offsetBend + (int)offsetYaw;

  // ID 18 需要变大 -> 减去 offsetBend (512 - (-200) = 712)
  int pos18 = CENTER_POS - (int)offsetBend + (int)offsetYaw;

  // 4. 安全限位 (0-1023)
  pos17 = constrain(pos17, 100, 900); // 留点头尾余量
  pos18 = constrain(pos18, 100, 900);

  // 5. 下发指令
  sc.WritePos(ID_LEFT, pos17, 0, 1000);
  sc.WritePos(ID_RIGHT, pos18, 0, 1000);

  // 调试打印
  Serial.print("BEND:"); Serial.print(inputBend);
  Serial.print(" -> 17:"); Serial.print(pos17);
  Serial.print(" | 18:"); Serial.println(pos18);
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(1000000, SERIAL_8N1, SERVO_RX_PIN, SERVO_TX_PIN);
  sc.pSerial = &Serial1;
  delay(1000);

  // 开启扭矩
  sc.EnableTorque(ID_LEFT, 1);
  sc.EnableTorque(ID_RIGHT, 1);
  delay(100);

  Serial.println("===============================");
  Serial.println("System Start (Range 0-1023)");
  Serial.println("Initializing: OPEN HAND (Bend=20)");
  Serial.println("Target: 17~312, 18~712");
  Serial.println("===============================");

  // 初始化：张开
  controlFinger(20.0, 0.0);
  delay(2000);
}

void loop() {
  // 1. 握拳 (Fist)
  // 17 -> 712 (变大), 18 -> 312 (变小) -> 收紧
  Serial.println(">>> Action: FIST (160)");
  controlFinger(160.0, 0.0);
  delay(2000);

  // 2. 张开 (Open)
  // 17 -> 312 (变小), 18 -> 712 (变大) -> 放松
  Serial.println(">>> Action: OPEN (20)");
  controlFinger(20.0, 0.0);
  delay(2000);
  
  // 3. 摆动测试
  Serial.println(">>> YAW Left");
  controlFinger(90.0, -100.0); 
  delay(1000);
  
  Serial.println(">>> YAW Right");
  controlFinger(90.0, 100.0);  
  delay(1000);
}