/*--------------------------------------------------------
 # Module Name : Arduino Library
 # Version : 1.0.0
 #
 # Software Name : Senso Track
 # Version : 1.0
 #
 # Copyright (c) 2023 benoit.herard(at)orange.com
 # This software is distributed under the Apache 2 license
 # <http://www.apache.org/licenses/LICENSE-2.0.html>
 #
 ##--------------------------------------------------------
 #
 # Created     : 2023-10
 # Authors     : Benoit HERARD <benoit.herard(at)orange.com>
 #
 # Description :
 #    simple example to connect to remote using Serial
 ##--------------------------------------------------------
 # History     :
 # 1.0.0 - 2023-09 : Release of the file
 #
 */
#include <SerialCom.h>
#include <SensoTrack.h>

// Create object to handle connection over serial
// (Can be as well HardwareSerial as SoftwareSerial)
SerialCom com(&Serial);

// Read an alaong pin and send sesnor value as sid sensor
void read_and_send(char sid, int pin){
  char buff[10];
  sprintf(buff, "%d", digitalRead(pin));
  senso_track_send(sid, buff);
}

// Function called by sens_track_lib when a command cmd is received from remote for sensor sid
void on_command(char *sid, char *cmd){
  Serial.print("Received command >"); Serial.print(cmd); Serial.print("< for >"); Serial.print(sid);Serial.println("<");
  if (strcmp(sid, "S0") == 0){
    read_and_send("S0", A0);
  }
}
void setup() {
        // start serial connection handler
        com.begin(9600);

        Serial.println("Arduino Started");
        
        senso_track_lib_init(&com, &on_command);
        senso_track_lib_declare_sensor("S0");
        senso_track_lib_declare_sensor("S1");
        senso_track_lib_declare_sensor("S2");
        senso_track_lib_declare_sensor("S3");
        
}


void loop() {
  senso_track_on_loop();
  read_and_send("S0", A0);
  read_and_send("S1", A1);
  read_and_send("S2", A2);
  read_and_send("S3", A3);
  delay(1000);
}
