const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;

char messageFromPC[buffSize] = {0};
int newFlashInterval = 0;

// Let’s python know that Arduino is ready
void setup() {
  Serial.begin(9600);
  delay(500);
  Serial.println("<Arduino is ready>");
}

// Begins receiving and returning data to python
void loop() {
  getDataFromPC();
  replyToPC();
}

// Stores data in inputBuffer
void getDataFromPC() {
    
  if(Serial.available() > 0) {

    char x = Serial.read();
      
    if (x == endMarker) {
      readInProgress = false;
      newDataFromPC = true;
      inputBuffer[bytesRecvd] = 0;
      parseData();
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}

// Converts inputted data to a string 
void parseData() {
  char * strtokIndx; // this is used by strtok() as an index
  
  strtokIndx = strtok(inputBuffer,",");      // Receive first part of message
  strcpy(messageFromPC, strtokIndx);   // Copy it to messageFromPC

}

// Return message back to python
void replyToPC() {

  if (newDataFromPC) {
    newDataFromPC = false;
    Serial.print("<Msg ");
    Serial.print(messageFromPC);
    Serial.println(">");
  }
}
