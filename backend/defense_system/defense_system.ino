#define SENSOR_PIN A0  // Sensor

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

bool running = true;

void loop() {

  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Command to toggle houselight
    if (command == 'start') { 
      running = true; // toggle pixOn bool
    } else if (command = 'stop') {
      running = false;
    }
  }

  // If python script is running, send vibration sensor data
  if (running) {
    // put your main code here, to run repeatedly:
    int sensorValue = analogRead(SENSOR_PIN);  // Read the analog input (0-1023)
    Serial.println(sensorValue);              // Print the value to the Serial Monitor
    delay(50);                                // Measure 20 times per second
  }
}
