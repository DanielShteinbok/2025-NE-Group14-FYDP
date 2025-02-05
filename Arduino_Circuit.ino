// Include the required Arduino libraries:
#include "OneWire.h"
#include "DallasTemperature.h"

// Define the 1-Wire bus pin for temperature sensor:
#define ONE_WIRE_BUS 5

// Define pins for the HC-SR04 ultrasonic sensor:
#define TRIG_PIN 3
#define ECHO_PIN 4

// Define the analog pin for the TDS sensor:
#define TDS_SENSOR_PIN A0

// Define constants for the TDS sensor:
#define VREF 5.0        // Reference voltage
#define ADC_RES 1024    // ADC resolution
#define TDS_FACTOR 0.5  // TDS factor

// Define pin for the flow sensor:
#define FLOW_SENSOR_PIN 2  // Flow sensor connected to digital pin 5

// Define pin for the pump:
#define PUMP_PIN 11

// Default pump duration
int pumpDuration = 0;

// OneWire setup
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Flow sensor variables
volatile int flowPulseCount = 0;
float flowRate = 0.0;

// Flow sensor interrupt function
void flowSensorInterrupt() {
  flowPulseCount++;
}

void setup() {
  Serial.begin(9600);
  sensors.begin();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP); // Use pull-up if needed
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), flowSensorInterrupt, FALLING);

  pinMode(PUMP_PIN, OUTPUT);

  Serial.println("Time (s) | Temp (C) | Temp (F) | Distance (cm) | TDS (ppm) | Flow Rate (L/min)");
}

void loop() {
  unsigned long elapsedTime = millis() / 1000;

  // Read temperature sensor
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  float tempF = sensors.getTempFByIndex(0);

  // Ultrasonic sensor
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.034 / 2;

  // Read TDS sensor
  int tdsAnalogValue = analogRead(TDS_SENSOR_PIN);
  float tdsVoltage = (tdsAnalogValue / (float)ADC_RES) * VREF;
  float tdsValue = (tdsVoltage * TDS_FACTOR) * 1000;

  // Calculate flow rate
  noInterrupts(); // Disable interrupts while reading the count
  int pulses = flowPulseCount;
  flowPulseCount = 0;
  interrupts(); // Enable interrupts again

  flowRate = (pulses / 21.0) * 60;  // Corrected formula

  Serial.print("Time: ");
  Serial.print(elapsedTime);
  Serial.print(" s | ");
  Serial.print(tempC);
  Serial.print(" °C | ");
  Serial.print(tempF);
  Serial.print(" °F | ");
  Serial.print(distance);
  Serial.print(" cm | ");
  Serial.print(tdsValue);
  Serial.print(" ppm | ");
  Serial.print(flowRate);
  Serial.println(" L/min");

  // Read pump duration command
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    pumpDuration = command.toInt();
    if (pumpDuration > 0) {
      Serial.print("Pump duration: ");
      Serial.print(pumpDuration);
      Serial.println(" ms");
    }
  }

  // Activate pump if needed
  if (pumpDuration > 0) {
    digitalWrite(PUMP_PIN, HIGH);
    delay(pumpDuration);
    digitalWrite(PUMP_PIN, LOW);
    pumpDuration = 0; // Reset pump duration after activation
  }

  delay(1000);
}
