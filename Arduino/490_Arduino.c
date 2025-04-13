//490 Report Arduino Code
#include <Wire.h>
#include "Adafruit_AS726x.h"

#define trigPin 2
#define echoPin 3
#define MixerFan 4  //blue
#define MixerPump 5 //white
#define NozzlePump 6 // red
#define Paraseltic 7  // green
#define DemoPin 8
#define test1 11
#define test2 12

#define Turbidity A0
#define temp A1
#define pHSense A2
#define TdsSensorPin A7
#define ADC_Diode A6

#define VREF 5.0
#define SCOUNT 30

int samples = 10;
float adc_resolution = 1024.0;
int analogBuffer[SCOUNT];
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0, copyIndex = 0;
float averageVoltage = 0, tdsValue = 0, temperature = 25;

static unsigned long sensorSampleTimepoint = millis();
const int interval = 500;
static int sensorStep = 0;

unsigned long sprayTime = 0;
unsigned long lastSprayTime = 0;
unsigned long mixTime = 0;
bool spraying = false;
bool mixing = false;

const unsigned long SPRAY_DURATION = 5000;        // 5 seconds spray time
const unsigned long SPRAY_COOLDOWN = 5 * 60000;   // 5 minutes cooldown


const float ADC_REF_V = 5.0;
const float Feedback_R = 1000000.0;
const float UV_PPFD = 0.002;
float Reflective_Sens;

Adafruit_AS726x ams;
float calibratedValues[AS726x_NUM_CHANNELS];
float wavelengths[AS726x_NUM_CHANNELS] = {450, 500, 550, 570, 600, 650};

// Sensor Data Storage
float last_pH_value = 0;
int last_distance = 0;

void setup() {
  Serial.begin(9600);
  delay(100);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(TdsSensorPin, INPUT);
  pinMode(NozzlePump, OUTPUT);
  pinMode(MixerFan, OUTPUT);
  pinMode(Paraseltic, OUTPUT);
  pinMode(MixerPump, OUTPUT);
  pinMode(DemoPin, INPUT);

  pinMode(test1, OUTPUT);
  pinMode(test2, OUTPUT);

  digitalWrite(NozzlePump, HIGH);
  digitalWrite(NozzlePump, HIGH);
  digitalWrite(MixerFan, HIGH);
  digitalWrite(Paraseltic, HIGH);

  if (!ams.begin()) {
   Serial.println("Could not connect to AS726x sensor! Check wiring.");
    while (1);
  }
}

float ph(float voltage) {
  return 7 + ((2.5 - voltage) / 0.18);
}

float readDLI() {
  uint8_t temp = ams.readTemperature();
  ams.startMeasurement();

  while (!ams.dataReady()) {
    delay(5);
  }

  ams.readCalibratedValues(calibratedValues);

  float sum = 0;
  float Final_Intensity = 0;
  for (int i = 0; i < AS726x_NUM_CHANNELS; i++) {
    sum += calibratedValues[i] * wavelengths[i];
    Final_Intensity += calibratedValues[i];
  }

  int wav = (Final_Intensity > 0) ? sum / Final_Intensity : 0;
  Reflective_Sens = Sens(wav);
  float photocurrent_micro = PhotocurrentCalc();
  float photoperiod = photoperiodCalc(photocurrent_micro);
  float PAR;
  float Lux = LuxPARCalc(photocurrent_micro, PAR);
  float DLI = DLICalc(Lux, photoperiod);
  Serial.println(DLI);
  return DLI;
}

float PhotocurrentCalc() {
  int ADC_Input = analogRead(ADC_Diode);
  float ADC_to_Voltage = (ADC_Input / 1023.0) * ADC_REF_V;
  return (ADC_to_Voltage / Feedback_R) * 1e6;
}

float Sens(int wav) {
  if (wav >= 400 && wav <= 499) return 0.05e-5;
  if (wav >= 500 && wav <= 599) return 0.2e-5;
  if (wav >= 600 && wav <= 699) return 0.35e-5;
  if (wav >= 700 && wav <= 750) return 0.45e-5;
  return 0.0;
}

float photoperiodCalc(float photocurrent_micro) {
  static unsigned long last_time = 0;
  static float accumulated_time = 0.0;
  static bool in_range = false;
  unsigned long current_time = millis();

  if (in_range) {
    accumulated_time += (current_time - last_time) / 60000.0;
  }
  last_time = current_time;
  return accumulated_time / 60.0;
}

float LuxPARCalc(float photocurrent_micro, float &PAR) {
  float Lux = (photocurrent_micro / Reflective_Sens);
  PAR = Lux * UV_PPFD;
  return Lux;
}

float DLICalc(float Lux, float photoperiod) {
  return Lux * UV_PPFD * 60 * 60 * photoperiod / 1000000;
}

