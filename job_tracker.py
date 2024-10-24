# job_tracker.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import traceback
from datetime import datetime
import webbrowser
import csv
import platform
from typing import Optional, Dict, List, Any
from data_manager import DataManager
from form_dialog import FormDialog

class JobTracker:
    """Main application class for the Job Application Tracker."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the Job Tracker application."""
        self.root = root
        self.root.title("Job Application Tracker")
        self.root.geometry("1200x800")
        
        # Theme settings
        self.is_dark_mode = tk.BooleanVar(value=False)
        self.set_theme()
        
        # Initialize data manager
        self.data_manager = DataManager("job_applications.json")
        self.applications = self.data_manager.load_data()
        
        # Sorting
        self.sort_by = "date"
        self.sort_reverse = True
        
        # Filters
        self.show_rejected = tk.BooleanVar(value=True)
        self.selected_country = tk.StringVar(value="All")
        
        # Setup GUI
        self.setup_gui()
        
        # Load initial data after GUI is ready
        self.root.after(100, self.initial_data_load)
        
    def initial_data_load(self) -> None:
        """Handle initial data loading and display."""
        self.refresh_list()
        if self.applications and self.tree.get_children():
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)
            self.tree.see(first_item)
            self.show_selected_details()
            
    def set_theme(self) -> None:
        """Configure application color scheme."""
        if self.is_dark_mode.get():
            self.colors = {
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'button': '#404040',
                'entry': '#363636',
                'table_bg': '#363636',
                'table_fg': '#ffffff',
                'highlight': '#4a4a4a'
            }
        else:
            self.colors = {
                'bg': '#ffffff',
                'fg': '#000000',
                'button': '#f0f0f0',
                'entry': '#ffffff',
                'table_bg': '#ffffff',
                'table_fg': '#000000',
                'highlight': '#e6e6e6'
            }
            
        self.root.configure(bg=self.colors['bg'])
        
        self.style = ttk.Style()
        self.style.configure('Custom.TButton',
                           background=self.colors['button'],
                           foreground=self.colors['fg'])
        self.style.configure('Custom.TEntry',
                           fieldbackground=self.colors['entry'],
                           foreground=self.colors['fg'])
        self.style.configure('Treeview',
                           background=self.colors['table_bg'],
                           foreground=self.colors['table_fg'],
                           fieldbackground=self.colors['table_bg'])
        
        self.update_widget_colors()
        
    def update_widget_colors(self) -> None:
        """Update colors of existing widgets."""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors['bg'])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=self.colors['bg'],
                                     fg=self.colors['fg'])
                    elif isinstance(child, tk.Frame):
                        child.configure(bg=self.colors['bg'])
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, tk.Label):
                                grandchild.configure(
                                    bg=self.colors['bg'],
                                    fg=self.colors['fg']
                                )
                                
    def setup_gui(self) -> None:
        """Setup the main GUI layout."""
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section for controls and table
        self.top_section = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.top_section.pack(fill=tk.BOTH, expand=True)
        
        # Setup controls
        self.setup_controls()
        
        # Setup table
        self.setup_application_list()
        
        # Setup details panel
        self.setup_details_panel()
        
    def setup_controls(self) -> None:
        """Setup control buttons and filters."""
        control_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Theme toggle
        ttk.Button(control_frame,
                  text="Toggle Theme",
                  style='Custom.TButton',
                  command=self.toggle_theme).pack(side=tk.LEFT, padx=5)
        
        # Add New button
        ttk.Button(control_frame,
                  text="Add New Application",
                  style='Custom.TButton',
                  command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        
        # Show/Hide rejected
        ttk.Checkbutton(control_frame,
                       text="Show Rejected",
                       variable=self.show_rejected,
                       command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        
        # Country filter
        self.update_country_filter(control_frame)
        
        # Export button
        ttk.Button(control_frame,
                  text="Export Data",
                  style='Custom.TButton',
                  command=self.export_data).pack(side=tk.RIGHT, padx=5)
        
    def update_country_filter(self, parent: tk.Frame) -> None:
        """Update country filter dropdown."""
        countries = ["All"] + sorted(list(set(
            app.get('country', '')
            for app in self.applications
            if app.get('country')
        )))
        
        country_filter = ttk.Combobox(parent,
                                    textvariable=self.selected_country,
                                    values=countries,
                                    state='readonly')
        country_filter.pack(side=tk.LEFT, padx=5)
        country_filter.bind('<<ComboboxSelected>>',
                          lambda e: self.refresh_list())
        
    def setup_application_list(self) -> None:
        """Setup the applications table."""
        table_frame = tk.Frame(self.top_section, bg=self.colors['bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Create treeview
        columns = ('company', 'position', 'date', 'location', 'status', 'id')
        self.tree = ttk.Treeview(table_frame,
                                columns=columns,
                                show='headings',
                                style='Treeview')
        
        # Configure columns
        column_configs = {
            'company': ('Company', 200),
            'position': ('Position', 200),
            'date': ('Date Applied', 100),
            'location': ('Location', 150),
            'status': ('Status', 100),
            'id': ('ID', 0)  # Hidden column
        }
        
        for col, (heading, width) in column_configs.items():
            self.tree.heading(col,
                            text=heading,
                            command=lambda c=col: self.sort_applications(c))
            self.tree.column(col, width=width)
        
        # Hide ID column
        self.tree.column('id', width=0, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame,
                                orient=tk.VERTICAL,
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.show_selected_details)
        
    def setup_details_panel(self) -> None:
        """Setup the details panel."""
        # Create panel
        self.details_panel = tk.Frame(self.main_container, bg=self.colors['bg'])
        
        # Add separator
        ttk.Separator(self.main_container,
                     orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Setup title frame
        title_frame = tk.Frame(self.details_panel, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(title_frame,
                text="Application Details",
                font=('Arial', 12, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(side=tk.LEFT)
        
        ttk.Button(title_frame,
                  text="Edit Application",
                  command=self.edit_application).pack(side=tk.RIGHT)
        
        # Create two columns
        details_columns = tk.Frame(self.details_panel, bg=self.colors['bg'])
        details_columns.pack(fill=tk.BOTH, expand=True)
        
        # Setup left column
        self.setup_details_left_column(details_columns)
        
        # Setup right column
        self.setup_details_right_column(details_columns)
        
        # Initially pack the panel
        self.details_panel.pack(fill=tk.BOTH, pady=(0, 10))
        
    def setup_details_left_column(self, parent: tk.Frame) -> None:
        """Setup left column of details panel."""
        left_col = tk.Frame(parent, bg=self.colors['bg'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Initialize variables
        self.details_vars = {}
        
        # Add fields
        fields = [
            ('Company:', 'company'),
            ('Position:', 'position'),
            ('Date Applied:', 'date'),
            ('Country:', 'country'),
            ('State/Province:', 'state'),
            ('Tracking Link:', 'link')
        ]
        
        for label_text, key in fields:
            frame = tk.Frame(left_col, bg=self.colors['bg'])
            frame.pack(fill=tk.X, pady=2)
            
            tk.Label(frame,
                    text=label_text,
                    width=15,
                    anchor='w',
                    bg=self.colors['bg'],
                    fg=self.colors['fg']).pack(side=tk.LEFT)
            
            self.details_vars[key] = tk.StringVar()
            value_label = tk.Label(frame,
                                 textvariable=self.details_vars[key],
                                 bg=self.colors['bg'],
                                 fg=self.colors['fg'],
                                 anchor='w')
            value_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Make link clickable
            if key == 'link':
                value_label.bind('<Button-1>', lambda e: self.open_link())
                value_label.config(fg='blue', cursor='hand2')
                
        # Add status dropdown
        self.setup_status_dropdown(left_col)
        
    def setup_status_dropdown(self, parent: tk.Frame) -> None:
        """Setup status dropdown in details panel."""
        status_frame = tk.Frame(parent, bg=self.colors['bg'])
        status_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(status_frame,
                text="Status:",
                width=15,
                anchor='w',
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(side=tk.LEFT)
        
        self.details_status_var = tk.StringVar()
        self.status_dropdown = ttk.Combobox(status_frame,
            textvariable=self.details_status_var,
            values=['not_applied', 'applied', 'approved', 'rejected'],
            state='readonly',
            width=15
        )
        self.status_dropdown.pack(side=tk.LEFT, padx=5)
        self.status_dropdown.bind('<<ComboboxSelected>>',
                                self.update_application_status)
        
    def setup_details_right_column(self, parent: tk.Frame) -> None:
        """Setup right column of details panel."""
        right_col = tk.Frame(parent, bg=self.colors['bg'])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Description section
        tk.Label(right_col,
                text="Job Description:",
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(anchor=tk.W)
        
        self.details_description = ScrolledText(right_col, height=6)
        self.details_description.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Comments section
        comments_frame = tk.Frame(right_col, bg=self.colors['bg'])
        comments_frame.pack(fill=tk.X)
        
        tk.Label(comments_frame,
                text="Comments:",
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(side=tk.LEFT)
        
        ttk.Button(comments_frame,
                  text="Save Comments",
                  command=self.save_comments).pack(side=tk.RIGHT)
        
        self.details_comments = ScrolledText(right_col, height=4)
        self.details_comments.pack(fill=tk.BOTH, expand=True)

    def show_add_dialog(self):
        """Show dialog for adding new application."""
        dialog = FormDialog(self.root, self.colors, self.handle_dialog_submit)
        
    def show_edit_dialog(self):
        """Show dialog for editing application."""
        if hasattr(self, 'current_app_id'):
            app = next((a for a in self.applications
                       if a['id'] == self.current_app_id), None)
            if app:
                dialog = FormDialog(self.root, self.colors,
                                  self.handle_dialog_submit, app)
                
    def handle_dialog_submit(self, application):
        """Handle form dialog submission."""
        if 'id' in application:  # Editing existing
            self.applications = [app for app in self.applications
                               if app['id'] != application['id']]
        self.applications.append(application)
        
        if self.data_manager.save_data(self.applications):
            self.refresh_list()
            
            # Select the new/updated application
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][-1] == application['id']:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
        else:
            messagebox.showerror("Error", "Failed to save application.")

    def show_selected_details(self, event=None) -> None:
        """Display details of selected application."""
        selection = self.tree.selection()
        if not selection:
            self.details_panel.pack_forget()
            return
            
        try:
            item = selection[0]
            values = self.tree.item(item)['values']
            if not values:
                return
                
            app_id = str(values[-1])  # Ensure ID is string
            app = next((a for a in self.applications
                       if str(a['id']).strip() == app_id.strip()), None)
            
            if not app:
                return
            
            # Show details panel if it's hidden
            if not self.details_panel.winfo_ismapped():
                self.details_panel.pack(fill=tk.BOTH, pady=(0, 10))
            
            # Update fields
            self.details_vars['company'].set(app.get('company', ''))
            self.details_vars['position'].set(app.get('position', ''))
            self.details_vars['date'].set(app.get('date', ''))
            self.details_vars['country'].set(app.get('country', ''))
            self.details_vars['state'].set(app.get('state', ''))
            self.details_vars['link'].set(app.get('link', ''))
            
            # Update status
            self.details_status_var.set(app.get('status', 'not_applied'))
            
            # Update description
            self.details_description.config(state='normal')
            self.details_description.delete('1.0', tk.END)
            self.details_description.insert('1.0', app.get('description', ''))
            self.details_description.config(state='disabled')
            
            # Update comments
            self.details_comments.delete('1.0', tk.END)
            self.details_comments.insert('1.0', app.get('comments', ''))
            
            # Store current application id
            self.current_app_id = app_id
            
        except Exception as e:
            logging.error(f"Error displaying details: {str(e)}")
            traceback.print_exc()
            
    def toggle_theme(self) -> None:
        """Toggle between light and dark theme."""
        self.is_dark_mode.set(not self.is_dark_mode.get())
        self.set_theme()
        
    def open_link(self) -> None:
        """Open tracking link in browser."""
        link = self.details_vars['link'].get()
        if link:
            webbrowser.open(link)
            
    def update_application_status(self, event=None) -> None:
        """Update status of current application."""
        if hasattr(self, 'current_app_id'):
            new_status = self.details_status_var.get()
            
            # Update application
            for app in self.applications:
                if app['id'] == self.current_app_id:
                    app['status'] = new_status
                    break
                    
            # Save and refresh
            if self.data_manager.save_data(self.applications):
                self.refresh_list()
                
                # Reselect the item
                for item in self.tree.get_children():
                    if self.tree.item(item)['values'][-1] == self.current_app_id:
                        self.tree.selection_set(item)
                        break

    def save_comments(self) -> None:
        """Save comments for current application."""
        if hasattr(self, 'current_app_id'):
            new_comments = self.details_comments.get('1.0', tk.END).strip()
            
            # Update application
            for app in self.applications:
                if app['id'] == self.current_app_id:
                    app['comments'] = new_comments
                    break
                    
            # Save data
            if self.data_manager.save_data(self.applications):
                messagebox.showinfo("Success", "Comments saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save comments.")
                
    def sort_applications(self, key: str) -> None:
        """Sort applications by given key."""
        if self.sort_by == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = key
            self.sort_reverse = False
        self.refresh_list()
        
    def refresh_list(self) -> None:
        """Refresh the applications list."""
        # Save selected item
        selected_id = None
        selection = self.tree.selection()
        if selection:
            selected_id = self.tree.item(selection[0])['values'][-1]
            
        # Clear current list
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Filter applications
        filtered_apps = self.applications
        if not self.show_rejected.get():
            filtered_apps = [app for app in filtered_apps
                           if app['status'] != 'rejected']
            
        if self.selected_country.get() != "All":
            filtered_apps = [app for app in filtered_apps
                           if app.get('country') == self.selected_country.get()]
            
        # Sort applications
        key = self.sort_by
        filtered_apps.sort(key=lambda x: x.get(key, ''),
                         reverse=self.sort_reverse)
        
        # Insert applications
        for app in filtered_apps:
            location = f"{app.get('country', '')}"
            if app.get('state'):
                location += f", {app['state']}"
            
            item = self.tree.insert('', tk.END, values=(
                app.get('company', ''),
                app.get('position', ''),
                app.get('date', ''),
                location,
                app.get('status', '').replace('_', ' ').title(),
                app.get('id', '')
            ))
            
            # Reselect previously selected item
            if selected_id and app['id'] == selected_id:
                self.tree.selection_set(item)
                self.tree.see(item)
                
        # Select first item if nothing is selected
        if not self.tree.selection() and self.tree.get_children():
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)
            self.show_selected_details()
    
    def edit_application(self):
        """Show dialog for editing current application."""
        self.show_edit_dialog()
            
    def export_data(self) -> None:
        """Export data to different formats."""
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Data")
        export_window.geometry("300x200")
        export_window.configure(bg=self.colors['bg'])
        
        def export_to_format(format_type: str) -> None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            try:
                if format_type == 'json':
                    self._export_json(timestamp)
                elif format_type == 'csv':
                    self._export_csv(timestamp)
                elif format_type == 'txt':
                    self._export_txt(timestamp)
                    
                messagebox.showinfo("Success",
                                  f"Data exported to job_applications_{timestamp}.{format_type}")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
                
        # Export buttons
        tk.Label(export_window,
                text="Choose export format:",
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(pady=10)
        
        for format_type in ['JSON', 'CSV', 'TXT']:
            ttk.Button(
                export_window,
                text=f"Export as {format_type}",
                style='Custom.TButton',
                command=lambda f=format_type.lower(): export_to_format(f)
            ).pack(pady=5)
        
        # Close button
        ttk.Button(export_window,
                  text="Close",
                  style='Custom.TButton',
                  command=export_window.destroy).pack(pady=10)
                  
    def _export_json(self, timestamp: str) -> None:
        """Export data to JSON format."""
        filename = f'job_applications_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.applications, f, indent=2, ensure_ascii=False)
            
    def _export_csv(self, timestamp: str) -> None:
        """Export data to CSV format."""
        filename = f'job_applications_{timestamp}.csv'
        fieldnames = [
            'company', 'position', 'date', 'country', 'state',
            'status', 'link', 'description', 'comments'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.applications)
            
    def _export_txt(self, timestamp: str) -> None:
        """Export data to text format."""
        filename = f'job_applications_{timestamp}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            for app in self.applications:
                f.write(f"Company: {app['company']}\n")
                f.write(f"Position: {app['position']}\n")
                f.write(f"Date Applied: {app['date']}\n")
                f.write(f"Location: {app['country']}")
                if app['state']:
                    f.write(f", {app['state']}")
                f.write("\n")
                f.write(
                    f"Status: {app['status'].replace('_', ' ').title()}\n"
                )
                if app['link']:
                    f.write(f"Tracking Link: {app['link']}\n")
                if app['description']:
                    f.write(f"Description: {app['description']}\n")
                if app['comments']:
                    f.write(f"Comments: {app['comments']}\n")
                f.write("-" * 50 + "\n\n")

def main():
    """Main entry point for the application."""
    try:
        # Set DPI awareness for Windows
        if platform.system() == "Windows":
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        logging.error(f"Failed to set DPI awareness: {str(e)}")
    
    root = tk.Tk()
    app = JobTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()