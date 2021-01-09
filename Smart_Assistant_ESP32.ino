#include <MCP3008.h>
#include <SPI.h>

MCP3008 adc(13,11,12,10);

void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:

    Serial.println("---------------");
    Serial.println("Value:" + String(adc.readADC(0)));
    delay(2000);
    
}
