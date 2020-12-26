# Raspberry Pi RTL-SDR Scanner

Software-defined radio and a Raspberry Pi to collect energy consumption sampled and sent to an efergy e2 classic

Connect to a terminal on the Pi and execute the following commands to install the dependencies:


    sudo apt-get update
    sudo apt-get install cmake build-essential python-pip libusb-1.0-0-dev python-numpy git pandoc

Next download, compile, and install the RTL-SDR library by executing:
Download: file
Copy Code

    cd ~
    git clone git://git.osmocom.org/rtl-sdr.git
    cd rtl-sdr
    mkdir build
    cd build
    cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON
    make
    sudo make install
    sudo ldconfig

Finally install the RTL-SDR Python wrapper by executing:
Download: file
Copy Code

    sudo pip install pyrtlsdr

## Efergy monitor (@github/magellannh/RPI_Efergy)

Instructions:
1) Get a working usb rtl-sdr device with the rtl_fm binary (probably from rtl-sdr library).

2) Check #defines in EfergyRPI_log.c to match your specific Efergy sensor/transmitter type

  In particular, check this one:
  #define VOLTAGE

  - With the default settings the program tries to decode up to 9 bytes of
    message data and checks for both 1 byte checksum and the 2 byte CRC.

3) Compile using: gcc -O3 -o EfergyRPI_log EfergyRPI_log.c  -lm 

4) Run program and review program help

  ./EfergyRPI_log -help

5) Find optimal frequency and gain values by analyzing rtl_fm output in debug mode

  rtl_fm -f 433.55e6 -s 200000 -r 96000 -A fast | ./EfergyRPI_log -d
  
   - Adjust frequency (-f) by .1 plus or minus until debug output
     shows wave center close to 0 and solid decode.
   - Gain (-g) may or may not be needed.  Some folks had best results
     by adding -g 19.7 to rtl_fm
 
6) Run in normal mode to output parsed energy usage info

   rtl_fm -f 433.55e6 -s 200000 -r 96000 -A fast 2>/dev/null | ./EfergyRPI_log

7) Run in log mode to send parsed energy usage info to log file

   rtl_fm -f 433.55e6 -s 200000 -r 96000 -A fast 2>/dev/null | ./EfergyRPI_log logfile

* VOLTAGE * set to 220
* SAMPLES between fflush: 30 *
