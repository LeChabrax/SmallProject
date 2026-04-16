
import os
import sys
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Add repo root for common
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

load_dotenv()

SERVICE_ACCOUNT_PATH = os.path.expanduser(os.getenv("SERVICE_ACCOUNT_PATH", "~/.config/google-service-account.json"))
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_sheet.py <query>")
        return

    query = sys.argv[1]
    
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
    gc = gspread.authorize(creds)
    
    spreadsheet_id = "138-N1nQInuH1_lH9X-fN0C0B0A0z0X0Y0Z0W0V0U0T" # Example, but wait, I should find the real ID
    # Actually infra/common/google_sheets.py has the ID.
    
    from infra.common.google_sheets import get_worksheet, SUIVI_AMB_ID
    
    print(f"Searching for '{query}' in Suivi_Amb...")
    wks = get_worksheet(SUIVI_AMB_ID, "Suivi_Amb")
    all_values = wks.get_all_values()
    
    headers = all_values[0]
    results = []
    for i, row in enumerate(all_values[1:], start=2):
        row_str = " ".join(row).lower()
        if query.lower() in row_str:
            results.append((i, row))
            
    if not results:
        print("No results found.")
    else:
        for i, row in results:
            print(f"Row {i}:")
            for h, v in zip(headers, row):
                if v:
                    print(f"  {h}: {v}")
            print("-" * 20)

if __name__ == "__main__":
    main()