void loop() {
  // Run normal operations as long as demo pin is LOW
  while (digitalRead(DemoPin) == LOW) {
    digitalWrite(test1, LOW);

    delay(50); // Small debounce delay
    // Normal sensor sampling logic
    if (millis() - sensorSampleTimepoint > interval) {
      sensorSampleTimepoint = millis();
      
      switch (sensorStep) {
        case 0:
          readTurbidity();
          break;
        case 1:
          readTDS();
          break;
        case 2:
          readUltrasonic();
          break;
        case 3:
          readPH();
          Serial.println();
          break;
        case 4:
          readDLI();
          break;
      }
      
      sensorStep++;
      if (sensorStep > 4) {
        sensorStep = 0;
        check_sensor_conditions();
      }
    }

    manage_spraying();
    manage_mixing();
    digitalWrite(test1, HIGH);
  }
  
  digitalWrite(test2, LOW);
  demo_mode();
  digitalWrite(test2, HIGH);
 
}

void check_sensor_conditions() {
  unsigned long currentTime = millis();
  
  if (!spraying && (currentTime - lastSprayTime >= SPRAY_COOLDOWN)) {
    if (sensor_check(last_pH_value, last_distance)) {
      Serial.println("Conditions met, initiating spray!");
      digitalWrite(NozzlePump, LOW);
      sprayTime = millis();
      spraying = true;
    } else {
      Serial.println("Conditions not met, initiating mixing.");
      digitalWrite(MixerFan, LOW);
      mixTime = millis();
      mixing = true;
    }
  }
}

void manage_spraying() {
  if (spraying && (millis() - sprayTime >= SPRAY_DURATION)) {
    digitalWrite(NozzlePump, HIGH);
    lastSprayTime = millis();
    spraying = false;
    Serial.println("Spray cycle complete.");
  }
}

void manage_mixing() {
  if (mixing && (millis() - mixTime >= 1500)) {
    digitalWrite(MixerFan, LOW);
    digitalWrite(Paraseltic, LOW);
    delay(200);
    digitalWrite(MixerFan, HIGH);
    digitalWrite(Paraseltic, HIGH);
    mixing = false;
    Serial.println("Mixing cycle complete.");
  }
}

void readTurbidity() {
  int sensorValue = analogRead(Turbidity);
  float voltage = sensorValue * (5.0 / 1024.0);
  
  Serial.print(voltage);
  Serial.print(",");
}

void readTDS() {
  analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);
  analogBufferIndex++;
  if (analogBufferIndex == SCOUNT) analogBufferIndex = 0;

  for (copyIndex = 0; copyIndex < SCOUNT; copyIndex++)
    analogBufferTemp[copyIndex] = analogBuffer[copyIndex];

  averageVoltage = getMedianNum(analogBufferTemp, SCOUNT) * (float)VREF / 1024.0;
  float compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0);
  float compensationVoltage = averageVoltage / compensationCoefficient;
  tdsValue = (133.42 * compensationVoltage * compensationVoltage * compensationVoltage -
              255.86 * compensationVoltage * compensationVoltage +
              857.39 * compensationVoltage) * 0.5;
              
  Serial.print(tdsValue);
  Serial.print(",");
}

void readUltrasonic() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  int duration = pulseIn(echoPin, HIGH);
  last_distance = (duration / 2) / 29.1;
  
  Serial.print(last_distance);
  Serial.print (",");
}

void readPH() {
  int measurings = 0;
  for (int i = 0; i < samples; i++) {
    measurings += analogRead(pHSense);
    delay(10);
  }
  
  float voltage = 5.0 / adc_resolution * measurings / samples;
  last_pH_value = ph(voltage);
  
  Serial.print(last_pH_value);
  Serial.print (",");
}

//example conditions, we can include more
bool sensor_check(float pH_value, int distance) {
  return (pH_value > 6.0 && pH_value < 7.0 && distance > 100);

}
//collapsed for the report
void demo_mode() {
  Serial.println("Demo mode activated: All pumps ON!");
  //low = on
  
  digitalWrite(MixerFan, HIGH);
  digitalWrite(Paraseltic, HIGH);
  digitalWrite(NozzlePump, HIGH);
  digitalWrite(MixerPump, HIGH);
  
  delay(2000);

  digitalWrite(MixerPump, LOW);
  delay(2000);

  digitalWrite(MixerFan, LOW);
  delay(5000);
  digitalWrite(MixerFan, HIGH);
  delay(200);

  digitalWrite(Paraseltic, LOW);
  delay(5000);
  digitalWrite(Paraseltic, HIGH);
  delay(200);

  digitalWrite(NozzlePump, LOW);
  delay(10000);
  digitalWrite(NozzlePump, HIGH);
  delay(200);

  digitalWrite(MixerPump, HIGH);
  delay(200);
  
}
//median value filter 
int getMedianNum(int bArray[], int iFilterLen) {
  int bTab[iFilterLen];
  for (byte i = 0; i < iFilterLen; i++)
    bTab[i] = bArray[i];
  
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  
  if ((iFilterLen & 1) > 0)
    bTemp = bTab[(iFilterLen - 1) / 2];
  else
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  
  return bTemp;
}