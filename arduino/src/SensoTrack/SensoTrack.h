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
 #    simple example to connect to senso tract backend 
 #    using Serial
 ##--------------------------------------------------------
 # History     :
 # 1.0.0 - 2023-09 : Release of the file
 ##--------------------------------------------------------
 # Communication with remote over serial with a basic text protocol
 # - Remote to arduino messages:
 #      remote request supported sensors:
 #          COMMAND/:/SENSORS
 #      remote send a request to a specific sensor without specif command 
 #          COMMAND/:/SENSOR/:/sid
 #              where:
 #                  sid is sensor identifier
 #      remote send a request to a specific sensor with specif command for sensor
 #          COMMAND/:/SENSOR/:/sid/:/command
 #              where:
 #                  sid is sensor identifier
 #                  command is a command for this sensor
 # - Arduino to remote messages:
 #      reply to supported sensors list request (1 per supported sensor)
 #          SENSOR/:/sid 
 #              where:
 #                  sid is supported sensor identifier
 #      sensor data
 #          DATA/:/sid/:/value
 #              where
 #                  sid is supported sensor identifier
 #                  value is sensor value
 */
#ifndef __SENSORTRACK_H__
#define __SENSORTRACK_H__
  #include <SerialCom.h>

  #define MAX_SENSORS 20

    // Initialize senso track lib
    //    call it in setup()
    //  SerialCom *serialCom: connection handler over serial
    //  void (*on_command)(char *, char *): function to call when a command is received from remote
    //    may be NULL
    void senso_track_lib_init(SerialCom *serialCom, void (*on_command)(char *, char *));

    // Delare a suppoirted sensor
    //    call it in setup() after senso_track_lib_init
    //  char *sid: sensor identifier
    void senso_track_lib_declare_sensor(char *sid);

    // Send a vale to remote for a sensor
    //    call it after lib is initilialized and supported sensors declared
    //  char *sid: sensor identifier
    //  char *value: sensor value
    void senso_track_send(char *sid, char *value);

    // Lib processing during main loop
    //  call it in loop()
    void senso_track_on_loop();
#endif
