#-------------------------------------------------------------------------------
#  Get a screen catpure from DPO4000 series scope and save it to a file

# python 2.7 (http://www.python.org/)
# pyvisa 1.4 (http://pyvisa.sourceforge.net/)
#-------------------------------------------------------------------------------
import visa

scope = visa.instrument('TCPIP::134.62.36.164::INSTR')
print scope.ask('*IDN?')
scope.write('HARDCOPY:PORT FILE')
scope.write('HARDCOPY:FILENAME \'c:\\TEMP.PNG\'')
scope.write('HARDCOPY START')
scope.write('FILESYSTEM:READFILE \'c:\\TEMP.PNG\'')
data = scope.read()
scope.write('FILESYSTEM:DELETE \'c:\\TEMP.PNG\'')
fid = open('my_image.png', 'wb')
fid.write(data)
fid.close()
print 'Done'
