// Include the required Arduino libraries:
#include "OneWire.h"
#include "DallasTemperature.h"
#include <PID_v1.h>

// Define the 1-Wire bus pin for temperature sensor:
#define ONE_WIRE_BUS 8

// Define pins for the HC-SR04 ultrasonic sensor:
#define TRIG_PIN 13
#define ECHO_PIN 12

// Define the analog pin for the TDS sensor:
#define TDS_SENSOR_PIN A0

// Define constants for the TDS sensor:
#define VREF 5.0        // Reference voltage
#define ADC_RES 1024    // ADC resolution
#define TDS_FACTOR 0.5  // TDS factor

// Define pin for the flow sensor:
#define FLOW_1_PIN 2  // Flow sensor connected to digital pin 5
#define FLOW_2_PIN 3

// Define pin for the pump:
#define PUMP_1_PIN 5
#define PUMP_2_PIN 6

#define PELTIER_HOT_PIN 10
#define PELTIER_COLD_PIN 11

// Will average over this many measurements for the flow sensor
// #define DISTANCE_WINDOW 100
const float DISTANCE_M = -0.787714755;
const float DISTANCE_B = 9.955578414;

const float FLOW_M = 5.35391e-5;
// const float FLOW_B = 0.003459284;

// OneWire setup
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Flow sensor variables
volatile int flowPulseCount1 = 0;
volatile int flowPulseCount2 = 0;
// we use a uint for modular arithmetic to always give the right time interval
unsigned long last_time;

// we'll need to keep P global
float P[2][2] = {{0,0},{0,0}};

// start with nothing in the tank, and nothing being added
float x[2] = {0,0};

// the constant rate of evaporation, estimated
const float w_dt = -1.653e-6;

// the variation in the rate of evaporation;
// multiplying this by dt gives the uncertainty (variance) in the change in volume in this cycle
const float Q_11_dt = 4.52e-18;

// when pumping, our pump rate has a variance of 7.3e-5 L/s
const float Q_22 = 7.3358e-5;

// // The MSE of the ultrasonic sensor is 0.35 L
// const float R_1 = 0.35;
// // from O42 in Test 4 True Measurements
// const float R_2 = 3.42e-7;  
// from more recent calculations, we should actually have R[0] = 0.036
// const float R_diag[2] = {0.35, 3.42e-7};
const float R_diag[2] = {0.05, 3.42e-7};

// pump rate is in milliseconds/L
const float PUMP_RATE = 50382.28019;

// order is: (water pump, nut pump)
// unsigned long pumpTimes[2];
// unsigned long pumpStartTimes[2] = {0,0};
float toPump[2] = {0, 0};
int pulsesThisCycle[2] = {0,0};

// define the PID controller
// PID Parameters
double Setpoint, Input, Output;
double Kp = 2.0, Ki = 5.0, Kd = 1.0; // Tune these values
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

