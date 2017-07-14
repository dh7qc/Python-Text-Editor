import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from tkinter import messagebox
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
        self.tabs = {} # { index, text widget }
        self.nb = ttk.Notebook(master)
        self.nb.bind("<Button-2>", self.close)

        # Override the X button.
        self.master.protocol('WM_DELETE_WINDOW', self.exit)
        
        # Create Menu Bar
        menubar = tk.Menu(self.master)
        
        # Create File Menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As...", command=self.save_as)
        filemenu.add_command(label="Close", command=self.close)
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
        
        # Create right-click menu.
        self.right_click_menu = tk.Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label="Undo", command=self.undo)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Cut", command=self.cut)
        self.right_click_menu.add_command(label="Copy", command=self.copy)
        self.right_click_menu.add_command(label="Paste", command=self.paste)
        self.right_click_menu.add_command(label="Delete", command=self.delete)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Select All", command=self.select_all)

        page_1 = ttk.Frame(self.nb)
        text_1 = self.create_text_window( page_1 )
        self.nb.add(page_1, text='Untitled')
        self.tabs[ self.nb.index( page_1 ) ] = text_1
        self.nb.pack(expand=1, fill="both")
        
    def create_text_window(self, frame):
        # Horizontal Scroll Bar 
        xscrollbar = tk.Scrollbar(frame, orient='horizontal')
        xscrollbar.pack(side='bottom', fill='x')
        
        # Vertical Scroll Bar
        yscrollbar = tk.Scrollbar(frame)
        yscrollbar.pack(side='right', fill='y')

        # Create Text Editor Box
        textbox = tk.Text(frame, relief='sunken', borderwidth=0, wrap='none')
        textbox.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, undo=True, autoseparators=True)

        # Keyboard / Click Bindings
        textbox.bind('<Control-s>', self.save_file)
        textbox.bind('<Control-o>', self.open_file)
        textbox.bind('<Control-n>', self.new_file)
        textbox.bind('<Control-a>', self.select_all)
        textbox.bind('<Button-3>', self.right_click)

        # Pack the textbox
        textbox.pack(fill='both', expand=True)

        # Get md5 hash of the initial state for comparison (to check for changes). 
        self.status = md5(textbox.get(1.0, 'end').encode('utf-8'))
        
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)
        
        return textbox

    def open_file(self, *args):
        # Prompt user to save file if there were changes, return if they cancel.
        if not self.save_changes():
            return
        
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
                self.tabs[ self.nb.index('current') ].delete(1.0, 'end')
                
                # Puts the contents of the file into the text widget.
                self.tabs[ self.nb.index('current') ].insert('end', file.read())
                
                # Update hash
                self.status = md5(tabs[ self.nb.index('current') ].get(1.0, 'end').encode('utf-8'))
            except:
                return

    def save_as(self):
        # Gets file directory and name of file to save.
        self.file_dir = (tkinter
         .filedialog
         .asksaveasfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes, defaultextension='.txt'))
        
        # Return if directory is still empty (user closes window without specifying file name).
        if not self.file_dir:
            return
         
        # Adds .txt suffix if not already included.
        if self.file_dir[len(self.file_dir)-5:] != '.txt':
            self.file_dir += '.txt'
            
        # Writes text widget's contents to file.
        file = open(self.file_dir, 'w')
        file.write(self.tabs[ self.nb.index('current') ].get(1.0, 'end'))
        file.close()
        
        # Update hash
        self.status = md5(self.tabs[ self.nb.index('current') ].get(1.0, 'end').encode('utf-8'))
        
    def save_file(self, *args):
        # If file directory is empty or Untitled, use save_as to get save information from user. 
        if not self.file_dir:
            self.save_as()

        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(self.file_dir, 'w') as file:
                file.write(self.tabs[ self.nb.index('current') ].get(1.0, 'end'))
                
            # Update hash
            self.status = md5(self.tabs[ self.nb.index('current') ].get(1.0, 'end').encode('utf-8'))
                
    def new_file(self, *args):        
        new_tab = ttk.Frame(self.nb)
        new_text = self.create_text_window( new_tab )
        self.nb.add(new_tab, text='Untitled')
        new_text.config(wrap= 'word' if self.word_wrap.get() else 'none')
        self.tabs[ self.nb.index( new_tab ) ] = new_text
        self.nb.select( new_tab )
        self.wrap( )
        
    def copy(self):
        # Clears the clipboard, copies selected contents.
        try: 
            sel = self.tabs[ self.nb.index('current') ].get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def delete(self):
        # Delete the selected text.
        try:
            self.tabs[ self.nb.index('current') ].delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def cut(self):
        # Copies selection to the clipboard, then deletes selection.
        try: 
            sel = self.tabs[ self.nb.index('current') ].get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.tabs[ self.nb.index('current') ].delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def wrap(self):
        if self.word_wrap.get() == True:
            for index in self.tabs:
                self.tabs[ index ].config(wrap="word")
        else:
            for index in self.tabs:
                self.tabs[ index ].config(wrap="none")
            
    def paste(self):
        self.tabs[ self.nb.index('current') ].insert(tk.INSERT, self.master.clipboard_get())
            
    def select_all(self, *args):
        # Selects / highlights all the text.
        self.tabs[ self.nb.index('current') ].tag_add(tk.SEL, "1.0", tk.END)
        
        # Set mark position to the end and scroll to the end of selection.
        self.tabs[ self.nb.index('current') ].mark_set(tk.INSERT, tk.END)
        self.tabs[ self.nb.index('current') ].see(tk.INSERT)

    def undo(self):
        self.tabs[ self.nb.index('current') ].edit_undo()

    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)
        
    def close(self, *args):
        # Make sure there is at least one tab still open.
        if self.nb.index("end") > 1:
            # self.tabs.pop( self.nb.index("current") )
            self.nb.forget( self.nb.index("current") )
        
    def exit(self):        
        # Check if any changes have been made.
        if self.save_changes():
            self.master.destroy()
        else:
            return
               
    def save_changes(self):
        # Check if any changes have been made, returns False if user chooses to cancel rather than select to save or not.
        if md5(self.tabs[ self.nb.index('current') ].get(1.0, 'end').encode('utf-8')).digest() != self.status.digest():
            # If changes were made since last save, ask if user wants to save.
            m = messagebox.askyesnocancel('Editor', 'Do you want to save changes to ' + ('Untitled' if not self.file_dir else self.file_dir) + '?' )
            
            # If None, cancel.
            if m is None:
                return False
            # else if True, save.
            elif m is True:
                self.save_file()
            # else don't save.
            else:
                pass
                
        return True

def main(): 
    root = tk.Tk()
    app = Editor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
    