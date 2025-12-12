#include <SCServo.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// ==========================================
// 硬件配置
// ==========================================
SCSCL sc;
WebServer server(80);

#define SERVO_TX_PIN D9
#define SERVO_RX_PIN D10

// ==========================================
// 手指控制参数
// ==========================================
const int CENTER_POS = 512;
const float BEND_STRENGTH = 200.0;
const float YAW_STRENGTH = 100.0;
const float IN_BEND_MIN = 20.0;
const float IN_BEND_MAX = 160.0;
const float IN_YAW_MIN = -100.0;
const float IN_YAW_MAX = 100.0;

// ==========================================
// WiFi配置
// ==========================================
const char* ssid = "AmazingHand";
const char* password = "12345678";

// ==========================================
// 每根手指的独立控制状态
// ==========================================
struct FingerControl {
  float bend[4];    // 0:食指, 1:中指, 2:无名指, 3:小指
  float yaw[4];     // 0:食指, 1:中指, 2:无名指, 3:小指
  float thumbBend;  // 大拇指弯曲
  float thumbYaw;   // 大拇指摆动
};
FingerControl fingerControl;

// ==========================================
// 工具函数
// ==========================================
float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// ==========================================
// 手指控制函数
// ==========================================
void setFinger(int id_left, int id_right, float inputBend, float inputYaw, bool isThumb) {
  inputBend = constrain(inputBend, IN_BEND_MIN, IN_BEND_MAX);
  inputYaw = constrain(inputYaw, IN_YAW_MIN, IN_YAW_MAX);

  float factorBend = mapFloat(inputBend, IN_BEND_MIN, IN_BEND_MAX, -1.0, 1.0);
  float factorYaw = mapFloat(inputYaw, IN_YAW_MIN, IN_YAW_MAX, -1.0, 1.0);

  float offsetBend = factorBend * BEND_STRENGTH;
  float offsetYaw = factorYaw * YAW_STRENGTH;

  int posLeft, posRight;
  if (isThumb) {
    posLeft = CENTER_POS - (int)offsetBend + (int)offsetYaw;
    posRight = CENTER_POS + (int)offsetBend + (int)offsetYaw;
  } else {
    posLeft = CENTER_POS + (int)offsetBend + (int)offsetYaw;
    posRight = CENTER_POS - (int)offsetBend + (int)offsetYaw;
  }

  posLeft = constrain(posLeft, 100, 900);
  posRight = constrain(posRight, 100, 900);

  sc.WritePos(id_left, posLeft, 0, 800);
  sc.WritePos(id_right, posRight, 0, 800);
}

void setFullHand(float bend, float yaw) {
  setFinger(11, 12, bend, yaw, true);  // 大拇指
  setFinger(13, 14, bend, yaw, false); // 食指
  setFinger(15, 16, bend, yaw, false); // 中指
  setFinger(17, 18, bend, yaw, false); // 无名指
}

// ==========================================
// 预设手势动作
// ==========================================
void makeFist() {
  setFullHand(160.0, 0.0);
}

void openHand() {
  setFullHand(20.0, 0.0);
}

void scissorsGesture() {
  setFullHand(20.0, 0.0);
  delay(100);
  setFinger(13, 14, 120.0, 0.0, false); // 食指
  setFinger(15, 16, 120.0, 0.0, false); // 中指
}

void rockGesture() {
  makeFist();
}

void paperGesture() {
  openHand();
}

void thumbsUp() {
  setFullHand(20.0, 0.0);
  delay(100);
  setFinger(11, 12, 140.0, 0.0, true); // 大拇指
}

void pointGesture() {
  setFullHand(20.0, 0.0);
  delay(100);
  setFinger(13, 14, 140.0, 0.0, false); // 食指
}

void okGesture() {
  setFullHand(20.0, 0.0);
  delay(100);
  setFinger(13, 14, 140.0, 0.0, false); // 食指
  setFinger(11, 12, 140.0, 0.0, true);  // 大拇指
}

// ==========================================
// 独立手指控制函数
// ==========================================
void setThumb(float bend, float yaw) {
  setFinger(11, 12, bend, yaw, true);
}

void setIndex(float bend, float yaw) {
  setFinger(13, 14, bend, yaw, false);
}

void setMiddle(float bend, float yaw) {
  setFinger(15, 16, bend, yaw, false);
}

void setRing(float bend, float yaw) {
  setFinger(17, 18, bend, yaw, false);
}