void iterateKalman(float z[2], float x[2], float P[2][2], float w, float Q_diag[2], float R_diag[2], float dt) {
  // note that the Q and R are just diagonal because we assume no process or measurement noise covariance
  // w is just the rate of evaporation
  // dt is the time step
  
  // define F
  float F[2][2] = {
    {1, dt},
    {0, 1}
  };

  float x_priori[2];

  // x_priori = Fx + w
  // a priori estimate has \dot{V} stay the same, but the total volume is incremented by both the flow rate and the evaporation
  x_priori[1] = x[1];
  x_priori[0] = x[0] + x[1]*dt + w*dt;

  // generate the a priori P matrix
  float P_priori[2][2] = {
    {0,0},
    {0,0}
  };

  for (int i =0; i < 2; ++i) {
    for (int j = 0; j < 2; ++j) {
      for (int k = 0; k < 2; ++k) {
        for (int l = 0; l < 2; ++l) {
          P_priori[i][j] += F[i][k]*P[k][l]*F[j][l];
        }
      }
      // P_priori[i][j] += Q[i][j];
    }
    P_priori[i][i] += Q_diag[i];
  }

 
  
  // compute innovation covariance
  float S[2][2];

  for (int i = 0; i < 2; ++i) {
    for (int j = 0; j < 2; ++j) {
      // S[i][j] = P_priori[i][j] + R[i][j];
      S[i][j] = P_priori[i][j];
    }
    S[i][i] += R_diag[i];
  }
  float det = S[0][0]*S[1][1] - S[0][1]*S[1][0];

  float S_inv[2][2] = {
    {S[1][1]/det, -S[0][1]/det},
    {-S[1][0]/det, S[0][0]/det}
  };
  
  // calculate Kalman gain
  float K[2][2] = {
    {0,0},
    {0,0}
  };
  for (int i = 0; i < 2; ++i) {
    for (int j = 0; j < 2; ++j) {
      for (int k = 0; k < 2; ++k) {
        K[i][j] += P_priori[i][k]*S_inv[k][j];
      }
    }
  }

  // compute posterior x, and use it to override the old x
  for (int i = 0; i < 2; ++i) {
    for (int k = 0; k < 2; ++k) {
      x[i] = x_priori[i] + K[i][k]*(z[k] - x_priori[k]);
    }
  }

  // compute posterior P, and use it to override the old P
  for (int i = 0; i < 2; ++i) {
    for (int j = 0; j < 2; ++j) {
      P[i][j] = P_priori[i][j];
      for (int k = 0; k < 2; ++k) {
        P[i][j] -= K[i][k]*P[k][j];
      }
    }
  }
}

void flowSensorInterrupt1() {
  flowPulseCount1++;
}
void flowSensorInterrupt2() {
  flowPulseCount2++;
}

void setup() {
  Serial.begin(9600);
  sensors.begin();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(FLOW_1_PIN, INPUT_PULLUP); // Use pull-up if needed
  pinMode(FLOW_2_PIN, INPUT_PULLUP); // Use pull-up if needed
  attachInterrupt(digitalPinToInterrupt(FLOW_1_PIN), flowSensorInterrupt1, FALLING);
  attachInterrupt(digitalPinToInterrupt(FLOW_2_PIN), flowSensorInterrupt2, FALLING);

  pinMode(PUMP_1_PIN, OUTPUT);

  // set the temperature setpoint
  Setpoint = 21.0; // Target temperature in Celsius
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(-255, 255); // Range from full cooling (-255) to full heating (255)

  // debugging--check for temperature sensor
  if (sensors.getDeviceCount() == 0) {
    Serial.println("ERROR: No DS18B20 sensor found!");
  } else {
    Serial.print("Sensor found: ");
    Serial.println(sensors.getDeviceCount());
  }

  Serial.println("Temp (C) | Volume (L) | TDS (ppm)");
}

