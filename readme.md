# Job Application Tracker

A desktop application built with Python and Tkinter for tracking job applications. Keep track of your job search progress, application statuses, and important details in a clean, user-friendly interface.

![Job Tracker UI](https://raw.githubusercontent.com/haroonalhadisk/job-application-tracker/refs/heads/main/screenshots/main.png)

## Features

- 📝 **Track Job Applications**
  - Company details
  - Position information
  - Application dates
  - Status tracking (Not Applied → Applied → Approved/Rejected)
  - Location details (Country/State)
  - Application links
  - Job descriptions
  - Personal comments

- 🔔 **Smart Notifications**
  - Daily reminders for pending updates
  - Status-based notifications
  - Bulk or individual dismissal
  - Automatic 24-hour reset

- 🔍 **Advanced Management**
  - Sort applications by any field
  - Filter by status and location
  - Quick status updates
  - Detailed application view
  - Edit existing applications

- 📤 **Data Export**
  - Export to JSON format
  - Export to CSV format
  - Export to TXT format

## Installation

### Automatic Installation (Recommended)

1. Download the latest release from the GitHub releases page
2. Extract the ZIP file to your desired location
3. Run `installer.bat`
4. Choose your installation method:
   - **Option 1**: Standalone Version (Portable)
   - **Option 2**: System Installation (Program Files)
5. Follow the on-screen instructions

### Manual Installation

If the installer doesn't work, follow these steps:

1. Ensure Python 3.7+ is installed
   - Download from [Python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. Download and extract the application files

3. Install required packages:
   ```bash
   pip install tkinter
   ```

4. Launch the application:
   - Double-click `launch.bat` (Normal mode)
   - Or `launch_with_console.bat` (Debug mode)
   
   If the BAT files don't work, run directly with Python:
   ```bash
   python job_tracker.py
   ```

## Usage Guide

### Adding a New Application

1. Click "Add New Application" button
2. Fill in the required fields:
   - Company Name*
   - Position*
   - Country (optional)
   - State/Province (optional)
   - Tracking Link (optional)
3. Select the application status
4. Add job description and comments if desired
5. Click "Submit"

### Managing Applications

- **View Details**: Click any application in the list
- **Edit Application**: Select an application and click "Edit Application"
- **Update Status**: Use the status dropdown in the details panel
- **Add Comments**: Type in the comments section and click "Save Comments"
- **Delete Application**: Select an application and click "Delete Selected"
- **Open Links**: Click the tracking link in the details panel

### Using Filters and Sorting

- Toggle "Show Rejected" to hide/show rejected applications
- Use the country dropdown to filter by location
- Click column headers to sort by that field
- Click again to reverse sort order

### Handling Notifications

- Toggle "Show Update Reminders" to enable/disable notifications
- Click "✕" to dismiss individual notifications
- Use "Dismiss All" to clear all notifications
- Double-click a notification for detailed view
- Update application status directly from notifications

### Exporting Data

1. Click "Export Data"
2. Choose your preferred format:
   - JSON (Complete data backup)
   - CSV (Spreadsheet compatible)
   - TXT (Human-readable format)
3. Find exported file in the application directory

## File Locations

- **Application Data**: `job_applications.json`
- **Notification States**: `notifications_state.json`
- **Log Files**: 
  - `job_tracker.log`
  - `notifications.log`

## Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Verify Python installation
   - Check error messages in console mode
   - Ensure all files are present

2. **Data Not Saving**
   - Check write permissions
   - Verify JSON files aren't locked
   - Launch in console mode for error messages

3. **UI Issues**
   - Update Python to latest version
   - Check system DPI settings
   - Try running in compatibility mode

### Data Recovery

The application maintains backup files:
- `job_applications.json.bak`
- `notifications_state.json.bak`

To recover:
1. Close the application
2. Remove the corrupted `.json` file
3. Rename the `.bak` file (remove `.bak`)
4. Restart the application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Look through existing GitHub issues
3. Create a new issue with:
   - Detailed description
   - Steps to reproduce
   - Error messages
   - System information

---