void setPinky(float bend, float yaw) {
  // 小指只有单电机控制，使用弯曲参数
  bend = constrain(bend, IN_BEND_MIN, IN_BEND_MAX);
  float factorBend = mapFloat(bend, IN_BEND_MIN, IN_BEND_MAX, -1.0, 1.0);
  float offsetBend = factorBend * BEND_STRENGTH;
  int pos = CENTER_POS + (int)offsetBend;
  pos = constrain(pos, 100, 900);
  // 注意：这里需要根据实际小指电机ID调整
  // sc.WritePos(19, pos, 0, 800);
}

// ==========================================
// HTML网页
// ==========================================
String getHTML() {
  String html = R"HTMLDELIMITER(
<!DOCTYPE html>
<html lang="en">
<head>
  <title>AmazingHand Control</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .container { max-width: 1200px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; }
    h1 { text-align: center; margin-bottom: 30px; font-size: 2.5em; }
    .finger-controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .finger-control { background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center; }
    .finger-control h3 { margin-top: 0; margin-bottom: 15px; font-size: 1.3em; color: #ffd700; }
    .finger-icon { font-size: 2.5em; margin-bottom: 10px; }
    .slider-group { margin: 15px 0; }
    .slider-group label { display: block; margin-bottom: 8px; font-weight: bold; font-size: 0.9em; }
    .slider-value { background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; margin-left: 5px; }
    input[type="range"] { width: 100%; height: 8px; border-radius: 5px; background: #ddd; outline: none; margin: 10px 0; -webkit-appearance: none; }
    input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #ffd700; cursor: pointer; }
    input[type="range"]::-moz-range-thumb { width: 20px; height: 20px; border-radius: 50%; background: #ffd700; cursor: pointer; border: none; }
    .apply-btn { width: 100%; padding: 10px; margin-top: 10px; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer; background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; transition: transform 0.1s; }
    .apply-btn:hover { transform: scale(1.05); }
    .apply-btn:active { transform: scale(0.95); }
    .preset-section { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .preset-section h3 { margin-top: 0; margin-bottom: 15px; color: #ffd700; text-align: center; }
    .preset-buttons { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }
    .preset-btn { padding: 12px; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer; background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; transition: transform 0.1s; }
    .preset-btn:hover { transform: scale(1.05); }
    .preset-btn:active { transform: scale(0.95); }
    .status { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center; font-size: 18px; }
    .status-emoji { font-size: 2em; margin-bottom: 10px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🤖 AmazingHand Finger Control</h1>

    <div class="finger-controls">
      <!-- Thumb -->
      <div class="finger-control">
        <div class="finger-icon">👍</div>
        <h3>Thumb</h3>
        <div class="slider-group">
          <label>Bend: <span class="slider-value" id="thumbBendValue">20</span></label>
          <input type="range" id="thumbBend" min="20" max="160" value="20" oninput="updateSlider('thumbBend')">
        </div>
        <div class="slider-group">
          <label>Yaw: <span class="slider-value" id="thumbYawValue">0</span></label>
          <input type="range" id="thumbYaw" min="-100" max="100" value="0" oninput="updateSlider('thumbYaw')">
        </div>
        <button class="apply-btn" onclick="applyFingerControl('thumb')">Apply Thumb</button>
      </div>

      <!-- Index Finger -->
      <div class="finger-control">
        <div class="finger-icon">☝️</div>
        <h3>Index Finger</h3>
        <div class="slider-group">
          <label>Bend: <span class="slider-value" id="indexBendValue">20</span></label>
          <input type="range" id="indexBend" min="20" max="160" value="20" oninput="updateSlider('indexBend')">
        </div>
        <div class="slider-group">
          <label>Yaw: <span class="slider-value" id="indexYawValue">0</span></label>
          <input type="range" id="indexYaw" min="-100" max="100" value="0" oninput="updateSlider('indexYaw')">
        </div>
        <button class="apply-btn" onclick="applyFingerControl('index')">Apply Index</button>
      </div>

      <!-- Middle Finger -->
      <div class="finger-control">
        <div class="finger-icon">🖕</div>
        <h3>Middle Finger</h3>
        <div class="slider-group">
          <label>Bend: <span class="slider-value" id="middleBendValue">20</span></label>
          <input type="range" id="middleBend" min="20" max="160" value="20" oninput="updateSlider('middleBend')">
        </div>
        <div class="slider-group">
          <label>Yaw: <span class="slider-value" id="middleYawValue">0</span></label>
          <input type="range" id="middleYaw" min="-100" max="100" value="0" oninput="updateSlider('middleYaw')">
        </div>
        <button class="apply-btn" onclick="applyFingerControl('middle')">Apply Middle</button>
      </div>

      <!-- Ring Finger -->
      <div class="finger-control">
        <div class="finger-icon">💍</div>
        <h3>Ring Finger</h3>
        <div class="slider-group">
          <label>Bend: <span class="slider-value" id="ringBendValue">20</span></label>
          <input type="range" id="ringBend" min="20" max="160" value="20" oninput="updateSlider('ringBend')">
        </div>
        <div class="slider-group">
          <label>Yaw: <span class="slider-value" id="ringYawValue">0</span></label>
          <input type="range" id="ringYaw" min="-100" max="100" value="0" oninput="updateSlider('ringYaw')">
        </div>
        <button class="apply-btn" onclick="applyFingerControl('ring')">Apply Ring</button>
      </div>

      <!-- Pinky Finger -->
      <div class="finger-control">
        <div class="finger-icon">🤟</div>
        <h3>Pinky Finger</h3>
        <div class="slider-group">
          <label>Bend: <span class="slider-value" id="pinkyBendValue">20</span></label>
          <input type="range" id="pinkyBend" min="20" max="160" value="20" oninput="updateSlider('pinkyBend')">
        </div>
        <button class="apply-btn" onclick="applyFingerControl('pinky')">Apply Pinky</button>
      </div>
    </div>

    <div class="preset-section">
      <h3>🎯 Quick Actions</h3>
      <div class="preset-buttons">
        <button class="preset-btn" onclick="sendAction('fist')">✊ Fist</button>
        <button class="preset-btn" onclick="sendAction('open')">✋ Open</button>
        <button class="preset-btn" onclick="sendAction('scissors')">✌️ Scissors</button>
        <button class="preset-btn" onclick="sendAction('thumbsup')">👍 Thumbs Up</button>
        <button class="preset-btn" onclick="sendAction('point')">👉 Point</button>
        <button class="preset-btn" onclick="sendAction('ok')">👌 OK</button>
        <button class="preset-btn" onclick="resetAllFingers()">🔄 Reset All</button>
      </div>
    </div>

    <div class="status">
      <div class="status-emoji" id="statusEmoji">👋</div>
      <div id="statusText">Ready - Control each finger independently!</div>
    </div>
  </div>

  <script>
    function updateSlider(sliderId) {
      const slider = document.getElementById(sliderId);
      const valueSpan = document.getElementById(sliderId + 'Value');
      valueSpan.textContent = slider.value;
    }

    function applyFingerControl(finger) {
      const bend = parseFloat(document.getElementById(finger + 'Bend').value);
      const yaw = finger === 'pinky' ? 0 : parseFloat(document.getElementById(finger + 'Yaw').value);

      fetch('/finger', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          finger: finger,
          bend: bend,
          yaw: yaw
        })
      })
      .then(response => response.json())
      .then(data => {
        updateStatus(finger, data.message);
      })
      .catch(error => {
        console.error('Error:', error);
        updateStatus('error', 'Failed to control finger');
      });
    }

    function sendAction(action) {
      fetch('/action', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: action})
      })
      .then(response => response.json())
      .then(data => {
        updateStatus(data.status, data.message);
      });
    }

    function resetAllFingers() {
      const fingers = ['thumb', 'index', 'middle', 'ring', 'pinky'];
      fingers.forEach(finger => {
        document.getElementById(finger + 'Bend').value = 20;
        document.getElementById(finger + 'BendValue').textContent = '20';
        if (finger !== 'pinky') {
          document.getElementById(finger + 'Yaw').value = 0;
          document.getElementById(finger + 'YawValue').textContent = '0';
        }
        applyFingerControl(finger);
      });
    }

    function updateStatus(status, message) {
      const emoji = document.getElementById('statusEmoji');
      const text = document.getElementById('statusText');
      text.textContent = message;

      switch(status) {
        case 'thumb': emoji.textContent = '👍'; break;
        case 'index': emoji.textContent = '☝️'; break;
        case 'middle': emoji.textContent = '🖕'; break;
        case 'ring': emoji.textContent = '💍'; break;
        case 'pinky': emoji.textContent = '🤟'; break;
        case 'fist': emoji.textContent = '✊'; break;
        case 'open': emoji.textContent = '✋'; break;
        case 'scissors': emoji.textContent = '✌️'; break;
        case 'thumbsup': emoji.textContent = '👍'; break;
        case 'point': emoji.textContent = '👉'; break;
        case 'ok': emoji.textContent = '👌'; break;
        case 'error': emoji.textContent = '⚠️'; break;
        default: emoji.textContent = '👋';
      }
    }
  </script>
</body>
</html>
)HTMLDELIMITER";
  return html;
}

