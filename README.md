# TACT Calendar4

TACT Calendar4 is a project for automatically retrieving weekly class schedules from TACT's publicly available timetables at regular intervals.

## Project Preview

You can view a preview of the project's output at [this Google Sheets link](https://docs.google.com/spreadsheets/d/1wlaknyDTFavd-k-YITlGyrFuIDn-XzhSp45QIysNriM/preview).

## Project Structure

```
tactcalendar4/
│
├── env/                    # Virtual environment (not tracked in git)
├── .env                    # Environment variables (keep this private!)
├── .gitignore              # Git ignore file
├── tactcalendar.service    # Systemd service file
├── manager.sh              # Shell script to run the manager
├── requirements.txt        # Python dependencies
├── TACTcalendar4.ipynb     # Jupyter notebook for the project
├── TACTcalendar4.py        # Main Python script
└── nuctcalendar-39398a67d180.json  # Google Calendar API credentials (keep this private!)
```

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/docto-rin/tactcalendar4.git
   cd tactcalendar4
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Set up the Google Calendar API credentials (see Google Calendar API documentation for details).

4. Run the manager:
   ```
   chmod +x manager.sh
   ./manager.sh
   ```

## Running as a Service

To run TACT Calendar4 as a systemd service:

1. Modify the `tactcalendar.service` file:
- Open the file and locate the `ExecStart` line.
- Update the path to match your specific installation directory.
- For example, if your project is in `/home/yourusername/tactcalendar4/`, change the line to:
   ```
   ExecStart=/home/yourusername/tactcalendar4/manager.sh
   ```

2. Copy `tactcalendar.service` to `/etc/systemd/system/`:
   ```
   sudo cp tactcalendar.service /etc/systemd/system/
   ```

3. Reload systemd, enable and start the service:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable tactcalendar.service
   sudo systemctl start tactcalendar.service
   ```

## License

This project is released under the [MIT License](LICENSE).