void loop() {
  // put your main code here, to run repeatedly:
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

  // tds sensor
  int tdsAnalogValue = analogRead(TDS_SENSOR_PIN);
  float tdsVoltage = (tdsAnalogValue / (float)ADC_RES) * VREF;
  float tdsValue = (tdsVoltage * TDS_FACTOR) * 1000;

  // flow sensors
  noInterrupts(); // Disable interrupts while reading the count
  int pulses1 = flowPulseCount1;
  int pulses2 = flowPulseCount2;
  pulsesThisCycle[0] += pulses1;
  pulsesThisCycle[1] += pulses2;
  flowPulseCount1 = 0;
  flowPulseCount2 = 0;
  interrupts(); // Enable interrupts again

  // define the stuff for Kalman filter
  // this is modular arithmetic, handling millis() wraparound
  unsigned long dt_millis = millis() - last_time;
  last_time = millis();
  // now we want to make a convenient float
  float dt = dt_millis/1000.0;
  // the thing to hold our estimates from our measurements
  float z[2];

  z[0] = distance*DISTANCE_M + DISTANCE_B;
  z[1] = (pulses1 + pulses2)*FLOW_M/dt;

  // if our pump reads zero, nothing is pumping and we should make R_diag[1][1] = 0
  // and also Q_22 = 0
  float Q_diag[2];
  Q_diag[0] = Q_11_dt*dt;
  if (pulses1 == 0 && pulses2 == 0) {
    Q_diag[1] = 0;
  } else {
    Q_diag[1] = Q_22;
  }

  // for now, make R_diag always the same since the flow rate R is already really small
  iterateKalman(z, x, P, w_dt, Q_diag, R_diag, dt);

  // handle incoming commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read incoming string
    command.trim(); // Remove any extra whitespace

    // if (command == "START PUMPING") {
    //     digitalWrite(PUMP_1_PIN, HIGH); // Turn pump on
    //     // Serial.println("Pump started");
    if (command.startsWith("PUMP_WATER") && toPump[0] == 0) {
      String valueStr = command.substring(command.indexOf(" "));
      valueStr.trim();
      // pumpTimes[0] = PUMP_RATE*valueStr.toFloat();
      // pumpStartTimes[0] = millis();
      toPump[0] = valueStr.toFloat();
      digitalWrite(PUMP_1_PIN, HIGH);
    } else if (command.startsWith("PUMP_NUTRIENTS") && toPump[1] == 0) {
      String valueStr = command.substring(command.indexOf(" "));
      valueStr.trim();
      // pumpTimes[1] = PUMP_RATE*valueStr.toFloat();
      // pumpStartTimes[1] = millis();
      // digitalWrite(PUMP_2_PIN, HIGH);
      toPump[1] = valueStr.toFloat();
    } else if (command == "STOP PUMPING") {
        digitalWrite(PUMP_1_PIN, LOW); // Turn pump off
        digitalWrite(PUMP_2_PIN, LOW); // Turn pump off
        // Serial.println("Pump stopped");
    } else if (command.startsWith("HEAT")) {
      String valueStr = command.substring(command.indexOf(" "));
      valueStr.trim();
      analogWrite(PELTIER_HOT_PIN, valueStr.toInt());
    // } else if (command == "HEAT") {
    //   analogWrite(PELTIER_HOT, 255);
    } else if (command == "STOP HEATING") {
      analogWrite(PELTIER_HOT_PIN, 0);
    } else if (command.startsWith("TEMP_SETPOINT_C")) {
      String valueStr = command.substring(command.indexOf(" "));
      valueStr.trim();
      Setpoint = valueStr.toFloat();
    }
  }

  // handle the pump times--turn the pumps off if necessary =========
  if (pulsesThisCycle[0]*FLOW_M >= toPump[0]) {
    digitalWrite(PUMP_1_PIN, LOW);
    // perhaps report the amount pumped?
    pulsesThisCycle[0] = 0;
    toPump[0] = 0;
  }
  if (pulsesThisCycle[1]*FLOW_M >= toPump[1]) {
    digitalWrite(PUMP_2_PIN, LOW);
    // perhaps report the amount pumped?
    pulsesThisCycle[1] = 0;
    toPump[1] = 0;
  }

  // Handle heating and cooling  =====================================
  Input = tempC;  
  myPID.Compute();

  // Control Heating and Cooling with a Dead Zone
  if (Output > 10) {  // Heating needed
      analogWrite(PELTIER_HOT_PIN, Output);
      analogWrite(PELTIER_COLD_PIN, 0);
  } 
  else if (Output < -10) {  // Cooling needed
      analogWrite(PELTIER_HOT_PIN, 0);
      analogWrite(PELTIER_COLD_PIN, abs(Output));
  } 
  else { // Dead zone to prevent oscillation
      analogWrite(PELTIER_HOT_PIN, 0);
      analogWrite(PELTIER_COLD_PIN, 0);
  }

  // print outputs
  // Serial.print(tempC);
  // Serial.print(" °C | ");
  // Serial.print(x[0]);
  // Serial.print(" L | ");
  // Serial.print(tdsValue);
  // Serial.println(" ppm | ");
  Serial.print(dt);
  Serial.print(", ");
  Serial.print(pulses1);
  Serial.print(", ");
  Serial.print(pulses2);
  Serial.print(", ");
  Serial.print(distance);
  Serial.print(", ");
  Serial.print(tempC);
  Serial.print(", ");
  Serial.println(tdsValue);

  

}
