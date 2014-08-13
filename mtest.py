import json
import os
import glob
import serial
import visa
from sys import platform
import mechanize
import time
import csv
import shutil
from BeautifulSoup import BeautifulSoup as soup

#globals
INSTRUMENT_DIRECTORY = './instruments'
SERIAL_ADDRESSES_OSX = ['ASRL1', 'ASRL2', 'ASRL3', 'ASRL4', 'ASRL5', 'ASRL6', 'ASRL7', 'ASRL8', 'ASRL9']
SERIAL_ADDRESSES_WINDOWS = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9']
MAC_OSX_ALIAS = 'darwin'
WINDOWS_ALIAS = 'win32'
LINUX_ALIAS = 'linux'
LINUX2_ALIAS = 'linux2'

#base class
class Instrument(object):

    def __init__(self, name, communicationProtocol='serial', serialAddress=None):
        self.name = name
        self.communicationProtocol = communicationProtocol
        self.serialAddress = serialAddress
        instrumentFile = open(os.path.join(INSTRUMENT_DIRECTORY, name + '.json'))
        instrumentFileDict = json.load(instrumentFile)
        self.parametersDict = instrumentFileDict['parameters']
        self.terminationCharacters = str(self.parametersDict['terminationCharacters'])
        if self.parametersDict['usbAddress'] == 'None':
            self.usbAddress = None
        else:
            self.usbAddress = self.parametersDict['usbAddress']
        if self.parametersDict['ipAddress'] == 'None':
            self.ipAddress = None
        else:
            self.ipAddress = self.parametersDict['ipAddress']
        if self.parametersDict['serialTimeout'] == 'None':
            self.serialTimeout = None
        else:
            self.serialTimeout = float(self.parametersDict['serialTimeout'])
        self.commandDict = instrumentFileDict['commands']
        self.connect()

    def __del__(self):
        self.disconnect()

    def print_commands(self):
        for command in self.commandDict:
            print command

    def print_command_description(self, commandName):
        print self.commandDict[commandName]['description']

    def print_command_arguments(self, commandName):
        print self.commandDict[commandName]['arguments']

    def get_command_string(self, commandName):
        return str(self.commandDict[commandName]['commandString'])

    def send_command(self, commandName, *parameters):
        #form parameter tuple
        parametersTuple = ()
        for parameter in parameters:
            #note that we typecast all parameters as strings here
            parametersTuple += (str(parameter),)
        if self.communicationProtocol is 'serial':
            # #note that pyserial no longer allows you to specify termination characters explicitly, so instead, we append them to the end of each command.
            # self.handle.write((self.get_command_string(commandName) % parametersTuple) + self.terminationCharacters)
            # return self.handle.read(SERIAL_READ_SIZE)
            return self.handle.ask(self.get_command_string(commandName) % parametersTuple)
        elif self.communicationProtocol is 'ethernet':
            return self.handle.ask(self.get_command_string(commandName) % parametersTuple)
        elif self.communicationProtocol is 'usb':
            return self.handle.ask(self.get_command_string(commandName) % parametersTuple)

    def write_command(self, commandName, *parameters):
        #form parameter tuple
        parametersTuple = ()
        for parameter in parameters:
            #note that we typecast all parameters as strings here
            parametersTuple += (str(parameter),)
        if self.communicationProtocol is 'serial':
            self.handle.write(self.get_command_string(commandName) % parametersTuple)

    def connect(self):
        # #refresh SERIAL_ADDRESSES_OSX in case a serial controller was connected after mtest was imported. 
        # SERIAL_ADDRESSES_OSX = glob.glob('/dev/tty.usbserial*')
        if self.communicationProtocol is 'serial':
            if self.serialAddress is not None:
                print 'Connecting to %s...' % self.serialAddress
                self.handle = visa.instrument(self.serialAddress)
                print 'Connected.'
            else:
                # Set up serial port depending on operating system
                if platform == MAC_OSX_ALIAS: 
                    for serialAddress in SERIAL_ADDRESSES_OSX:
                        try:
                            print 'Connecting to %s...' % serialAddress
                            self.handle = visa.instrument(serialAddress)
                            print 'Connected.'
                            self.serialAddress = serialAddress
                            break
                        except:
                            print 'Could not connect to %s.' %serialAddress
                elif platform == WINDOWS_ALIAS:
                    for serialAddress in SERIAL_ADDRESSES_WINDOWS:
                        try:
                            print 'Connecting to %s...' % serialAddress
                            self.handle = visa.instrument(serialAddress)
                            print 'Connected.'
                            self.serialAddress = serialAddress
                            break
                        except:
                            print 'Could not connect to %s.' %serialAddress
                elif platform == LINUX_ALIAS or platform == LINUX2_ALIAS:
                    print 'This library has not been tested on Linux. Attempting to connect using OSX protocol: '
                    for serialAddress in SERIAL_ADDRESSES_OSX:
                        try:
                            print 'Connecting to %s...' % serialAddress
                            self.handle = visa.instrument(serialAddress)
                            print 'Connected.'
                            self.serialAddress = serialAddress
                            break
                        except:
                            print 'Could not connect to %s.' %serialAddress

        elif self.communicationProtocol is 'ethernet':
            #check if device can connect via ethernet
            if self.ipAddress is None:
                print 'Error. This instrument has not been configured to connect via ethernet. Please specify the instrument\'s IP address in its corresponding JSON file.'
            else:
                self.handle = visa.instrument(self.ipAddress)
                #set termination characters so instrument knows when to stop listening and execute a command
                self.handle.term_chars = self.terminationCharacters

        elif self.communicationProtocol is 'usb':
            #check if device can connect via usb
            if self.usbAddress is None:
                print 'Error. This instrument has not been configured to connect via usb. Please specify the instrument\'s usb address in its corresponding JSON file.'
            else:
                self.handle = visa.instrument(self.usbAddress)
                #set termination characters so instrument knows when to stop listening and execute a command
                self.handle.term_chars = self.terminationCharacters

    def disconnect(self):
        if self.communicationProtocol is 'serial':
            self.handle.close()
        elif self.communicationProtocol is 'ethernet':
            self.handle.close()
        elif self.communicationProtocol is 'usb':
            self.handle.close()

    def get_id(self):
        return self.send_command('get_id')

    def reset(self):
        return self.send_command('reset')

