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
from Tkinter import *               #Python Standard GUI builder
from SDV_VisaCmds import *       #Custom VISA commands library
import tkFileDialog                 #Dialog Box for saving files
from PIL import Image, ImageTk      #Used for Image support beyond GIF

#Main Application Frame
class App(Frame):
    def __init__(self):
        Frame.__init__( self )
        self.master.title("Scope Display Viewer")
        self.master.resizable(height=0, width=0)
        self.grid()
        # Variables used by GUI objects
        self.v = StringVar()
        self.status_text = StringVar()
        self.connectedto = StringVar()
        self.scope = ''
        self.status_text.set("Waiting")
        self.file_opt = self.options = {}
        self.DisplayState = 'stop'

        #First frame
        self.frame1 = Frame()
        self.frame1.grid(row=0)
        Label(self.frame1, text='Instrument List').grid(row=0, column = 1)
        self.b1=Button(self.frame1, text = 'Update List', width = 12, \
                       command = self.makeinstrlist)
        self.b1.grid(row=1, padx = 2, pady = 2)
        self.b3=Button(self.frame1, text = 'View Display',
                      command = self.ChangeRunState, state = DISABLED)
        self.b3.grid(row=3, padx = 2, pady = 2)
        self.instrumentlist = getinstrument()
        self.listbox = Listbox(self.frame1, height = len(self.instrumentlist), \
                               width = 35, exportselection=0)
        self.listbox.bind("<ButtonRelease-1>", self.CreateScope)
        self.listbox.grid(row = 1, column = 1, rowspan = \
                          len(self.instrumentlist), padx = 2, sticky = "n")
        self.l1 =Label(self.frame1, textvariable = self.connectedto,width = 35)
        self.l1.grid(column = 1, pady = 2)
        self.connectedto.set('Select and Instrument')
        # image frame
        self.imageframe = Toplevel()
        self.imageframe.withdraw()
        self.panel1 = Label(self.imageframe)
        self.imageframe.resizable(height=0, width=0)
        self.imageframe.protocol("WM_DELETE_WINDOW", self.handler)
        self.menubar = Menu(self.imageframe)
        self.menubar.add_command(label="Save Image", command=self.saveimage)
        self.imageframe.config(menu=self.menubar)

        # Second Frame Objects
        self.frame2 = Frame(relief = RAISED, borderwidth=2)
        self.frame2.grid(row=1)
        Label(self.frame2, text = "Talk/Listen Entry Line", anchor=SW, \
              justify=LEFT).grid(row = 1, column = 0)
        self.statusbar = Label(self.frame2, textvariable=self.status_text, bd=1, \
                               relief=SUNKEN, anchor=W, width = 60)
        self.statusbar.grid(row =3, column = 0, columnspan = 4, sticky = "w")
        self.talker = Entry(self.frame2, textvariable = self.v, width = 60)
        self.talker.bind("<Return>", self.TLcommand)
        self.talker.grid(row = 2, column = 0, columnspan = 4, \
                         sticky = "w", pady = 2)

       # last configuration of widgets
        self.makeinstrlist()
        
    # Populates the list box with Resources found in TekVISA
    def makeinstrlist(self):
        self.listbox.select_clear(0)
        self.selectedindex = ()
        self.scope = ''
        instrumentlist = getinstrument()
        self.listbox.delete(0, END)
        for a in instrumentlist:
            self.listbox.insert(END, a)
        self.listbox.config(height=len(instrumentlist))
        self.l1.grid_forget()
        self.listbox.grid(row = 1, column = 1, rowspan = \
                          len(self.instrumentlist), padx = 2, sticky = "n")
        self.l1.grid(column = 1, pady = 2)
        self.status_text.set("Instrument List Updated - Communication Reset")
        self.connectedto.set('Select and Instrument')
        self.b3.config(state = DISABLED)

    # Connects to a scope and saves it for passing to VisaCmds functions
    def CreateScope(self, event):
        self.selectedindex = self.listbox.curselection()
        clicked = self.listbox.get(self.selectedindex)
        self.listbox.select_anchor(self.selectedindex)
        if "ERROR" in clicked:
            self.status_text.set(clicked)
        else:
            self.scope = makeInstr(clicked)
            self.status_text.set("Selection set to " + clicked)
            scopename = IDinstrument(self.scope).split(',')[1]
            self.connectedto.set(scopename)
            self.b3.config(state = NORMAL)

    # Handles Talk-Listen line, if instrument is selected form list
    def TLcommand(self, event):
        if self.scope == '':
            self.status_text.set("Please select an Instrument")
        elif "ERROR" in self.listbox.get(self.selectedindex):
            self.status_text.set(self.listbox.selection_get())
            
        else:
            command = self.v.get()
            self.talker.delete(0, END)
            self.status_text.set(VISA_TL(self.scope,command))
          
    # Toggles state of showing the display
    def ChangeRunState(self):
        if self.DisplayState == 'stop':
            self.DisplayState = 'run'
            self.b3.config(text='Stop Viewer')
            self.filename = HardCopySetup(self.scope)
            self.GetImage()
        else:
            self.DisplayState = 'stop'
            self.b3.config(text='View Display')
        
    # Grabs a hardcopy from connected scope
    def GetImage(self):
        if self.DisplayState == 'run':
            self.capture = CreateHardCopy(self.scope, self.filename)
            self.image1 = ImageTk.PhotoImage(Image.open(self.capture))
            self.panel1.config(image=self.image1)
            self.panel1.grid()
            self.panel1.image = self.image1
            self.imageframe.state(newstate="normal")
            self.master.after(50, self.GetImage)

    # Closes the screen shot frame, without destroying the object
    def handler(self):
        self.imageframe.withdraw()

    # Dialog to save the screen capture where desired
    def saveimage(self):
        ext = self.filename.split('.')[1]
        self.options['filetypes'] = [('Image File', '.' + ext)]
        f1name = tkFileDialog.asksaveasfilename(**self.file_opt)
        if ('.' + ext) not in f1name:
            f1name = f1name + '.' + ext
        f1 = open(f1name, 'wb')
        f2 = open(self.filename, 'rb')
        data = f2.read()
        f1.write(data)
        f1.close()
        f2.close()
        
        
# Run this if this is the main program loaded
if __name__ == "__main__":
   App().mainloop()
