#ifndef __SENSORTRACK_H__
#define __SENSORTRACK_H__
  #include <SerialCom.h>

  #define MAX_SENSORS 20

  void senso_track_lib_init(SerialCom *serialCom, void (*on_command)(char *, char *));
  void senso_track_lib_declare_sensor(char *sensor);
  void senso_track_send(char *sid, char *value);
  void senso_track_on_loop();

    
#endif
