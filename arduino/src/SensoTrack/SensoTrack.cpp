#include <SensoTrack.h>



#define SEPARATOR "/:/"
#define SENSORS_RQT "SENSORS"
#define SINGLE_SENSOR_RQT "SENSOR"
#define SENSOR_REPLY "SENSOR"
#define DATA_KW "DATA"
#define COMMAND_KW "COMMAND"


typedef struct {
 SerialCom *serialCom;
 char *sensors[MAX_SENSORS];
 uint8_t sensorsCount=0;
 void (*on_command)(char *, char *) = NULL;
 uint8_t initialized = 0;
} sensoTrack;

sensoTrack sensoTrackLib;

uint8_t is_supported_sensor(char *sid){
  uint8_t i;
  for (i=0;i<sensoTrackLib.sensorsCount;i++){
    if (strcmp(sid, sensoTrackLib.sensors[i])==0){
      return 1;
    }
  }
  return 0;
}

void sensors_list(){
  uint8_t i;
  char sensorDef[50];
  for (i=0;i<sensoTrackLib.sensorsCount;i++){
    sprintf(sensorDef,"%s%s%s", SENSOR_REPLY, SEPARATOR, sensoTrackLib.sensors[i]);
    sensoTrackLib.serialCom->println(sensorDef);
  }
}

void serialComOnCommand(char *cmd){
  char commandBuff[100], sid[20];
  char *startAt;
  char *subCmd;
  char *sidStartAt, *sidEndAt;
  uint8_t sidLen;

  if (!sensoTrackLib.initialized){
    return;
  }

  sprintf(commandBuff,"%s%s", COMMAND_KW, SEPARATOR);
  if (strncmp(cmd, commandBuff, strlen(commandBuff)) == 0) {
    startAt = cmd+strlen(commandBuff);
    if (strncmp(startAt, SENSORS_RQT, strlen(SENSORS_RQT)) == 0){
      sensors_list();
    }else if (strncmp(startAt, SINGLE_SENSOR_RQT, strlen(SINGLE_SENSOR_RQT)) == 0 && sensoTrackLib.on_command){
      sidStartAt=startAt+strlen(SINGLE_SENSOR_RQT)+strlen(SEPARATOR);
      sidEndAt=strstr(sidStartAt, SEPARATOR);
      if (sidEndAt){
        sidLen=sidEndAt-sidStartAt;
        strncpy(sid, sidStartAt, sidLen);
        sid[sidLen]=0;
        subCmd=sidEndAt+strlen(SEPARATOR);
      }else{
        strcpy(sid, sidStartAt);
        subCmd=sidStartAt+strlen(sid);
      }
      if (is_supported_sensor(sid)){
        sensoTrackLib.on_command(sid, subCmd);
      }
    }
  }
  
}

void senso_track_lib_init(SerialCom *serialCom,  void (*on_command)(char *, char *)){
  sensoTrackLib.serialCom=serialCom;
  serialCom->commandHandler=&serialComOnCommand;
  //sensoTrackLib.sensors = sensors;
  sensoTrackLib.on_command = on_command;
  sensoTrackLib.initialized = 1;
}

void senso_track_lib_declare_sensor(char *sensor){
  if (!sensoTrackLib.initialized){
    return;
  }
  sensoTrackLib.sensors[sensoTrackLib.sensorsCount] = malloc(strlen(sensor)+1);
  strcpy(sensoTrackLib.sensors[sensoTrackLib.sensorsCount], sensor);  
  sensoTrackLib.sensorsCount++;
  
}
void senso_track_on_loop(){
  if (sensoTrackLib.initialized){
    sensoTrackLib.serialCom->handleSerialCom();
  }
}

void senso_track_send(char *sid, char *value){
  if (!sensoTrackLib.initialized){
    return;
  }
  if (is_supported_sensor(sid)){
    sensoTrackLib.serialCom->print(DATA_KW);
    sensoTrackLib.serialCom->print(SEPARATOR);
    sensoTrackLib.serialCom->print(sid);
    sensoTrackLib.serialCom->print(SEPARATOR);
    sensoTrackLib.serialCom->println(value);
  }
  
}