#dc power supply class
class DCPowerSupply(Instrument):
    def get_version(self):
        return self.send_command('get_version')

    def set_output(self, output):
        self.send_command('set_output', output)

    def set_voltage(self, voltage):
        self.send_command('set_voltage', voltage)

    def set_current(self, current):
        self.send_command('set_current', current)

    def get_voltage(self):
        return float(self.send_command('get_voltage'))

    def get_current(self):
        return float(self.send_command('get_current'))

    def get_programmed_voltage(self):
        return float(self.send_command('get_programmed_voltage'))

    def get_programmed_current(self):
        return float(self.send_command('get_programmed_current'))

    def set_range(self, range):
        self.send_command('set_range', range)

#electronic load class
class ElectronicLoad(Instrument):
    def set_input(self, input):
        self.write_command('set_input', input)

    def set_voltage(self, voltage):
        self.write_command('set_voltage', voltage)

    def set_current(self, current):
        self.write_command('set_current', current)

    def set_resistance(self, resistance):
        self.write_command('set_resistance', resistance)

    def set_range_current(self, range):
        self.write_command('set_range_current', range)

    def set_range_resistance(self, range):
        self.write_command('set_range_resistance', range)

    def set_slew_voltage(self, slew):
        self.write_command('set_slew_voltage', slew)

    def set_slew_current(self, slew):
        self.write_command('set_slew_current', slew)

    def set_mode(self, mode):
        self.write_command('set_mode', mode)

    def get_programmed_voltage(self):
        return float(self.send_command('get_programmed_voltage'))

    def get_programmed_current(self):
        return float(self.send_command('get_programmed_current'))

    def get_programmed_resistance(self):
        return float(self.send_command('get_programmed_resistance'))

    def get_voltage(self):
        return float(self.send_command('get_voltage'))

    def get_current(self):
        return float(self.send_command('get_current'))

    def get_power(self):
        return float(self.send_command('get_power'))

#oscilloscope class
class Oscilloscope(Instrument):
    def get_screen_capture(self):
        self.send_command('get_screen_capture')

#specific instrument classes
#dc power supplies
class AgilentE3631A(DCPowerSupply):
    def set_voltage_and_current(self, range, voltage, current):
        self.send_command('set_voltage_and_current', range, voltage, current)

class AgilentE3633A(DCPowerSupply):
    def set_voltage_and_current(self, voltage, current):
        self.send_command('set_voltage_and_current', voltage, current)

    def set_voltage_limit(self, voltageLimit):
        self.send_command('set_voltage_limit', voltageLimit)

    def set_current_limit(self, currentLimit):
        self.send_command('set_current_limit', currentLimit)

#electronic loads
class Agilent6060B(ElectronicLoad):
    def get_error(self):
        return self.send_command('get_error')

