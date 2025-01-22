// Include the required Arduino libraries:
#include "OneWire.h"
#include "DallasTemperature.h"

// Define to which pin of the Arduino the 1-Wire bus is connected:
#define ONE_WIRE_BUS 2

// Define pins for the HC-SR04 ultrasonic sensor:
#define TRIG_PIN 3
#define ECHO_PIN 4

// Define the analog pin for the TDS sensor:
#define TDS_SENSOR_PIN A0

// Define constants for the TDS sensor:
#define VREF 5.0        // Reference voltage (5V for Arduino Uno)
#define ADC_RES 1024    // ADC resolution (10-bit ADC -> 1024)
#define TDS_FACTOR 0.5  // TDS factor for converting voltage to ppm

// Define pin for the flow sensor:
#define FLOW_SENSOR_PIN 5  // Flow sensor connected to digital pin 5

// Create a new instance of the oneWire class to communicate with any OneWire device:
OneWire oneWire(ONE_WIRE_BUS);

// Pass the oneWire reference to DallasTemperature library:
DallasTemperature sensors(&oneWire);

// Flow sensor variables
volatile int flowPulseCount = 0; // Variable to count flow sensor pulses
float flowRate = 0.0;            // Flow rate in liters per minute

// Flow sensor interrupt function to count pulses
void flowSensorInterrupt() {
  flowPulseCount++;  // Increment pulse count on each interrupt
}

void setup() {
  // Begin serial communication at a baud rate of 9600:
  Serial.begin(9600);

  // Start up the DS18B20 temperature sensor library:
  sensors.begin();

  // Set the ultrasonic sensor pins:
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Set up the flow sensor pin as an input and attach the interrupt:
  pinMode(FLOW_SENSOR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), flowSensorInterrupt, RISING);

  // Print header:
  Serial.println("Time (s) | Temperature (C) | Temperature (F) | Distance (cm) | TDS (ppm) | Flow Rate (L/min)");
}

void loop() {
  // Measure elapsed time:
  unsigned long elapsedTime = millis() / 1000;

  // Send the command for all devices on the bus to perform a temperature conversion:
  sensors.requestTemperatures();

  // Fetch the temperature in degrees Celsius and Fahrenheit:
  float tempC = sensors.getTempCByIndex(0); // index 0 refers to the first device
  float tempF = sensors.getTempFByIndex(0);

  // Trigger the ultrasonic sensor:
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Read the echo pin and calculate the distance in cm:
  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.034 / 2; // Convert duration to cm

  // Read analog value from the TDS sensor:
  int tdsAnalogValue = analogRead(TDS_SENSOR_PIN);

  // Convert the analog reading to voltage:
  float tdsVoltage = (tdsAnalogValue / (float)ADC_RES) * VREF;

  // Calculate TDS value in ppm:
  float tdsValue = (tdsVoltage * TDS_FACTOR) * 1000; // Convert to ppm

  // Calculate flow rate (in liters per minute):
  flowRate = (flowPulseCount / 21);  // Typically, 21 pulses = 1 liter of water
  flowPulseCount = 0;  // Reset pulse count for the next cycle

  // Print the results in the Serial Monitor:
  Serial.print("Time: ");
  Serial.print(elapsedTime);
  Serial.print(" s | ");
  Serial.print(tempC);
  Serial.print(" \xC2\xB0 | ");
  Serial.print(tempF);
  Serial.print(" \xC2\xB0 | ");
  Serial.print(distance);
  Serial.print(" cm | ");
  Serial.print(tdsValue);
  Serial.print(" ppm | ");
  Serial.print(flowRate);
  Serial.println(" L/min");

  // Wait 1 second:
  delay(1000);
}
