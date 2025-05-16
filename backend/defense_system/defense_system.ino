#define SENSOR_PIN A0  // Sensor

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

running = false;

void loop() {

  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Command to toggle houselight
    if (command == 's') { 
      running = !running; // toggle pixOn bool
      if (running) {
        // put your main code here, to run repeatedly:
        int sensorValue = analogRead(analogPin);  // Read the analog input (0-1023)
        Serial.println(sensorValue);              // Print the value to the Serial Monitor
        delay(50);                                // Measure 20 times per second
      }
    }
  }
}