#oscilloscopes
class TektronixMSO4104BL(Oscilloscope):
    def get_screen_capture(self):
        if (self.communicationProtocol is 'usb') or (self.communicationProtocol is 'serial'):
            #globals
            WAIT_TIME = 0.5
            OUTPUT_WAVEFORMS_FILENAME = 'waveforms'
            OUTPUT_SCREENCAPTURE_FILENAME = 'screenCapture'
            OUTPUT_WAVEFORMS_FILE_EXTENSION = '.csv'
            OUTPUT_SCREENCAPTURE_FILE_EXTENSION = '.png'

            #send stop command to freeze waveforms
            self.handle.write("ACQuire:STATE STOP")

            drives = ['E:', 'F:']
            #attempt to write to both drives so the user does not have to specify which USB port they connected their thumb drive to
            for drive in drives:
                #create unique timestamped filename
                timestr = time.strftime('%Y%m%d-%H%M%S')
                #create directory to save screen captures and final csv file with all channel waveforms
                outputDir = os.path.join(drive, timestr + '-scope-capture')
                self.handle.write("FILESystem:MKDir \"" + outputDir + "\"")

                #save waveforms
                waveformsFilename = os.path.join(outputDir, OUTPUT_WAVEFORMS_FILENAME + OUTPUT_WAVEFORMS_FILE_EXTENSION)
                self.handle.write("SAVE:WAVEFORM ALL,\"" + waveformsFilename + "\"")
                while '1' in self.handle.ask("BUSY?"):
                        time.sleep(WAIT_TIME)

                #save screencapture
                screenCaptureFilename = os.path.join(outputDir, OUTPUT_SCREENCAPTURE_FILENAME + OUTPUT_SCREENCAPTURE_FILE_EXTENSION)
                self.handle.write("SAVE:IMAGE \"" + screenCaptureFilename + "\"")
                while '1' in self.handle.ask("BUSY?"):
                        time.sleep(WAIT_TIME)

            #send run command to unfreeze waveforms
            self.handle.write("ACQuire:STATE RUN")

        elif self.communicationProtocol is 'ethernet':
            #globals
            CHANNELS = ['ch1', 'ch2', 'ch3', 'ch4']
            OUTPUT_FORMAT = 'spreadsheet'
            OUTPUT_WAVEFORMS_FILENAME = 'waveforms'
            OUTPUT_SCREENCAPTURE_FILENAME = 'screenCapture'
            OUTPUT_WAVEFORMS_FILE_EXTENSION = '.csv'
            OUTPUT_SCREENCAPTURE_FILE_EXTENSION = '.png'
            ROW_OFFSET = 19

            #send stop command to freeze waveforms
            self.handle.write("ACQuire:STATE STOP")

            #create unique timestamped filename
            timestr = time.strftime('%Y%m%d-%H%M%S')
            #create temporary directory for individual channel waveform csv files
            tmpDir = timestr + '-scope-capture-tmp'
            os.mkdir(tmpDir)
            #create directory to save screen captures and final csv file with all channel waveforms
            outputDir = timestr + '-scope-capture'
            os.mkdir(outputDir)

            #save waveform to csv for each channel
            for channel in CHANNELS:
                br = mechanize.Browser()
                br.open('http://192.168.171.84:81/data/mso_data4.html')
                br.select_form(name='firstForm')
                channelControl = br.find_control('command')
                channelControl.value = ['select:control ' + channel]
                fileFormatControl = br.find_control('command1')
                fileFormatControl.value = ['save:waveform:fileformat ' + OUTPUT_FORMAT]
                response = br.submit()
                outputFile = open(os.path.join(tmpDir, channel + OUTPUT_WAVEFORMS_FILE_EXTENSION), "wb")
                outputFile.write(response.read())
                outputFile.close()

            #combine all csv channel waveform files into one
            csvDict = {}
            for channel in CHANNELS:
                f = open(os.path.join(tmpDir, channel + OUTPUT_WAVEFORMS_FILE_EXTENSION), 'rb')
                reader = csv.reader(f)
                rows = []
                for rowNumber, row in enumerate(reader):
                    if rowNumber < ROW_OFFSET:
                        rows.append(row)
                    else:
                        if len(row) > 0:
                            rows.append(row)
                csvDict[channel] = rows
                f.close()

            #check to make sure that all csv files had the same number of rows
            numRows = len(csvDict[CHANNELS[0]])
            for key in csvDict:
                if len(csvDict[key]) != numRows:
                    raise Exception('Error: The number of rows in the csv files for individual channels are not equal.')

            waveformsFilename = os.path.join(outputDir, OUTPUT_WAVEFORMS_FILENAME + OUTPUT_WAVEFORMS_FILE_EXTENSION)
            fout = open(waveformsFilename, 'wb')
            writer = csv.writer(fout)
            for row in range(numRows):
                rowList = []
                for numChannel, channel in enumerate(CHANNELS):
                    if row < ROW_OFFSET:
                        if numChannel is 0:
                            rowList += csvDict[channel][row]
                    else:
                        if numChannel is 0:
                            rowList += csvDict[channel][row]
                        else:
                            rowList += [csvDict[channel][row][1]]
                writer.writerow(rowList)

            #delete temporary directory
            shutil.rmtree(tmpDir)

            #get screencapture
            br = mechanize.Browser()
            html = br.open('http://192.168.171.84:81/control/control.html')
            bsoup = soup(html)
            image_tags = bsoup.findAll('img', {'id': 'thescreen'})
            image = image_tags[0]
            screenCaptureFilename = os.path.join(outputDir, OUTPUT_SCREENCAPTURE_FILENAME + OUTPUT_SCREENCAPTURE_FILE_EXTENSION)
            data = br.open(image['src']).read()
            br.back()
            save = open(screenCaptureFilename, 'wb')
            save.write(data)
            save.close()

            #send run command to unfreeze waveforms
            self.handle.write("ACQuire:STATE RUN")

