# Self- Driving Robot

## Description
This project involves building a self-drviing robot using a Raspberri Pi 5 for AI-based control and an Arduino for motor management. The robot is designed to navigate autonomously using a PI camera module and computer vision techniques.

## Components
- **Raspberry Pi 5**: Main control unit for AI processing and camera input handling
- **hailo 8L AI accelerator**: AI accelerator to run efficient inference.
- **Arduino**: Responsible for motor control and interfacing with sensors.
- **PI Camera Module**: Captures real-time images for processing for collision detection and avoidance.
- **Motor Driver**: Controls robot movement.

## Features
- Real-time image processing using RPI camera module and object detection using YOLO6n.
- Simple command interface for manual control.

## Installation
- Follow this [guide](https://github.com/hailo-ai/hailo-rpi5-examples/blob/main/doc/basic-pipelines.md#installation) to set up Raspberry Pi 5 with the AI kit. The most important part is to ensure that you have the *venv_hailo_rpi5_examples* Python virtual environment (for more info on Python virtual environments read this [guide](https://realpython.com/python-virtual-environments-a-primer/))
- Clone the repository:
    ```bash
    git clone https://github.com/gb270/self-driving-robot.git

- Copy over *venv_hailo_rpi5_examples* to the self-driving-robot directory. This can differ on different operating systems but for example on Linux/MacOS:
    ```bash
    cp ~/hailo-rp5-examples/venv_hailo_rpi5_examples/ ~/self-driving-robot/raspberry-pi/ -r

*Note* that these directories may be stored in a different place on your machine.

- From the *self-driving-robot* directory intialise the virtual environment:
    ```bash
    source venv_hailo_rpi5_examples/bin/activate

- Ensure the Arduino is set up correctly (_Further instructions coming soon_)


## Usage

To run the object detection (robot will go towards people and avoid other objects) run the following commands:
    ```bash
    cd raspberry-pi/
    python instance_segmentation.py --input rpi


Alternatively, for manual control: after cloning the repo run:
    ``` bash
    python3 test.py

and follow the instructions

## License
This project is licensed under the GNU GPL. See the [License](LICENSE) file for more details. 

## Acknowledgements
- [Hailo](https://hailo.ai/)
- [Arduino](https://www.arduino.cc/)
- [Raspberry Pi](https://www.raspberrypi.org/)

### Note
This project is still in active development. More advanced AI features are coming soon!