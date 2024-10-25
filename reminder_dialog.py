# reminder_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
from typing import Callable, Dict, Any, List
import logging
import traceback
import webbrowser

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reminder.log'),
        logging.StreamHandler()
    ]
)

class ApplicationDetailsDialog(tk.Toplevel):
    """Dialog for showing detailed application information."""
    
    def __init__(self, parent: tk.Tk, application: Dict[str, Any], 
                 colors: Dict[str, str], callback: Callable):
        """Initialize the application details dialog."""
        try:
            super().__init__(parent)
            self.application = application
            self.colors = colors
            self.callback = callback
            
            self.title(f"Application Details - {application['company']}")
            self.geometry("600x500")
            self.configure(bg=colors['bg'])
            
            # Make dialog modal
            self.transient(parent)
            self.grab_set()
            
            # Initialize components
            self.status_var = None
            self.comments_text = None
            
            # Setup GUI
            self.setup_gui()
            self.load_data()
            self.center_window()
            
        except Exception as e:
            logging.error(f"Error initializing ApplicationDetailsDialog: {str(e)}")
            traceback.print_exc()
            raise
        
    def center_window(self) -> None:
        """Center dialog on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_gui(self) -> None:
        """Setup the dialog GUI."""
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Details section
        details_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Company and Position (read-only)
        fields = [
            ('Company:', self.application['company']),
            ('Position:', self.application['position']),
            ('Date Applied:', self.application['date']),
            ('Link:', self.application.get('link', ''))
        ]
        
        for idx, (label, value) in enumerate(fields):
            tk.Label(details_frame,
                    text=label,
                    bg=self.colors['bg'],
                    anchor='w',
                    width=12).grid(row=idx, column=0, sticky='w', pady=2)
            
            # Make link clickable if it's the link field
            if label == 'Link:' and value:
                link_label = tk.Label(details_frame,
                                    text=value,
                                    bg=self.colors['bg'],
                                    fg='blue',
                                    cursor='hand2',
                                    anchor='w')
                link_label.grid(row=idx, column=1, sticky='w', pady=2)
                link_label.bind('<Button-1>', lambda e: self.open_link())
            else:
                tk.Label(details_frame,
                        text=value,
                        bg=self.colors['bg'],
                        anchor='w').grid(row=idx, column=1, sticky='w', pady=2)
        
        # Status dropdown
        tk.Label(details_frame,
                text="Status:",
                bg=self.colors['bg'],
                anchor='w',
                width=12).grid(row=len(fields), column=0, sticky='w', pady=2)
                
        self.status_var = tk.StringVar(value=self.application['status'])
        self.status_combo = ttk.Combobox(
            details_frame,
            textvariable=self.status_var,
            values=['not_applied', 'applied', 'approved', 'rejected'],
            state='readonly',
            width=15
        )
        self.status_combo.grid(row=len(fields), column=1, sticky='w', pady=2)
        
        # Comments section
        tk.Label(main_frame,
                text="Comments:",
                bg=self.colors['bg'],
                anchor='w').pack(fill=tk.X, pady=(10, 5))
                
        self.comments_text = ScrolledText(main_frame, height=10)
        self.comments_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame,
                  text="Update",
                  command=self.update).pack(side=tk.LEFT, padx=5)
                  
        ttk.Button(button_frame,
                  text="Dismiss",
                  command=self.dismiss).pack(side=tk.LEFT, padx=5)
                  
        ttk.Button(button_frame,
                  text="Cancel",
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
    def load_data(self) -> None:
        """Load application data into form."""
        self.comments_text.delete('1.0', tk.END)
        self.comments_text.insert('1.0', self.application.get('comments', ''))
        
    def open_link(self, event=None) -> None:
        """Open the application link in default browser."""
        try:
            link = self.application.get('link')
            if link:
                webbrowser.open(link)
        except Exception as e:
            logging.error(f"Error opening link: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to open link: {str(e)}")
        
    def update(self) -> None:
        """Update application details."""
        try:
            updated_app = self.application.copy()
            updated_app['status'] = self.status_var.get()
            updated_app['comments'] = self.comments_text.get('1.0', 'end-1c')
            self.callback(updated_app, 'update')
            self.destroy()
        except Exception as e:
            logging.error(f"Error updating application: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to update application: {str(e)}")
        
    def dismiss(self) -> None:
        """Dismiss notification."""
        try:
            self.callback(self.application, 'dismiss')
            self.destroy()
        except Exception as e:
            logging.error(f"Error dismissing application: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to dismiss application: {str(e)}")

class ReminderDialog(tk.Toplevel):
    """Dialog for showing pending application updates."""
    
    def __init__(self, parent: tk.Tk, applications: List[Dict[str, Any]], 
                 colors: Dict[str, str], callback: Callable):
        """Initialize the reminder dialog."""
        try:
            super().__init__(parent)
            self.applications = applications
            self.colors = colors
            self.callback = callback
            
            self.title("Application Updates Reminder")
            self.geometry("800x600")
            self.configure(bg=colors['bg'])
            
            # Make dialog modal
            self.transient(parent)
            self.grab_set()
            
            # Initialize components
            self.tree = None
            self.button_frames = {}
            
            # Setup GUI
            self.setup_gui()
            self.center_window()
            
            # Bind events for window close
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            logging.error(f"Error initializing ReminderDialog: {str(e)}")
            traceback.print_exc()
            raise
        
    def center_window(self) -> None:
        """Center dialog on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_gui(self) -> None:
        """Setup the dialog GUI."""
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, 
                text=f"You have {len(self.applications)} applications to check for updates", 
                bg=self.colors['bg'],
                font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
                
        ttk.Button(header_frame,
                  text="Dismiss All",
                  command=self.dismiss_all).pack(side=tk.RIGHT)
        
        # Applications list
        list_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('company', 'position', 'status', 'date', 'id')
        self.tree = ttk.Treeview(list_frame,
                                columns=columns,
                                show='headings',
                                selectmode='browse')
        
        # Configure columns
        column_configs = {
            'company': ('Company', 200),
            'position': ('Position', 200),
            'status': ('Status', 100),
            'date': ('Date Applied', 100),
            'id': ('ID', 0)  # Hidden column
        }
        
        for col, (heading, width) in column_configs.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
            
        # Hide ID column
        self.tree.column('id', width=0, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame,
                                orient=tk.VERTICAL,
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load applications
        self.load_applications()
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Map>', self.update_button_positions)
        self.tree.bind('<Configure>', self.update_button_positions)
        self.tree.bind('<Visibility>', self.update_button_positions)
        
    def load_applications(self) -> None:
        """Load applications into the treeview."""
        try:
            for app in self.applications:
                item = self.tree.insert('', tk.END, values=(
                    app.get('company', ''),
                    app.get('position', ''),
                    app.get('status', ''),
                    app.get('date', ''),
                    str(app.get('id', ''))  # Ensure ID is string
                ))
                
                # Create dismiss button
                button_frame = tk.Frame(self.tree, bg=self.colors['bg'])
                ttk.Button(button_frame,
                          text="✕",
                          width=3,
                          command=lambda id=app['id']: self.dismiss_item(id)).pack()
                self.button_frames[str(app['id'])] = button_frame
                
            logging.info(f"Loaded {len(self.applications)} applications into tree")
            
        except Exception as e:
            logging.error(f"Error loading applications: {str(e)}")
            traceback.print_exc()
            
    def update_button_positions(self, event=None) -> None:
        """Update positions of dismiss buttons."""
        try:
            for item in self.tree.get_children():
                app_id = str(self.tree.item(item)['values'][-1])
                if app_id in self.button_frames:
                    bbox = self.tree.bbox(item, 'company')
                    if bbox:
                        x = bbox[2] + 400  # Position after the last visible column
                        y = bbox[1]
                        self.button_frames[app_id].place(x=x, y=y)
        except Exception as e:
            logging.error(f"Error updating button positions: {str(e)}")
            traceback.print_exc()
            
    def on_double_click(self, event) -> None:
        """Handle double-click on tree item."""
        try:
            selection = self.tree.selection()
            if not selection:
                return
                
            item = selection[0]
            values = self.tree.item(item)['values']
            app_id = str(values[-1]) if values else None
            
            if not app_id:
                return
                
            app = next((app for app in self.applications if str(app['id']) == app_id), None)
            if app:
                dialog = ApplicationDetailsDialog(self, app, self.colors, self.handle_details_action)
            
        except Exception as e:
            logging.error(f"Error showing details dialog: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", 
                               f"Failed to show application details: {str(e)}")
            
    def handle_details_action(self, application: Dict[str, Any], action: str) -> None:
        """Handle actions from details dialog."""
        try:
            if action == 'update':
                self.callback(application, 'update')
            else:
                self.callback(application, 'dismiss')
                
            # Remove from tree
            app_id = str(application['id'])
            for item in self.tree.get_children():
                if str(self.tree.item(item)['values'][-1]) == app_id:
                    self.tree.delete(item)
                    if app_id in self.button_frames:
                        self.button_frames[app_id].destroy()
                        del self.button_frames[app_id]
                    break
                    
            # Close dialog if no more items
            if not self.tree.get_children():
                self.destroy()
                
        except Exception as e:
            logging.error(f"Error handling details action: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to process action: {str(e)}")
            
    def dismiss_item(self, app_id: str) -> None:
        """Dismiss a single notification."""
        try:
            app_id = str(app_id)
            app = next((app for app in self.applications if str(app['id']) == app_id), None)
            if app:
                self.callback(app, 'dismiss')
                
                # Remove from tree
                for item in self.tree.get_children():
                    if str(self.tree.item(item)['values'][-1]) == app_id:
                        self.tree.delete(item)
                        if app_id in self.button_frames:
                            self.button_frames[app_id].destroy()
                            del self.button_frames[app_id]
                        break
                        
                # Close dialog if no more items
                if not self.tree.get_children():
                    self.destroy()
                    
        except Exception as e:
            logging.error(f"Error dismissing item: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to dismiss item: {str(e)}")
            
    def dismiss_all(self) -> None:
        """Dismiss all notifications."""
        try:
            for app in self.applications:
                self.callback(app, 'dismiss')
            self.destroy()
        except Exception as e:
            logging.error(f"Error dismissing all items: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to dismiss all items: {str(e)}")
            
    def on_closing(self) -> None:
        """Handle window closing."""
        try:
            if messagebox.askyesno("Confirm",
                                 "Do you want to dismiss all notifications?"):
                self.dismiss_all()
            else:
                self.destroy()
        except Exception as e:
            logging.error(f"Error handling window closing: {str(e)}")
            traceback.print_exc()
            self.destroy()