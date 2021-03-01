import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from tkinter import messagebox
import os
from hashlib import md5

class Document:
    def __init__(self, Frame, TextWidget, FileDir=''):
        self.file_dir = FileDir
        self.file_name = 'Untitled' if not FileDir else os.path.basename(FileDir)
        self.textbox = TextWidget
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
        
class Editor:
    def __init__(self, master):
        self.master = master
        self.master.title("Notepad+=1")
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        
        self.filetypes = (("Normal text file", "*.txt"), ("all files", "*.*"))
        self.init_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        self.tabs = {} # { index, text widget }
        
        # Create Notebook ( for tabs ).
        self.nb = ttk.Notebook(master)
        self.nb.bind("<Button-2>", self.close_tab)
        self.nb.bind("<B1-Motion>", self.move_tab)
        self.nb.pack(expand=1, fill="both")
        self.nb.enable_traversal()
        #self.nb.bind('<<NotebookTabChanged>>', self.tab_change)

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
        filemenu.add_command(label="Close", command=self.close_tab)
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
        
        # Create tab right-click menu
        self.tab_right_click_menu = tk.Menu(self.master, tearoff=0)
        self.tab_right_click_menu.add_command(label="New Tab", command=self.new_file)
        self.nb.bind('<Button-3>', self.right_click_tab)

        # Create Initial Tab
        first_tab = ttk.Frame(self.nb)
        self.tabs[ first_tab ] = Document( first_tab, self.create_text_widget(first_tab) )
        self.nb.add(first_tab, text='Untitled')

    def create_text_widget(self, frame):
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
        textbox.bind('<Control-w>', self.close_tab)
        textbox.bind('<Button-3>', self.right_click)

        # Pack the textbox
        textbox.pack(fill='both', expand=True)        
        
        # Configure Scrollbars
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)
        
        return textbox

    def open_file(self, *args):        
        # Open a window to browse to the file you would like to open, returns the directory.
        file_dir = (tkinter
         .filedialog
         .askopenfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes))
        
        # If directory is not the empty string, try to open the file. 
        if file_dir:
            try:
                # Open the file.
                file = open(file_dir)
                
                # Create a new tab.
                new_tab = ttk.Frame(self.nb)
                self.tabs[ new_tab ] = Document(new_tab, self.create_text_widget(new_tab), file_dir)
                self.nb.add(new_tab, text=os.path.basename(file_dir))
                self.nb.select( new_tab )
                            
                # Puts the contents of the file into the text widget.
                self.tabs[ new_tab ].textbox.insert('end', file.read())
                
                # Update hash
                self.tabs[ new_tab ].status = md5(tabs[ new_tab ].textbox.get(1.0, 'end').encode('utf-8'))
            except:
                return

    def save_as(self):
        curr_tab = self.get_tab()
    
        # Gets file directory and name of file to save.
        file_dir = (tkinter
         .filedialog
         .asksaveasfilename(initialdir=self.init_dir, title="Select file", filetypes=self.filetypes, defaultextension='.txt'))
        
        # Return if directory is still empty (user closes window without specifying file name).
        if not file_dir:
            return
         
        # Adds .txt suffix if not already included.
        if file_dir[-4:] != '.txt':
            file_dir += '.txt'
            
        self.tabs[ curr_tab ].file_dir = file_dir
        self.tabs[ curr_tab ].file_name = os.path.basename(file_dir)
        self.nb.tab( curr_tab, text=self.tabs[ curr_tab ].file_name) 
            
        # Writes text widget's contents to file.
        file = open(file_dir, 'w')
        file.write(self.tabs[ curr_tab ].textbox.get(1.0, 'end'))
        file.close()
        
        # Update hash
        self.tabs[ curr_tab ].status = md5(self.tabs[ curr_tab ].textbox.get(1.0, 'end').encode('utf-8'))
        
    def save_file(self, *args):
        curr_tab = self.get_tab()
        
        # If file directory is empty or Untitled, use save_as to get save information from user. 
        if not self.tabs[ curr_tab ].file_dir:
            self.save_as()

        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(self.tabs[ curr_tab ].file_dir, 'w') as file:
                file.write(self.tabs[ curr_tab ].textbox.get(1.0, 'end'))
                
            # Update hash
            self.tabs[ curr_tab ].status = md5(self.tabs[ curr_tab ].textbox.get(1.0, 'end').encode('utf-8'))
                
    def new_file(self, *args):                
        # Create new tab
        new_tab = ttk.Frame(self.nb)
        self.tabs[ new_tab ] = Document(new_tab, self.create_text_widget(new_tab))
        self.tabs[ new_tab ].textbox.config(wrap= 'word' if self.word_wrap.get() else 'none')
        self.nb.add(new_tab, text='Untitled')
        self.nb.select( new_tab )
        
    def copy(self):
        # Clears the clipboard, copies selected contents.
        try: 
            sel = self.tabs[ self.get_tab() ].textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def delete(self):
        # Delete the selected text.
        try:
            self.tabs[ self.get_tab() ].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def cut(self):
        # Copies selection to the clipboard, then deletes selection.
        try: 
            sel = self.tabs[ self.get_tab() ].textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            self.tabs[ self.get_tab() ].textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def wrap(self):
        if self.word_wrap.get() == True:
            for index in self.tabs:
                self.tabs[ index ].textbox.config(wrap="word")
        else:
            for index in self.tabs:
                self.tabs[ index ].textbox.config(wrap="none")
            
    def paste(self):
        try: 
            self.tabs[ self.get_tab() ].textbox.insert(tk.INSERT, self.master.clipboard_get())
        except tk.TclError:
            pass
            
    def select_all(self, *args):
        curr_tab = self.get_tab()
        
        # Selects / highlights all the text.
        self.tabs[ curr_tab ].textbox.tag_add(tk.SEL, "1.0", tk.END)
        
        # Set mark position to the end and scroll to the end of selection.
        self.tabs[ curr_tab ].textbox.mark_set(tk.INSERT, tk.END)
        self.tabs[ curr_tab ].textbox.see(tk.INSERT)

    def undo(self):
        self.tabs[ self.get_tab() ].textbox.edit_undo()

    def right_click(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)
        
    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)
        
    def close_tab(self, event=None):
        # Close the current tab if close is selected from file menu, or keyboard shortcut.
        if event is None or event.type == str( 2 ):
            selected_tab = self.get_tab()
        # Otherwise close the tab based on coordinates of center-click.
        else:
            try:
                index = event.widget.index('@%d,%d' % (event.x, event.y))
                selected_tab = self.nb._nametowidget( self.nb.tabs()[index] )
            except tk.TclError:
                return

        # Prompt to save changes before closing tab
        if self.save_changes():
            self.nb.forget( selected_tab )
            self.tabs.pop( selected_tab )

        # Exit if last tab is closed
        if self.nb.index("end") == 0:
            self.master.destroy()
        
    def exit(self):        
        # Check if any changes have been made.
        if self.save_changes():
            self.master.destroy()
        else:
            return
               
    def save_changes(self):
        curr_tab = self.get_tab()
        file_dir = self.tabs[ curr_tab ].file_dir
        
        # Check if any changes have been made, returns False if user chooses to cancel rather than select to save or not.
        if md5(self.tabs[ curr_tab ].textbox.get(1.0, 'end').encode('utf-8')).digest() != self.tabs[ curr_tab ].status.digest():
            # If changes were made since last save, ask if user wants to save.
            m = messagebox.askyesnocancel('Editor', 'Do you want to save changes to ' + ('Untitled' if not file_dir else file_dir) + '?' )
            
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
    
    # Get the object of the current tab.
    def get_tab(self):
        return self.nb._nametowidget( self.nb.select() )
        
    def move_tab(self, event):
        '''
        Check if there is more than one tab.
        
        Use the y-coordinate of the current tab so that if the user moves the mouse up / down 
        out of the range of the tabs, the left / right movement still moves the tab.
        '''
        if self.nb.index("end") > 1:
            y = self.get_tab().winfo_y() - 5
            
            try:
                self.nb.insert( event.widget.index('@%d,%d' % (event.x, y)), self.nb.select() )
            except tk.TclError:
                return

def main(): 
    root = tk.Tk()
    app = Editor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
    