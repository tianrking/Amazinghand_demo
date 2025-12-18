#include <SCServo.h>

SCSCL sc;

// 定义使用的引脚
#define SERVO_TX_PIN D9   // GPIO9 作为 TX
#define SERVO_RX_PIN D10  // GPIO10 作为 RX

void setup()
{
  // 增加初始延时，等待系统稳定
  delay(2000);

  Serial.begin(115200);
  delay(500); // 等待串口初始化

  Serial.println();
  Serial.println("========================");
  Serial.println("XIAO ESP32C3 - SCServo Ping Test");
  Serial.println("========================");
  Serial.print("TX Pin: D9 (GPIO");
  Serial.print(SERVO_TX_PIN);
  Serial.print("), RX Pin: D10 (GPIO");
  Serial.println(SERVO_RX_PIN);

  // 等待更长时间再初始化UART1
  delay(1000);

  // 初始化UART1用于舵机控制，使用指定的引脚
  Serial.println("Initializing UART1...");
  Serial1.begin(1000000, SERIAL_8N1, SERVO_RX_PIN, SERVO_TX_PIN);
  delay(1000); // 等待UART1稳定

  Serial.println("UART1 initialized at 1000000 baud");

  // 设置SCServo串口
  sc.pSerial = &Serial1;
  delay(1000);

  Serial.println("SCServo configured");
  Serial.println();
}

void loop()
{
  Serial.println();
  Serial.println("========================");
  Serial.println("Scanning servo IDs 1-20...");
  Serial.println("========================");

  int foundCount = 0;

  // 扫描所有ID
  for(int testID = 1; testID <= 20; testID++){
    Serial.print("Pinging ID ");
    if(testID < 10) Serial.print(" "); // 对齐
    Serial.print(testID);
    Serial.print(": ");

    int testResult = sc.Ping(testID);
    if(testResult != -1){
      Serial.print("FOUND! - ID: ");
      Serial.print(testResult);

      // 尝试读取更多信息
      int voltage = sc.ReadVoltage(testResult);
      Serial.print(", Voltage: ");
      Serial.print(voltage);
      Serial.print("mV");

      int pos = sc.ReadPos(testResult);
      Serial.print(", Position: ");
      Serial.println(pos);

      foundCount++;
    } else {
      Serial.println("No response");
    }
    delay(50); // 短延时
  }

  Serial.println("========================");
  Serial.print("Scan complete. Found ");
  Serial.print(foundCount);
  Serial.println(" servo(s)");
  Serial.println("========================");
  Serial.println();

  // 等待10秒再重新扫描
  Serial.println("Waiting 10 seconds before next scan...");
  delay(10000);
}