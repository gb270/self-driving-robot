# Self- Driving Robot

## Description
This project involves building a self-drviing robot using a Raspberri Pi 5 for AI-based control and an Arduino for motor management. The robot is designed to navigate autonomously using a PI camera module and computer vision techniques.


## Components

- **Raspberry Pi 5**: Main control unit for AI processing and camera input handling
- **Arduino**: Responsible for motor control and interfacing with sensors.
- **PI Camera Module**: Captures real-time images for processing for collision detection and avoidance.
- **Motor Driver**: Controls robot movement.

## Features
- Real-time image processing using OpenCV and object detection using YOLO.
- Simple command interface for manual control.

## Note
This project is still in active development. At the moment, only the manual control has been implemented. AI features are still in development.

For manual control: after cloning the repo and setting up correctly run:
    ``` bash
    python3 test.py

and follow the instructions given.
More in-depth instructions and a guide for reproducing this entire project will be added shortly.

## License
This project is licensed under the GNU GPL. See the [License](LICENSE) file for more details. 