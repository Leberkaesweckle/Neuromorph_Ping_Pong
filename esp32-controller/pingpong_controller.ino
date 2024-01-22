// Program for controlling 6 LEDs connected to GPIO pins

// led1 and led2s freequency can be set individually so they can be distinguished later
// led3 through led6 each have their own pin but share the same frequency.
// These leds are connected to the each of the playing field / display for tracking 

// Define pin numbers for the LEDs
const int ledPin1 = 21;
const int ledPin2 = 23;

const int ledPin3 = 12;   
const int ledPin4 = 14;   
const int ledPin5 = 27;  
const int ledPin6 = 26;   

// Define blink frequencies for each LED (in Hz)
const float frequency1 = 160.0; 
const float frequency2 = 70.0; 
const float frequency_display = 100.0;

const long interval1 = (1.0 / frequency1) * 1000 / 2; 
const long interval2 = (1.0 / frequency2) * 1000 / 2; 
const long interval_Display = (1.0 / frequency_display) * 1000 / 2; 

bool ledState1 = LOW;
bool ledState2 = LOW;
bool ledState_display = LOW;

// Variables to hold the last time the LED was updated
unsigned long previousMillis1 = 0; 
unsigned long previousMillis2 = 0;
unsigned long previousMillisDisplay = 0;

void setup() {
  // Set the digital pins as outputs
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  pinMode(ledPin4, OUTPUT);
  pinMode(ledPin5, OUTPUT);
  pinMode(ledPin6, OUTPUT);
}

void loop() {
  
  unsigned long currentMillis = millis();

  // Update LED 1
  if (currentMillis - previousMillis1 >= interval1) 
  {
    previousMillis1 = currentMillis;
    ledState1 = !ledState1;
    digitalWrite(ledPin1, ledState1);
  }

  // Update Display LEDs
  if(currentMillis - previousMillisDisplay >= interval_Display)
  {

    previousMillisDisplay = currentMillis;
    ledState_display = !ledState_display;
    
    digitalWrite(ledPin3, ledState_display);
    digitalWrite(ledPin4, ledState_display);
    digitalWrite(ledPin5, ledState_display);
    digitalWrite(ledPin6, ledState_display);
  }

  // Update LED 2
  if (currentMillis - previousMillis2 >= interval2) 
  {
    previousMillis2 = currentMillis;
    ledState2 = !ledState2;
    digitalWrite(ledPin2, ledState2);
  }
}
