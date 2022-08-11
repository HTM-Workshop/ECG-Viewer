/*         Sketch v2.0.0
    Written by Kevin Williams - 2022    

        Note on compatibility:
    This version of the sketch is compatible with 2.x.x of the ECG Viewer
 
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
    MA 02110-1301, USA.
 */

char buf[6];

void setup(void) {
    Serial.begin(115200);
}

void loop(void) {
    while(Serial.available() == 0) {}
    while(Serial.available() > 0) {
        Serial.read();
    }
    sprintf(buf, "$%03d\n", analogRead(A0));
    Serial.print(buf);
}
