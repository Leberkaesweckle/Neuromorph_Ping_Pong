// Program for letting two led blink in a specified frequency
// The pins and frequency of each led can be set indivudally


const int ledPin1 = 13;
const int ledPin2 = 15; 
const long frequency1 = 50;
const long frequency2 = 100;

const long interval1 = (1.0 / frequency1) * 1000 / 2;
const long interval2 = (1.0 / frequency2) * 1000 / 2;

bool ledState1 = LOW;
bool ledState2 = LOW;

unsigned long previousMillis1 = 0; 
unsigned long previousMillis2 = 0;

void setup() {
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
}

void loop() {
  unsigned long currentMillis = millis();

  // Update LED 1
  if (currentMillis - previousMillis1 >= interval1) {
    previousMillis1 = currentMillis;
    ledState1 = !ledState1;
    digitalWrite(ledPin1, ledState1);
  }
  

  // Update LED 2
  if (currentMillis - previousMillis2 >= interval2) {
    previousMillis2 = currentMillis;
    ledState2 = !ledState2;
    digitalWrite(ledPin2, ledState2);
  }
}
