# -*- coding: utf-8 -*-
'''
ScopeDisplay Viewer for DPO2000/3000/4000 TDS2000/3000 scopes
using Ethernet or USB connection. Also includes a Talk Listener,
Update instrument list button (for VISA resources) and Screen Capture.
Programed using
python 2.7 (http://www.python.org/)
pyvisa 1.3 (http://pypi.python.org/pypi/PyVISA/1.3)
Python Imaging Library V1.1.7 (http://www.pythonware.com/products/pil/)
Requires either TekVISA or NIVISA to be installed
SDV_MAIN.pyw handles setting up the graphical user interface and operation
SDV_VisaCmds.py  handles interfacing with the instrument
'''
'''
ScopeDisplay Viewer for DPO2000/3000/4000 TDS2000/3000 scopes
using Ethernet or USB connection. Also includes a Talk Listener,
Update instrument list button (for VISA resources) and Screen Capture.
Programed using
python 2.7 (http://www.python.org/)
pyvisa 1.3 (http://pypi.python.org/pypi/PyVISA/1.3)
Python Imaging Library V1.1.7 (http://www.pythonware.com/products/pil/)
Requires either TekVISA or NIVISA to be installed
SDV_MAIN.pyw handles setting up the graphical user interface and operation
SDV_VisaCmds.py  handles interfacing with the instrument

'''
from visa import *              # Basic VISA communication to instrument
from pyvisa import vpp43        # Communication to VISA drivers

#Create a list of instruments seen as resourced by visa, and return as array
def getinstrument():
    resource_names = []
    while True:
        try:
            find_list, return_counter, instrument_description = \
                  vpp43.find_resources(resource_manager.session, "?*")
            resource_names.append(instrument_description)
            break
        except VisaIOError:
            resource_names.append("ERROR: No Instruments Detected")
            return_counter = 0
            break
        except:
            resource_names.append("ERROR: Unable to communicate " \
                                  + "with VISA Driver")
            return_counter = 0
            break

    for i in xrange(return_counter - 1):
        resource_names.append(vpp43.find_next(find_list))

    return resource_names

# Return *IDN? from instrument, or error if unable to talk to scope
def IDinstrument(scope):
    while True:
        try:
            iam = str(scope.ask("*IDN?"))
            break
        except:
            iam = "ERROR: No response from Instrument"
            break
    return iam

# Connect to VISA resource and check communication. Scope object is returned
def makeInstr(identifier):
    while True:
        try:
            scope = instrument(identifier, timeout = 5)
            scope.ask("*IDN?")
            break
        except:
            scope = "ERROR: Unable to Communicate with this Resource"
            break
    return scope

# Check status of instrument if an error occurred
def checkerror(scope):
    while True:
        try:
            scope.ask("*ESR?")
            events = 'ERROR: ' + str(scope.ask("ALLEV?"))
            break
        except:
            events = "ERROR: Unable to Communicate with this Resource"
            break
    return events

# Read/Write to scope.  Commands can be forced as a read, write or ask
def VISA_TL(scope, command):
    while True:
        try:
            if '-w' in command[0:2]:
                scope.write(command[3:])
                return  command[3:]              
            elif '-r' in command[0:2]:
                return scope.read_raw()
            elif '-a' in command[0:2]:
                return scope.ask(command[3:])
            elif "?" in command:
                return (scope.ask(command))
            else:
                scope.write(command)
                worked = checkerror(scope)
                if "queue empty" in worked:
                    return command + " sent successfully"
                else:
                    return worked
            break
        except:
            return checkerror(scope)
            break

# Setup scope and get needed info to capture and save hardcopy
def HardCopySetup(scope):
    scopename = scope.ask("*IDN?").split(',')
    if 'TDS' in scopename[1] and  '20'  in scopename[1]:
        fileformat = 'TIF'
        scope.write("HARDCOPY:BUTTON SAVESIMAGE")
        scope.write("HARDCOPY:FORMAT TIFF")
        scope.write("HARDCOPY:PORT USB")      
    elif 'DPO' in scopename[1] or 'MSO' in scopename[1]:
        fileformat = 'PNG'
        scope.write(":header off")
        scope.write("wfmoutpre:bit_nr 8")
    elif 'TDS' in scopename[1] and '30' in scopename[1]:
        scope.write("HARDCOPY:PALETTE NORMAL")
        fileformat = 'BMP'
        scope.write("HARDCOPY:PORT GPIB")
        scope.write("HARDCOPY:FORMAT BMPColor")
       
    #Generic all model configure the scope hardcopy settings
    scope.write("header off")
    scope.write("VERBOSE OFF")
    scope.write("HARDCOPY:PREVIEW 0")
    scope.write("SAVE:IMAG:FILEF " + fileformat)
    filename = scopename[1] + '_' + scopename[2] +'_'+ '.' + fileformat
    return filename

# Grab hardcopy from scope and save as generic filename    
def CreateHardCopy(scope, filename):
    try:
        scope.write("HARDCOPY START")
        data = scope.read()
        scope.ask('*opc?')
    except VisaIOError:
        pass
    f = open(filename, 'wb')
    f.write(data)
    f.close()
    return filename
