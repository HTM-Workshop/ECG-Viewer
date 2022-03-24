void setup(void) {
    Serial.begin(115200);
}

void loop(void) {
    while(Serial.available() == 0) {}
    Serial.read();
    Serial.println(1000 - analogRead(A0));
}

