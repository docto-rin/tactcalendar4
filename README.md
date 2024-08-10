# TACT Calendar4

TACT Calendar4 is a project for automatically retrieving weekly class schedules from TACT's publicly available timetables at regular intervals and updating a Google Sheets document.

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
└── TACTcalendar4.py        # Main Python script
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

3. Set up the Google Sheets API credentials and configure the .env file:
   - Go to the Google Cloud Console and create a new project.
   - Enable the Google Sheets API for your project.
   - Create credentials (Service Account Key) for the Sheets API.
   - Download the JSON key file and place it in a secure location within your project directory.
   - Create a `.env` file in the project root directory if it doesn't exist.
   - Add the following lines to the `.env` file:
     ```
     # Google Sheets API認証情報
     GOOGLE_APPLICATION_CREDENTIALS="/path/to/tactcalendar4/tact-calendar-credentials.json"

     # TACT上に公開されている時間割のスプレッドシートID
     SPREADSHEET_KEY="spreadsheet_id_here"

     # TACT上に公開されている時間割のワークシート名
     WORKSHEET_NAME="医学科4年生"
     ```
   - Replace `/path/to/tactcalendar4/tact-calendar-credentials.json` with the actual path to your downloaded JSON key file.
   - Replace `spreadsheet_id_here` with the ID of the Google Sheets spreadsheet containing the TACT timetables.
   - If necessary, modify the `WORKSHEET_NAME` to match the specific worksheet you're working with.

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