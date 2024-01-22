// blinker.ino
// Simple program to let a to the esp32 connected led blink in the specified frequency

// Define the LED pin
const int ledPin = 2;

// Delay between of and on cyle: 
const int delayTime = 1000 / 70 / 2; // 1000 ms divided by frequency and then divided by 2

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  digitalWrite(ledPin, HIGH);

  delay(delayTime);

  digitalWrite(ledPin, LOW);

  delay(delayTime);
}
