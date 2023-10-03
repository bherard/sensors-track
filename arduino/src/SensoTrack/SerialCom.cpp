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
 #     Helper class implementation
 ##--------------------------------------------------------
 # History     :
 # 1.0.0 - 2015-12-03 : Release of the file
 #
 */
#include "SerialCom.h"

#ifdef SUPPORT_SOFTWARE_SERIAL
#if ARDUINO >= 100
SerialCom::SerialCom(SoftwareSerial *sws){
        this->commandHandler = NULL;
        this->isHW=0;
        this->sws=sws;
        this->mySerial=sws;
}
#else
SerialCom::SerialCom(NewSoftSerial *sws){
        this->commandHandler = NULL;
        this->isHW=0;
        this->sws=sws;
        this->mySerial=sws;
}
#endif
#endif
SerialCom::SerialCom(HardwareSerial *hws){
        this->commandHandler = NULL;
        this->isHW=1;
        this->hws=hws;
        this->mySerial=hws;
}
SerialCom::SerialCom(Stream *hws){
        this->commandHandler = NULL;
        this->isHW=1;
        this->hws=(HardwareSerial*)hws;
        this->mySerial=hws;
}



void SerialCom::begin(uint16_t baud){
        if (this->isHW) {
                this->hws->begin(baud);
        }else{
                this->sws->begin(baud);
        }
        this->println("Arduino Started");
}



void SerialCom::handleSerialCom(){
        if (this->mySerial->available()) {
                char cmd[COMMAND_BUFFER_SIZE];
                int i=0;
                char c=0;
                do {
                        if (this->mySerial->available()) {
                                c=this->mySerial->read();
                                //Serial.print(c);
                                cmd[i++]=c;
                                cmd[i]=0;
                        }

                } while (c != '\n');
                cmd[i-1]=0;
                mySerial->println(F("\n***START***"));
                delay(5);
                mySerial->flush();
                if (this->commandHandler){
                        this->commandHandler(cmd);
                }
                delay(5);
                mySerial->println(F("\n***DONE***"));
                delay(5);
        }
}


size_t SerialCom::write(uint8_t b){
        this->mySerial->write(b);
}
