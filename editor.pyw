import tkinter as tk

class Editor:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        
        # Create Menu Bar
        menubar = tk.Menu(self.master)
        
        # Create File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New")
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Save as...")
        filemenu.add_command(label="Close")
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
        xscrollbar = tk.Scrollbar(self.master, orient="horizontal")
        xscrollbar.pack(side="bottom", fill="x")
        
        # Vertical Scroll Bar
        yscrollbar = tk.Scrollbar(self.master)
        yscrollbar.pack(side="right", fill="y")
        
        # Create Text Editor Box
        textbox = tk.Text(self.master, relief="sunken", borderwidth=0, wrap="none")
        textbox.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
        textbox.pack(fill="both")
        
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)

    def open(self):
        pass
        
    def save(self):
        pass

    def exit(self):
        self.master.destroy()
        

def main(): 
    root = tk.Tk()
    app = Editor(root)
    root.mainloop()

if __name__ == '__main__':
    main()