# form_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

class FormDialog(tk.Toplevel):
    """Dialog window for adding/editing job applications."""
    
    def __init__(self, parent, colors, callback, application=None):
        """Initialize the form dialog.
        
        Args:
            parent: Parent window
            colors: Dictionary of color scheme
            callback: Function to call on successful submission
            application: Optional existing application data for editing
        """
        super().__init__(parent)
        self.colors = colors
        self.callback = callback
        self.application = application
        
        # Configure window
        self.title("Add Application" if not application else "Edit Application")
        self.configure(bg=self.colors['bg'])
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize variables
        self.form_vars = {}
        
        # Setup GUI
        self.setup_gui()
        
        # Center window
        self.center_window()
        
        # Load data if editing
        if application:
            self.load_application_data()
            
    def center_window(self):
        """Center the dialog window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_gui(self):
        """Setup the dialog GUI."""
        # Main container
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create two columns
        form_columns = tk.Frame(main_frame, bg=self.colors['bg'])
        form_columns.pack(fill=tk.BOTH, expand=True)
        
        # Setup columns
        self.setup_left_column(form_columns)
        self.setup_right_column(form_columns)
        
        # Setup buttons
        self.setup_buttons(main_frame)
        
    def setup_left_column(self, parent):
        """Setup left column of form."""
        left_col = tk.Frame(parent, bg=self.colors['bg'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Form fields
        fields = [
            ('Company Name:', 'company', True),
            ('Position:', 'position', True),
            ('Country:', 'country', False),
            ('State/Province:', 'state', False),
            ('Tracking Link:', 'link', False)
        ]
        
        for label_text, field, required in fields:
            frame = tk.Frame(left_col, bg=self.colors['bg'])
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame,
                    text=label_text + (' *' if required else ''),
                    bg=self.colors['bg'],
                    fg=self.colors['fg'],
                    width=15,
                    anchor='w').pack(side=tk.LEFT)
            
            self.form_vars[field] = tk.StringVar()
            ttk.Entry(frame,
                     textvariable=self.form_vars[field]).pack(side=tk.LEFT,
                                                            fill=tk.X,
                                                            expand=True,
                                                            padx=5)
        
        # Status dropdown
        status_frame = tk.Frame(left_col, bg=self.colors['bg'])
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame,
                text="Status:",
                bg=self.colors['bg'],
                fg=self.colors['fg'],
                width=15,
                anchor='w').pack(side=tk.LEFT)
        
        self.form_vars['status'] = tk.StringVar(value="not_applied")
        ttk.Combobox(status_frame,
                    textvariable=self.form_vars['status'],
                    values=['not_applied', 'applied', 'approved', 'rejected'],
                    state='readonly').pack(side=tk.LEFT, padx=5)
                    
    def setup_right_column(self, parent):
        """Setup right column of form."""
        right_col = tk.Frame(parent, bg=self.colors['bg'])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Description
        tk.Label(right_col,
                text="Job Description:",
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(anchor=tk.W)
        
        self.description_text = ScrolledText(right_col, height=10)
        self.description_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Comments
        tk.Label(right_col,
                text="Comments:",
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(anchor=tk.W)
        
        self.comments_text = ScrolledText(right_col, height=5)
        self.comments_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_buttons(self, parent):
        """Setup form buttons."""
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame,
                  text="Submit",
                  command=self.submit).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame,
                  text="Cancel",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
                  
    def load_application_data(self):
        """Load existing application data into form."""
        for field in self.form_vars:
            if field in self.application:
                self.form_vars[field].set(self.application[field])
        
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', self.application.get('description', ''))
        
        self.comments_text.delete('1.0', tk.END)
        self.comments_text.insert('1.0', self.application.get('comments', ''))
        
    def get_form_data(self):
        """Get data from form fields."""
        application = {
            'company': self.form_vars['company'].get().strip(),
            'position': self.form_vars['position'].get().strip(),
            'country': self.form_vars['country'].get().strip(),
            'state': self.form_vars['state'].get().strip(),
            'link': self.form_vars['link'].get().strip(),
            'status': self.form_vars['status'].get(),
            'description': self.description_text.get('1.0', tk.END).strip(),
            'comments': self.comments_text.get('1.0', tk.END).strip(),
        }
        
        if self.application:  # If editing
            application['id'] = self.application['id']
            application['date'] = self.application['date']
        else:  # If adding new
            application['date'] = datetime.now().strftime('%Y-%m-%d')
            application['id'] = datetime.now().strftime('%Y%m%d%H%M%S')
            
        return application
        
    def validate_form(self):
        """Validate form data."""
        if not self.form_vars['company'].get().strip():
            messagebox.showerror("Error", "Company name is required!")
            return False
        if not self.form_vars['position'].get().strip():
            messagebox.showerror("Error", "Position is required!")
            return False
        return True
        
    def submit(self):
        """Handle form submission."""
        if not self.validate_form():
            return
            
        application = self.get_form_data()
        self.callback(application)
        self.destroy()