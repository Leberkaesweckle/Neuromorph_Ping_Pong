# Neuromorphic Ping Pong
Ping pong game played with LEDs tracked by a neuromorphic camera.

![](docs/banner.JPG)


## Setup

- 4 LEDs blinking with a frequency of 100Hz to mark the corners of the playing field as shown in the image above.
- 1-2 LEDs for player1 (160Hz) and optionally player2
(70Hz)
## How to run

First start the Ping pong with the included Server

```sh
python ping_pong_server.py
```

then optionally start the client.

```sh
python neuromorphic_vision_paddle_client.py
```

The client should connect to the server and the start detecting the leds of the display. After a short calibration phase the corner leds will be detected and marked on screen. The player Leds should now work and the game should be playable.

## Structure

- `src/` : Sourcecode of the game and neuromorphic camera control
- `esp32-controller/` : Hardware details and source code for the esp32 programs used


