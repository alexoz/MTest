MTest
======


## Description

A python library for instrumentation control

By: Alex Omid-Zohoor 

Released August 2014


## Dependencies

* Python 2.7.5
* PyVISA 1.5
* mechanize 0.2.5
* BeautifulSoup 3.2.1
* pyserial 2.7
* NI-VISA 5.4.1 


## Installation

OSX:

1. Install NI-VISA 5.4.1: http://www.ni.com/download/ni-visa-5.4.1/4631/en/

2. Install python dependencies: pip install -r requirements.txt

3. Add path to the MTest directory to PYTHONPATH. This can be done by adding the following line to
   your ~/.bash_profile: export PYTHONPATH="<path to MTest>:$PYTHONPATH"

4. Add the following line to your ~/.bash_profile: alias python32='arch -i386 /usr/bin/python2.7'
   This creates an alias for 32-bit python. You will need to call all functions from 32-bit
   python since NI-VISA is a 32-bit library

5. Install the Prologix GPIB-USB Controller 6.0 USB Driver for OSX: http://prologix.biz 

6. In order to call mtest.py from anywhere, set the value of the INSTRUMENT_DIRECTORY global variable in 
   MTest/mtest.py to the absolute path of MTest/instruments. Otherwise you will only be able to call
   mtest.py from MTest/


WINDOWS:

1. Install NI-VISA 5.4.1: http://www.ni.com/download/ni-visa-5.4.1/4626/en/

2. Install python dependencies: pip install -r requirements.txt

3. Add path to the MTest directory to PYTHONPATH. This can be done by going to 
   My Computer > Properties > Advanced System Settings > Environment Variables >
   Then under system variables, create a new Variable called PYTHONPATH, and set the 
   Variable value to <path to MTest>. Or if PYTHONPATH already exists, simply append
   <path to MTest> to the end of the Variable value

4. Install the Prologix GPIB-USB Controller 6.0 USB Driver for WINDOWS: http://prologix.biz 

5. In order to call mtest.py from anywhere, set the value of the INSTRUMENT_DIRECTORY global variable in 
   MTest/mtest.py to the absolute path of MTest/instruments. Otherwise you will only be able to call
   mtest.py from MTest/


## Instruments

Currently supported instruments include:

1. Agilent E3631A (DC Power Supply)
2. Agilent E3633A (DC Power Supply)
3. Agilent 6060B (Electronic Load)
4. Tektronix MSO 4104B-L (Oscilloscope)

Excluded instruments failed to meet at least one of the following criteria:

1. Remote controllable via serial, usb, or ethernet
2. Useful in an automated test setting. (For example, some older oscilloscopes are remote controllable but can only store waveform data on antiquated local storage media such as CompactFlash. Since this media can only hold a few screenshots and waveforms, it is not useful for longterm automated testing)

Instrument representation:

Each supported instrument is represented by a json file in the MTest/instruments directory with the same name as the instrument. These json files contain a python dictionary with two main keys called 'parameters' and 'commands'. The 'parameters' entry contains information about the instrument itself such as:

id: The identification string of the instrument. This is the string that the instrument sends when asked to identify itself (for many instruments, the command to ask an instrument to identify itself is "*IDN?")

ipAddress: The IP address of the instrument if it is able to connect via ethernet

terminationCharacters: Characters used by the instrument to indicate the end of a message (see instrument's User's Manual)

timeout: Time to wait between sending instrument commands, since it takes instruments some time to receive and process commands. A good value for this parameter can be determined experimentally by writing a test script that sends several commands in a row and checks to see if the commands were properly executed. 

The 'commands' entry is effectively a lookup table for various instrument commands. Each key, which is the name of a python function in mtest.py, corresponds to a value, which is a python dictionary that contains information about the command itself such as:

commandString: The string that is sent to the instrument to execute the command. Note that % placeholders are used for arguments that must be specified by the user at runtime

arguments: Brief description of the arguments that the command takes

description: Description of the command copied from the instrument's User Manual or Programming Manual


## Examples

In the following examples, '>>' indicates a terminal, command prompt, or python prompt command. 

Confirm successful installation of mtest python module:

1. Open terminal in OSX or command prompt in WINDOWS

2. Start 32-bit python: 
	OSX:
	>> python32   
	WINDOWS:
	>> python 

3. >> import mtest

4. If the module imports without raising errors, installation was successful

Quick capture from Tektronix MSO4104B-L Oscilloscope:

1. Turn on Tektronix MSO 4104B-L

2. Open terminal in OSX or command prompt in WINDOWS

3. Start 32-bit python: 
	OSX:
	>> python32   
	WINDOWS:
	>> python 

4. >> import mtest

5. >> osc = mtest.TektronixMSO4104BL('TektronixMSO4104BL', 'ethernet')

6. >> osc.get_screen_capture()

7. This should create a timestamped directory with a csv file containing the waveform data of all 4 channels and a screenshot png image


## Scripts

There are a number of test and functional scripts in the MTest/scripts directory. Test scripts are meant to test the ability
to control specific instruments with mtest, as well as determine the minimum instrument timeout (if relevant). When adding
a new instrument to MTest, one should also create a corresponding test script. Functional scripts, such as batteryCycle.py, are
template scripts that can be used for automated testing. 


## Organization 

mtest.py is organized in an object-oriented fashion, where each instrument inherits properties from a base class of Instrument. 
Subclasses of Instrument currently include DCPowerSupply, Oscilloscope, and ElectronicLoad. Subclasses of these classes are 
individual instruments themselves, such as Agilent6060B, AgilentE3633A, AgilentE3631A, and TektronixMSO4104BL. 

Instrument
	DCPowerSupply
		AgilentE3633A
		AgilentE3631A
	ElectronicLoad
		Agilent6060B
	Oscilloscope
		TektronixMSO4104BL

This structure was mainly chosen to keep the code organized and scalable. The level of code reuse is minor, as each time a new 
instrument is added a custom JSON file must be created in MTest/instruments. However, this structure can help guide the process
of adding a new instrument. For example, all instruments inherit from the base instrument class, and thus must contain commands
for the Instrument methods of get_id() and reset(). All instruments that inherit from the DCPowerSupply class must include a
command for set_voltage(), etc.