// ==========================================
// API路由处理
// ==========================================
void handleRoot() {
  server.sendHeader("Content-Type", "text/html; charset=UTF-8");
  server.send(200, "text/html", getHTML());
}

void handleAction() {
  server.sendHeader("Content-Type", "application/json; charset=UTF-8");
  String body = server.arg("plain");
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, body);

  if (error) {
    server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"JSON Parse Failed\"}");
    return;
  }

  String action = doc["action"];
  String message = "";

  if (action == "fist") {
    makeFist();
    message = "Fist action executing...";
  } else if (action == "open") {
    openHand();
    message = "Open action executing...";
  } else if (action == "scissors") {
    scissorsGesture();
    message = "Scissors action executing...";
  } else if (action == "thumbsup") {
    thumbsUp();
    message = "Thumbs up action executing...";
  } else if (action == "point") {
    pointGesture();
    message = "Point action executing...";
  } else if (action == "ok") {
    okGesture();
    message = "OK gesture executing...";
  } else {
    message = "Unknown action";
  }

  server.send(200, "application/json", "{\"status\":\"" + action + "\",\"message\":\"" + message + "\"}");
}

void handleControl() {
  server.sendHeader("Content-Type", "application/json; charset=UTF-8");
  String body = server.arg("plain");
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, body);

  if (error) {
    server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"JSON Parse Failed\"}");
    return;
  }

  float bend = doc["bend"];
  float yaw = doc["yaw"];

  setFullHand(bend, yaw);

  char message[100];
  sprintf(message, "Precise Control: Bend=%.1f, Yaw=%.1f", bend, yaw);

  server.send(200, "application/json", "{\"status\":\"control\",\"message\":\"" + String(message) + "\"}");
}

