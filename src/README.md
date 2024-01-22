# Main project files

- `./`: Current directory contains the game and neuromorphic application
- `util/`:  script to locate the metavision sdk and ensure it's found
- `blinker_opengl/`:  simple c++ opengl application that blinks with the specified frequency
- `playground/`: undocumented scripts used during the development 

# Usage
- Follow the guide to install the metavision sdk under https://docs.prophesee.ai/stable/installation/index.html


- Setup your python environment (ensure that you use a compatible python version for your OS) 

    ```sh 
    python3 -m venv --system-site-packages .venv
    ```
- The `--system-site-packages` flag allows access of the virtual environment to the system packages where metavision is installed
- Activate it (e.g. `source .venv/bin/activate` or `.venv\Scripts\activate.bat`)
- Install our dependencies `pip install opencv-python numpy pygame`
- Install metavision dependencies if not already done: https://docs.prophesee.ai/stable/installation/linux.html#installing-dependencies