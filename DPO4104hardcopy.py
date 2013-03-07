#-------------------------------------------------------------------------------
#  Get a screen catpure from DPO4000 series scope and save it to a file

# python 2.7 (http://www.python.org/)
# pyvisa 1.4 (http://pyvisa.sourceforge.net/)
#-------------------------------------------------------------------------------
import visa

scope = visa.instrument('USB0::0x0699::0x0401::No_Serial::INSTR')
print scope.ask('*IDN?')

scope.write('SAVE:IMAG:FILEF PNG')
scope.write('HARDCOPY START')
raw_data = scope.read_raw()


fid = open('my_image.png', 'wb')
fid.write(raw_data)
fid.close()
print 'Done'
