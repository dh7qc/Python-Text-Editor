import tkinter as tk
import tkinter.filedialog
import os
from hashlib import md5

class Editor:
    def __init__(self, master):
        self.master = master
        self.master.title("Text Editor")
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.filetypes = (("Normal text file", "*.txt"), ("all files", "*.*"))
        self.file_dir = ''
        self.init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        # Create Menu Bar
        menubar = tk.Menu(self.master)
        
        # Create File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save as...", command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)
        
        # Create Edit Menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.cut)
        editmenu.add_command(label="Copy", command=self.copy)
        editmenu.add_command(label="Paste", command=self.paste)
        editmenu.add_command(label="Delete", command=self.delete)
        editmenu.add_command(label="Select All", command=self.select_all)
        
        # Create Format Menu, with a check button for word wrap.
        formatmenu = tk.Menu(menubar, tearoff=0)
        self.word_wrap = tk.BooleanVar()
        formatmenu.add_checkbutton(label="Word Wrap", onvalue=True, offvalue=False, variable=self.word_wrap, command=self.wrap)
        
        # Attach to Menu Bar
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Format", menu=formatmenu)
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
        
        # Keyboard / Click Bindings
        textbox.bind('<Control-s>', self.save_file)
        textbox.bind('<Control-o>', self.open_file)
        textbox.bind('<Control-n>', self.new_file)
        textbox.bind('<Button-3>', self.right_click)
           
        # Pack the textbox
        textbox.pack(fill='both')
        
        # Create right-click menu.
        self.right_click_menu = tk.Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label="Cut", command=self.cut)
        self.right_click_menu.add_command(label="Copy", command=self.copy)
        self.right_click_menu.add_command(label="Paste", command=self.paste)
        self.right_click_menu.add_command(label="Delete", command=self.delete)
       
        # Get md5 hash of the initial state for comparison (to check for changes). 
        self.status = md5(textbox.get(1.0, 'end').encode('utf-8'))
        
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)

    def open_file(self, *args):
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
        
    def save_file(self, *args):
        # If file directory is empty, use save_as to get save information from user. 
        if not self.file_dir:
            self.save_as()

        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(self.file_dir, 'w') as file:
                file.write(self.textbox.get(1.0, 'end'))
                
            # Update hash
            self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
                
    def new_file(self, *args):
        # Saves file if there are changes, resets directory, and clears text widget.
        if md5(self.textbox.get(1.0, 'end').encode('utf-8')).digest() != self.status.digest():
            self.save_file()
        self.file_dir = ''
        self.textbox.delete(1.0, 'end')
        
        # Update hash
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
        
    def copy(self):
        # Clears the clipboard, copies selected contents.
        try: 
            sel = self.textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def delete(self):
        # Delete the selected text.
        try:
            self.textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def cut(self):
        # Copies selection to the clipboard, then deletes selection.
        try: 
            sel = self.textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def wrap(self):
        if self.word_wrap.get() == True:
            self.textbox.config(wrap="word")
        else:
            self.textbox.config(wrap="none")
            
    def paste(self):
        self.textbox.insert(tk.INSERT, self.master.clipboard_get())
            
    def select_all(self):
        pass
        
    def undo(self):
        pass
        
    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)
        
    def exit(self):        
        # Destroy the editor window.
        self.master.destroy()
        
def main(): 
    root = tk.Tk()
    app = Editor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
    