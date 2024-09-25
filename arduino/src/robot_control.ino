// Motor speed
const int E1 = 3; 
const int E2 = 11;
const int E3 = 5; 
const int E4 = 6; 

// Motor direction
const int M1 = 4; 
const int M2 = 12;
const int M3 = 8; 
const int M4 = 7; 

// const for ultrasonic sensor
const int echoPin = 13;
const int trigPin = 9;

// variables for ultrasonic sensor
long duration;
int distance;

enum Motor {
  MOTOR1,
  MOTOR2,
  MOTOR3,
  MOTOR4
};

// Struct for relating motor to the speed pin
// idea is to create a dictionary that maps M1 -> E1, i.e. M1 -> pin 3 etc. for all motors
struct KeyValuePair {
  int motorPin;
  int speedPin;
};

const int MAX_ITEMS = 4;
KeyValuePair dictionary[MAX_ITEMS] = {
  {M1, E1},
  {M2, E2},
  {M3, E3},
  {M4, E4}
};

int getSpeedPin(int motorPin) {
  for (int i = 0; i < MAX_ITEMS; i++) {
    if (dictionary[i].motorPin == motorPin) {
      return dictionary[i].speedPin;
    }
  }
  return -1; // Pin not found so return invalid pin value
}

int getMotorPin(Motor motor) {
  switch (motor) {
    case MOTOR1: return M1;
    case MOTOR2: return M2;
    case MOTOR3: return M3;
    case MOTOR4: return M4;
    default: return -1;
  }
}

// Generic commands
void Motor_forward(Motor motor, char Speed) {
  int motorPin = getMotorPin(motor);
  int speedPin = getSpeedPin(motorPin);

  if (motorPin != -1 && speedPin != - 1) {
    digitalWrite(motorPin, LOW);
    analogWrite(speedPin, Speed);
  }
}

void Motor_reverse(Motor motor, char Speed) {
  int motorPin = getMotorPin(motor);
  int speedPin = getSpeedPin(motorPin);

  if (motorPin != -1 && speedPin != - 1) {
    digitalWrite(motorPin, HIGH);
    analogWrite(speedPin, Speed);
  }
}

void Motor_stop(Motor motor) {
  int motorPin = getMotorPin(motor);
  int speedPin = getSpeedPin(motorPin);

  if (motorPin != -1 && speedPin != -1) {
    analogWrite(speedPin, 0);
  }
}

void car_forward(char Speed) {
  for (int i = MOTOR1; i <= MOTOR4; i++) {
    Motor motor = static_cast<Motor>(i); // Convert int to Motor enum
    Motor_forward(motor, Speed); 
    }  
}

void car_reverse(char Speed) {
  for (int i = MOTOR1; i <= MOTOR4; i++) {
    Motor motor = static_cast<Motor>(i);
    Motor_reverse(motor, Speed);
  }
}

void car_stop() {
  for (int i = MOTOR1; i <= MOTOR4; i++) {
    Motor motor = static_cast<Motor>(i); // Convert int to Motor enum
    Motor_stop(motor);
  }  
}



void car_left(char Speed) {
  Motor_reverse(MOTOR1, Speed);
  Motor_forward(MOTOR2, Speed);
  Motor_reverse(MOTOR3, Speed);
  Motor_forward(MOTOR4, Speed);
}

void car_right(char Speed) {
  Motor_forward(MOTOR1, Speed);
  Motor_reverse(MOTOR2, Speed);
  Motor_forward(MOTOR3, Speed);
  Motor_reverse(MOTOR4, Speed);
}

void car_forward_left(char Speed) {
  Motor_forward(MOTOR1, Speed / 2);
  Motor_forward(MOTOR2, Speed);
  Motor_forward(MOTOR3, Speed / 2);
  Motor_forward(MOTOR4, Speed);
}

void car_forward_right(char Speed) {
  Motor_forward(MOTOR1, Speed);
  Motor_forward(MOTOR2, Speed / 2);
  Motor_forward(MOTOR3, Speed);
  Motor_forward(MOTOR4, Speed / 2);
}

void car_backward_left(char Speed) {
  Motor_reverse(MOTOR1, Speed / 2);
  Motor_reverse(MOTOR2, Speed);
  Motor_reverse(MOTOR3, Speed / 2);
  Motor_reverse(MOTOR4, Speed);
}

void car_backward_right(char Speed) {
  Motor_reverse(MOTOR1, Speed);
  Motor_reverse(MOTOR2, Speed / 2);
  Motor_reverse(MOTOR3, Speed);
  Motor_reverse(MOTOR4, Speed / 2);
}

int get_distance() {
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2;
  // Prints the distance on the Serial Monitor if the value is not 0
  if (distance >= 0) {
    return distance;
  } else {
    return -1;
  }
}



void setup() {
  for(int i=3;i<9;i++)
    pinMode(i,OUTPUT);
  for(int i=11;i<13;i++)
    pinMode(i,OUTPUT);
  
  pinMode(echoPin, INPUT);
  pinMode(trigPin, OUTPUT);
  Serial.begin(9600);

  // Optional initial delay to stabilize the sensor
  delay(1000);
}
// MOTOR positioning IMPORTANT FOR TURNING COMMANDS TO WORK
/* 
M1: Front-left
M2: Front-Right
M3: Rear-Left
M4: Rear-Right
*/
void loop() {
  
  // communication with RPI 5
  if (Serial.available() > 0) {
    char command = Serial.read();

    // Forward
    if (command == 'F') {
      Serial.println("Moving Forward");
      car_forward(100);
      delay(500);
      car_stop();
    }

    // Reverse
    if (command == 'B') {
      Serial.println("Moving Backwards");
      car_reverse(100);
      delay(500);
      car_stop();
    }

    // Left
    if (command == 'L') {
      Serial.println("Moving Left");
      car_left(100);
      delay(500);
      car_stop();
    }

    // Right
    if (command == 'R') {
      Serial.println("Moving Right");
      car_right(100);
      delay(500);
      car_stop();
    }

    // Forward left
    if (command == 'Q') {
      car_forward_left(100);
      delay(500);
      car_stop();
    }

    // Forward right
    if (command == 'E') {
      car_forward_right(100);
      delay(500);
      car_stop();
    }

    // Backward left
    if (command == 'A') {
      car_backward_left(100);
      delay(500);
      car_stop();
    }

    // Backward right
    if (command == 'D') {
      car_backward_right(100);
      delay(500);
      car_stop();
    }

  }

}
