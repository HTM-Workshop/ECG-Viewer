char buf[6];

void setup(void) {
    Serial.begin(115200);
    //analogReference(EXTERNAL);
}

void loop(void) {
    while(Serial.available() == 0) {}
    while(Serial.available() > 0) {
        Serial.read();
    }
    sprintf(buf, "a%03d\n", analogRead(A0));
    Serial.println(buf);
}
