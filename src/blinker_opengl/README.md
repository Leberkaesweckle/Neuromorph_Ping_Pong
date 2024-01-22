# Simple Opengl Blinking program 
Program that flashes the window with a specified frequency. Used over pygame to ensure a consistent  framerate and allow for adaptive sync.

# Build

```sh
g++ main.cpp -o BlinkingApp -lGL -lGLEW -lglfw
```

# Usage

Simply run the app with the wanted frequency as parameter
```sh
./BlinkingApp 3 # Flashes the window with a  frequency of 3Hz 
```