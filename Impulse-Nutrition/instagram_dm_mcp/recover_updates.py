import re
import os
import sys
import gspread
from google.oauth2.service_account import Credentials

LOG_FILE = "/Users/antoinechabrat/.gemini/tmp/impulse-nutrition/tool-outputs/session-aa571efa-69dc-40b0-91a5-d472158f26aa/run_shell_command_1774816722188_0.txt"
SPREADSHEET_ID = "1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4"
SHEET_NAME = "Suivi_Amb"

def main():
    print("Parsing log file...")
    updates_by_username = {}
    
    with open(LOG_FILE, "r") as f:
        for line in f:
            # e.g., [22:38:48] [2/400] @adamsbaihii → last=influencer → high ←
            # match username and the priority at the end of the line
            match = re.search(r"\] @([^ ]+) → .*? → (high|medium|good)", line)
            if match:
                username = match.group(1).strip()
                priority = match.group(2).strip()
                updates_by_username[username.lower()] = priority
                
    print(f"Parsed {len(updates_by_username)} username updates.")

    if not updates_by_username:
        print("No updates found.")
        return

    print("Connecting to Google Sheets...")
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "/Users/antoinechabrat/.config/google-service-account.json")
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    
    print("Fetching current rows...")
    all_data = ws.get_all_values()
    
    # We will build a list of lists for Column L to update in one go
    # Column L is index 11
    col_l_updates = []
    
    for i, row in enumerate(all_data):
        if i == 0:
            # Header
            col_l_updates.append([row[11] if len(row) > 11 else "Priorité"])
            continue
            
        sheet_username = row[8].strip() if len(row) > 8 else ""
        current_prio = row[11].strip() if len(row) > 11 else ""
        
        new_prio = updates_by_username.get(sheet_username.lower())
        if new_prio:
            col_l_updates.append([new_prio])
        else:
            col_l_updates.append([current_prio])

    print("Applying single block update for Column L...")
    # Update range L1:L<size>
    end_row = len(col_l_updates)
    ws.update(f'L1:L{end_row}', col_l_updates)
    print("Done!")

if __name__ == "__main__":
    main()
