#include <SCServo.h>

SCSCL sc;

// --- 硬件定义 ---
// (你刚才的代码写的是 D4/D5，如果还是 D9/D10 请自行修改这里)
#define SERVO_TX_PIN D4
#define SERVO_RX_PIN D5

// ==========================================
// [全手配置: 10位精度 0-1023]
// ==========================================

// 中心点
const int CENTER_POS = 512;

// 动作强度
const float BEND_STRENGTH = 200.0; // 弯曲幅度
const float YAW_STRENGTH  = 100.0; // 摆动幅度

// 输入范围
const float IN_BEND_MIN = 20.0;   // 张开
const float IN_BEND_MAX = 160.0;  // 握拳
const float IN_YAW_MIN = -100.0;
const float IN_YAW_MAX = 100.0;

// ==========================================

float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// --- 通用手指控制函数 ---
// id_left:  左电机ID (如 11, 13, 15, 17)
// id_right: 右电机ID (如 12, 14, 16, 18)
// isThumb:  是否是大拇指 (true/false)
void setFinger(int id_left, int id_right, float inputBend, float inputYaw, bool isThumb) {
  
  // 1. 限制范围
  inputBend = constrain(inputBend, IN_BEND_MIN, IN_BEND_MAX);
  inputYaw  = constrain(inputYaw, IN_YAW_MIN, IN_YAW_MAX);

  // 2. 计算系数 (-1.0 ~ 1.0)
  float factorBend = mapFloat(inputBend, IN_BEND_MIN, IN_BEND_MAX, -1.0, 1.0);
  float factorYaw  = mapFloat(inputYaw, IN_YAW_MIN, IN_YAW_MAX, -1.0, 1.0);

  // 3. 计算偏移量
  float offsetBend = factorBend * BEND_STRENGTH;
  float offsetYaw  = factorYaw * YAW_STRENGTH;

  // 4. [核心逻辑]
  int posLeft, posRight;

  if (isThumb) {
    // === 大拇指逻辑 (通常与四指相反) ===
    // 尝试反转弯曲方向：Left减, Right加
    // 如果大拇指方向反了，把这里的 +/- 对调即可
    posLeft  = CENTER_POS - (int)offsetBend + (int)offsetYaw;
    posRight = CENTER_POS + (int)offsetBend + (int)offsetYaw;
  } else {
    // === 普通手指逻辑 (食指、中指、无名指) ===
    // 沿用你验证过的 17/18 成功逻辑：
    // 张开(-200) -> Left变小(+ -200), Right变大(- -200)
    posLeft  = CENTER_POS + (int)offsetBend + (int)offsetYaw;
    posRight = CENTER_POS - (int)offsetBend + (int)offsetYaw;
  }

  // 5. 安全限位
  posLeft  = constrain(posLeft, 100, 900);
  posRight = constrain(posRight, 100, 900);

  // 6. 下发指令
  sc.WritePos(id_left, posLeft, 0, 1000); // 1000ms 速度
  sc.WritePos(id_right, posRight, 0, 1000);
}

// 封装一个函数控制整只手
void setFullHand(float bend, float yaw) {
  // 大拇指 (11, 12) - 开启特殊逻辑
  setFinger(11, 12, bend, yaw, true);
  
  // 食指 (13, 14)
  setFinger(13, 14, bend, yaw, false);
  
  // 中指 (15, 16)
  setFinger(15, 16, bend, yaw, false);
  
  // 无名指 (17, 18) - 你的验证基准
  setFinger(17, 18, bend, yaw, false);
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(1000000, SERIAL_8N1, SERVO_RX_PIN, SERVO_TX_PIN);
  sc.pSerial = &Serial1;
  delay(1000);

  Serial.println("==========================");
  Serial.println("AmazingHand Full Control");
  Serial.println("Range: 0-1023");
  Serial.println("==========================");

  // 1. 开启所有电机扭矩 (11 ~ 18)
  for (int i = 11; i <= 18; i++) {
    sc.EnableTorque(i, 1);
    delay(20);
  }
  delay(500);

  // 2. 初始化：整手张开
  Serial.println("Init: OPEN HAND");
  setFullHand(20.0, 0.0);
  
  delay(2000);
}

void loop() {
  // === 动作演示 ===

  // 1. 握拳 (Fist)
  Serial.println(">>> FIST (160)");
  setFullHand(160.0, 0.0);
  delay(3000);

  // 2. 张开 (Open)
  Serial.println(">>> OPEN (20)");
  setFullHand(20.0, 0.0);
  delay(3000);

  // 3. 挥手测试 (Wave) - 左右摆动
  Serial.println(">>> WAVE LEFT");
  setFullHand(90.0, -100.0); // 半握状态向左
  delay(1500);

  Serial.println(">>> WAVE RIGHT");
  setFullHand(90.0, 100.0); // 半握状态向右
  delay(1500);
  
  // 回中
  setFullHand(20.0, 0.0);
  delay(2000);
  
  // 4. 单独动食指 (勾引动作)
  Serial.println(">>> Index Finger Demo");
  setFinger(13, 14, 160.0, 0.0, false); // 食指弯曲
  delay(1000);
  setFinger(13, 14, 20.0, 0.0, false);  // 食指伸直
  delay(1000);
}