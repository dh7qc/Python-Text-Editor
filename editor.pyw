import tkinter as tk
import tkinter.filedialog
import os
from hashlib import md5

class Editor:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.filetypes = (("Normal text file", "*.txt"), ("all files", "*.*"))
        self.file_dir = ''
        self.init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        # Create Menu Bar
        menubar = tk.Menu(self.master)
        
        # Create File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save as...", command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)
        
        # Create Edit Menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo")
        editmenu.add_separator()
        editmenu.add_command(label="Cut")
        editmenu.add_command(label="Copy")
        editmenu.add_command(label="Paste")
        editmenu.add_command(label="Delete")
        editmenu.add_command(label="Select All")
        
        # Attach to Menu Bar
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        self.master.config(menu=menubar)

        # Horizontal Scroll Bar 
        xscrollbar = tk.Scrollbar(self.master, orient='horizontal')
        xscrollbar.pack(side='bottom', fill='x')
        
        # Vertical Scroll Bar
        yscrollbar = tk.Scrollbar(self.master)
        yscrollbar.pack(side='right', fill='y')
        
        # Create Text Editor Box
        textbox = self.textbox = tk.Text(self.master, relief='sunken', borderwidth=0, wrap='none')
        textbox.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        textbox.pack(fill='both')
        
        # Get md5 hash of the initial state for comparison (to check for changes). 
        self.status = md5(textbox.get(1.0, 'end').encode('utf-8'))
        
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)

    def open_file(self):
        # Open a window to browse to the file you would like to open, returns the directory.
        self.file_dir = (tkinter
         .filedialog
         .askopenfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes))
        
        # If directory is not the empty string, try to open the file. 
        if self.file_dir:
            try: 
                # Open the file.
                file = open(self.file_dir)
            
                # Clears the text widget.
                self.textbox.delete(1.0, 'end')
                
                # Puts the contents of the file into the text widget.
                self.textbox.insert('end', file.read())
                
                # Update hash
                self.status = md5(textbox.get(1.0, 'end').encode('utf-8'))
            except:
                return
                
    def save_as(self):
        # Gets file directory and name of file to save.
        self.file_dir = (tkinter
         .filedialog
         .asksaveasfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes))
        
        # Return if directory is still empty (user closes window without specifying file name).
        if not self.file_dir:
            return
         
        # Adds .txt suffix if not already included.
        if self.file_dir[len(self.file_dir)-5:] != '.txt':
            self.file_dir += '.txt'
            
        # Writes text widget's contents to file.
        file = open(self.file_dir, 'w')
        file.write(self.textbox.get(1.0, 'end'))
        file.close()
        
        # Update hash
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
        
    def save_file(self):
        # If file directory is empty, use save_as to get save information from user. 
        if not self.file_dir:
           self.save_as()

        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(self.file_dir, 'w') as file:
                file.write(self.textbox.get(1.0, 'end'))
                
            # Update hash
            self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
                
    def new(self):
        # Saves file if there are changes, resets directory, and clears text widget.
        if md5(self.textbox.get(1.0, 'end').encode('utf-8')).digest() != self.status.digest():
            self.save_file()
        self.file_dir = ''
        self.textbox.delete(1.0, 'end')
        
        # Update hash
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
        
    def exit(self):        
        # Destroy the editor window.
        self.master.destroy()
        
def main(): 
    root = tk.Tk()
    app = Editor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
    