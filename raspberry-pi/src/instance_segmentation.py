import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import argparse
import multiprocessing
import numpy as np
import setproctitle
import cv2
import time
import hailo
import serial
from hailo_rpi_common import (
    get_default_parser,
    QUEUE,
    get_caps_from_pad,
    get_numpy_from_buffer,
    GStreamerApp,
    app_callback_class,
)

# -----------------------------------------------------------------------------------------------
# Serial Communication with Arduino
# -----------------------------------------------------------------------------------------------
# Initialize the serial communication with Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)


# -----------------------------------------------------------------------------------------------
# Functions to control the robot
# -----------------------------------------------------------------------------------------------
def send_command_to_arduino(command):
    """Sends a direction command to the Arduino."""
    valid_commands = ['F', 'B', 'L', 'R', 'Q', 'E', 'A', 'D']
    if command in valid_commands:
        ser.write(bytes(command, 'utf-8'))
        print(f"Sent command to Arduino: {command}")

        if ser.in_waiting > 0:
            received = ser.readline().decode('utf-8').rstrip()
            print("Arduino response:", received)

def turn_robot_left():
    send_command_to_arduino('L')

def turn_robot_right():
    send_command_to_arduino('R')

def move_robot_forward():
    send_command_to_arduino('F')

def move_robot_backward():
    send_command_to_arduino('B')

def stop_robot():
    send_command_to_arduino('S')


# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()



# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()
    string_to_print = f"Frame count: {user_data.get_count()}\n"

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Flag to check if any valid detections were found
    any_detection = False

    # Parse the detections
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()

        # Get bounding box coordinates
        x_min = int(bbox.xmin() * width)
        y_min = int(bbox.ymin() * height)
        x_max = int(bbox.xmax() * width)
        y_max = int(bbox.ymax() * height)

        # Calculate the center of the bounding box
        x_center = (x_min + x_max) // 2
        y_center = (y_min + y_max) // 2
        
        # Print detection info
        string_to_print += (f"Detection: {label} {confidence:.2f}\n")
        string_to_print += (f"Bounding box: ({x_min}, {y_min}), ({x_max}, {y_max})\n")
        string_to_print += (f"Object center: ({x_center}, {y_center})\n")

        if label == "person":
            # Control robot based on object position
            if x_center < width / 3:
                turn_robot_left()
            elif x_center > 2 * width / 3:
                turn_robot_right()
            else:
                move_robot_forward()
        
        # Avoid any other detected objects
        else:
            if x_center < width / 3:
                # Object is on the left side; turn right to avoid it
                turn_robot_right()
            elif x_center > 2 * width / 3:
                # Object is on the right side; turn left to avoid it
                turn_robot_left()
            else:
                # Object is in the center; move backward or adjust as necessary
                move_robot_backward()
    
    # stopping robot if nothing found
    if not any_detection:
        stop_robot()

    print(string_to_print)
    return Gst.PadProbeReturn.OK


#-----------------------------------------------------------------------------------------------
# User Gstreamer Application
# -----------------------------------------------------------------------------------------------

# This class inherits from the hailo_rpi_common.GStreamerApp class

class GStreamerInstanceSegmentationApp(GStreamerApp):
    def __init__(self, args, user_data):
        # Call the parent class constructor
        super().__init__(args, user_data)
        # Additional initialization code can be added here
        # Set Hailo parameters these parameters should be set based on the model used
        self.batch_size = 2
        self.network_width = 640
        self.network_height = 640
        self.network_format = "RGB"
        self.default_postprocess_so = os.path.join(self.postprocess_dir, 'libyolov5seg_post.so')
        self.post_function_name = "yolov5seg"
        self.hef_path = os.path.join(self.current_path, '../resources/yolov5n_seg_h8l_mz.hef')
        self.app_callback = app_callback

	    # Set the process title
        setproctitle.setproctitle("Hailo Instance Segmentation App")

        self.create_pipeline()

    def get_pipeline_string(self):
        if self.source_type == "rpi":
            source_element = f"libcamerasrc name=src_0 ! "
            source_element += f"video/x-raw, format={self.network_format}, width=1536, height=864 ! "
            source_element += QUEUE("queue_src_scale")
            source_element += f"videoscale ! "
            source_element += f"video/x-raw, format={self.network_format}, width={self.network_width}, height={self.network_height}, framerate=30/1 ! "

        elif self.source_type == "usb":
            source_element = f"v4l2src device={self.video_source} name=src_0 ! "
            source_element += f"video/x-raw, width=640, height=480, framerate=30/1 ! "
        else:
            source_element = f"filesrc location=\"{self.video_source}\" name=src_0 ! "
            source_element += QUEUE("queue_dec264")
            source_element += f" qtdemux ! h264parse ! avdec_h264 max-threads=2 ! "
            source_element += f" video/x-raw,format=I420 ! "
        source_element += QUEUE("queue_scale")
        source_element += f"videoscale n-threads=2 ! "
        source_element += QUEUE("queue_src_convert")
        source_element += f"videoconvert n-threads=3 name=src_convert qos=false ! "
        source_element += f"video/x-raw, format={self.network_format}, width={self.network_width}, height={self.network_height}, pixel-aspect-ratio=1/1 ! "


        pipeline_string = "hailomuxer name=hmux "
        pipeline_string += source_element
        pipeline_string += "tee name=t ! "
        pipeline_string += QUEUE("bypass_queue", max_size_buffers=20) + "hmux.sink_0 "
        pipeline_string += "t. ! " + QUEUE("queue_hailonet")
        pipeline_string += "videoconvert n-threads=3 ! "
        pipeline_string += f"hailonet hef-path={self.hef_path} batch-size={self.batch_size} force-writable=true ! "
        pipeline_string += QUEUE("queue_hailofilter")
        pipeline_string += f"hailofilter function-name={self.post_function_name} so-path={self.default_postprocess_so} qos=false ! "
        pipeline_string += QUEUE("queue_hmuc") + " hmux.sink_1 "
        pipeline_string += "hmux. ! " + QUEUE("queue_hailo_python")
        pipeline_string += QUEUE("queue_user_callback")
        pipeline_string += f"identity name=identity_callback ! "
        pipeline_string += QUEUE("queue_hailooverlay")
        pipeline_string += f"hailooverlay ! "
        pipeline_string += QUEUE("queue_videoconvert")
        pipeline_string += f"videoconvert n-threads=3 qos=false ! "
        pipeline_string += QUEUE("queue_hailo_display")
        pipeline_string += f"fpsdisplaysink video-sink={self.video_sink} name=hailo_display sync={self.sync} text-overlay={self.options_menu.show_fps} signal-fps-measurements=true "
        print(pipeline_string)
        return pipeline_string

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    parser = get_default_parser()
    args = parser.parse_args()
    app = GStreamerInstanceSegmentationApp(args, user_data)
    app.run()
