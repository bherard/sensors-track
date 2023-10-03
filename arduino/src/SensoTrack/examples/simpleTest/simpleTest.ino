/*--------------------------------------------------------
 # Module Name : Arduino Library
 # Version : 1.0.0
 #
 # Software Name : SerialCom
 # Version : 1.0
 #
 # Copyright (c) 2015 Zorglub42
 # This software is distributed under the Apache 2 license
 # <http://www.apache.org/licenses/LICENSE-2.0.html>
 #
 ##--------------------------------------------------------
 # File Name   : SerialCom.h
 #
 # Created     : 2015-12
 # Authors     : Zorglub42 <contact(at)zorglub42.fr>
 #
 # Description :
 #     simple example to connect to socket server
 ##--------------------------------------------------------
 # History     :
 # 1.0.0 - 2015-12-03 : Release of the file
 #
 */
#include <SerialCom.h>
#include <SensoTrack.h>

// Create object to handle connection to socket server
// Can use as well HardwareSerial as SoftwareSerial
SerialCom com(&Serial);

void on_command(char *sid, char *cmd){
  Serial.println(strlen(cmd));
  delay(500);
  Serial.print("Received command >"); Serial.print(cmd); Serial.print("< for >"); Serial.print(sid);Serial.println("<");
  if (strcmp(sid, "A0")==0){
    senso_track_send("A0", "10");
  }
}
void setup() {
        // start object
        com.begin(9600);
        com.println("Arduino Started");
        
        senso_track_lib_init(&com, &on_command);
        senso_track_lib_declare_sensor("A0");
        senso_track_lib_declare_sensor("A1");
        senso_track_lib_declare_sensor("A2");
        senso_track_lib_declare_sensor("A3");
        
}


void loop() {
  //com.handleSerialCom();
  senso_track_on_loop();
  //senso_track_send("A1", "30");
  //delay(1000);
}