void handleFinger() {
  server.sendHeader("Content-Type", "application/json; charset=UTF-8");
  String body = server.arg("plain");
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, body);

  if (error) {
    server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"JSON Parse Failed\"}");
    return;
  }

  String finger = doc["finger"];
  float bend = doc["bend"];
  float yaw = doc["yaw"];

  String message = "";

  if (finger == "thumb") {
    setThumb(bend, yaw);
    message = "Thumb control: Bend=" + String(bend, 1) + ", Yaw=" + String(yaw, 1);
  } else if (finger == "index") {
    setIndex(bend, yaw);
    message = "Index finger control: Bend=" + String(bend, 1) + ", Yaw=" + String(yaw, 1);
  } else if (finger == "middle") {
    setMiddle(bend, yaw);
    message = "Middle finger control: Bend=" + String(bend, 1) + ", Yaw=" + String(yaw, 1);
  } else if (finger == "ring") {
    setRing(bend, yaw);
    message = "Ring finger control: Bend=" + String(bend, 1) + ", Yaw=" + String(yaw, 1);
  } else if (finger == "pinky") {
    setPinky(bend, yaw);
    message = "Pinky finger control: Bend=" + String(bend, 1);
  } else {
    message = "Unknown finger: " + finger;
  }

  server.send(200, "application/json", "{\"status\":\"" + finger + "\",\"message\":\"" + message + "\"}");
}

void handleStatus() {
  server.sendHeader("Content-Type", "application/json; charset=UTF-8");
  StaticJsonDocument<100> doc;
  doc["connected"] = true;
  doc["uptime"] = millis();

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

// ==========================================
// 初始化和主循环
// ==========================================
void setup() {
  Serial.begin(115200);
  Serial1.begin(1000000, SERIAL_8N1, SERVO_RX_PIN, SERVO_TX_PIN);
  sc.pSerial = &Serial1;
  delay(1000);

  // 初始化WiFi AP模式
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();

  Serial.print("WiFi AP Started: ");
  Serial.println(ssid);
  Serial.print("IP Address: ");
  Serial.println(IP);
  Serial.println("Please visit this address in browser");

  // 初始化Web服务器
  server.on("/", HTTP_GET, handleRoot);
  server.on("/action", HTTP_POST, handleAction);
  server.on("/control", HTTP_POST, handleControl);
  server.on("/finger", HTTP_POST, handleFinger);
  server.on("/status", HTTP_GET, handleStatus);

  server.begin();
  Serial.println("Web Server Started");

  // 开启所有电机扭矩
  for (int i = 11; i <= 18; i++) {
    sc.EnableTorque(i, 1);
    delay(20);
  }
  delay(500);

  Serial.println("==========================");
  Serial.println("AmazingHand WiFi Control");
  Serial.println("==========================");

  // 初始化：张开手势
  openHand();
  delay(2000);
}

void loop() {
  server.handleClient();
  delay(10);
}