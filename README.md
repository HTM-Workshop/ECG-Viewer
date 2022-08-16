<img src="icon/icon.png" width="128" height="128" align=left> 

# ECG Viewer

A cross-platform graphical front-end for the 'ECG Reader' sensor. The program displays real-time ECG data sourced from the Arduino-based sensor, along with deriving a heart-rate and exporting of data as a PNG, CSV or RAW. 

### **WARNING**: This program is for educational purposes only. NOT FOR MEDICAL USE!



## Version 2.0.0 Changes
<ul>
  <li>Capture speed is +200% faster.</li>
  <li>More graph export options.</li>
  <li>Graph framerate options to help with slower computers.</li>
  <li>Cleaner and more stable codebase.</li>
  <li>Updated Arduino sketch (v2.0.0)</li>
</ul>
Note: The Arduino sketch from Version 1.x.x is no longer compatible with the ECG Viewer program. The 2.0.0 version of the sketch will need to be uploaded to the Arduino (see folder: arduino_ecg/).

## Notes on binaries:
The binaries distributed under releases are not signed. Certain versions of Windows and MacOS may prevent this program from running. The binaries are statically linked and shouldn't require any further configuration to run. 

The program DOES NOT contain drivers for Arduino. You may need to install an FTDI driver if your computer doesn't already have one installed. 


## Building from source:

Note: Python 3.9 will need to be installed (Python 3.10 may also work, but has not been thoroughly tested with the prerequisite libraries). **When installing Python, make sure the ‘Add Python 3.x to PATH’ option is selected during the Windows install.**

#### Windows:
Two scripts are provided to build the program, make.bat and make_ve_build.bat. make.bat will generate the binary normally, without a virtual environment. make_ve_build.bat will generate a binary using a virtual environment, which can later be removed. Depending on your system configuration, Windows may block the execution of batch scripts for security reasons. However, you should be presented with an option to ‘Run Anyways’. You can execute the batch script by either double-clicking on the batch file or executing it from the command/powershell window. 

#### MacOS / Linux:
The ‘make’ command will need to be installed. Open a terminal window, type ‘make’, and press enter. You should be prompted to install the development tools from Apple. Once it’s installed, navigate the terminal to the ecg_viewer git directory. Once in the folder, using the command ‘make’ will automatically install the prerequisites, build the user-interface, and compile the executable to the dist/ directory. 


## Screenshots
![version_1 1 0_win](https://user-images.githubusercontent.com/64606561/182402522-b2fe3eff-01d4-4bc9-ad85-041b43a4a084.png)
![version_1 1 0_mac](https://user-images.githubusercontent.com/64606561/182402519-286e66b4-ecd2-485e-ac6f-dc65fa093e31.png)
![version_1 1 0_lin](https://user-images.githubusercontent.com/64606561/182402518-d9b7552e-01ac-4c81-8674-1c34a27f5348.png)




