void setup(void) {
    Serial.begin(115200);
    analogReference(INTERNAL);
}

void loop(void) {
    while(Serial.available() == 0) {}
    Serial.read();
    Serial.println(analogRead(A0));
    Serial.flush();
}
