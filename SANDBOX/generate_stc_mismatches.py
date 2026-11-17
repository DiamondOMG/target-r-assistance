import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, 'MCP_SERVER')
from dotenv import load_dotenv
load_dotenv('MCP_SERVER/.env')

from jarvis_mcp.targetr_query import TargetRQuery
from google.oauth2 import service_account
import google.auth.transport.requests
import httpx

KEY_FILE = 'target-r-assistance-5f4d3703fed8.json'
SPREADSHEET_ID = '1ou0_T2bAhyWfWyQSCel6i5EQ5ob5iB6BmKjl16z2Sls'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheet_data():
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    creds.refresh(google.auth.transport.requests.Request())
    headers = {'Authorization': f'Bearer {creds.token}'}
    resp = httpx.get(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/\'Stores (5)\'!A1:Z', headers=headers)
    rows = resp.json().get('values', [])
    header = rows[0]
    return [dict(zip(header, r)) for r in rows[1:]]

async def main():
    sheet_stores = get_sheet_data()
    
    # Store lookups
    # 1. By exact STC in sheet
    sheet_stc_map = {s.get('STC', '').strip(): s for s in sheet_stores if s.get('STC')}
    
    # 2. Big C numeric code -> store info
    bigc_by_code = {}
    tops_by_code = {}
    store_by_name_en = {}
    
    for s in sheet_stores:
        stc = s.get('STC', '').strip()
        name_en = s.get('NAME_EN', '').strip().lower()
        if name_en:
            store_by_name_en[name_en] = s
            
        if stc.isdigit():
            bigc_by_code[stc] = s
        else:
            digits = ''.join(c for c in stc if c.isdigit())
            if digits:
                tops_by_code[digits] = s

    tq = TargetRQuery.from_env()
    screens, _, _ = await tq._get_rows('screen', 'cached')

    # Bangphlee / 11106 screens analysis
    stc_11106_list = []
    all_mismatches = []
    
    for s in screens:
        screen_id = s.get('screenId')
        current_stc = (s.get('STC') or '').strip()
        store_code = (s.get('storeCode') or '').strip()
        store_loc = (s.get('storeLocation') or '').strip()
        retailer = s.get('retailer') or ''
        label = s.get('label') or ''
        
        # Check if screen relates to 11106
        is_11106_related = ('11106' in current_stc or '11106' in store_code or 'bangphlee' in store_loc.lower())
        
        # Determine expected STC according to Final Sheet
        expected_stc = None
        match_type = "matched"
        store_info = None
        
        # Find store in sheet
        if store_code and store_code in bigc_by_code:
            store_info = bigc_by_code[store_code]
            expected_stc = store_info.get('STC')
        elif store_code and store_code in tops_by_code:
            store_info = tops_by_code[store_code]
            expected_stc = store_info.get('STC')
        elif store_loc.lower() in store_by_name_en:
            store_info = store_by_name_en[store_loc.lower()]
            expected_stc = store_info.get('STC')
        elif current_stc.startswith('BC') and current_stc[2:] in bigc_by_code:
            store_info = bigc_by_code[current_stc[2:]]
            expected_stc = store_info.get('STC')
            
        # Classify mismatch
        if current_stc == expected_stc:
            match_type = "exact_match"
        elif expected_stc is not None:
            if current_stc.startswith('BC') and current_stc[2:] == expected_stc:
                match_type = "prefix_diff_bc"
            elif store_code and store_code in bigc_by_code and current_stc != expected_stc:
                match_type = "wrong_store_assignment"
            elif retailer == 'Tops' and current_stc != expected_stc:
                match_type = "tops_code_diff"
            else:
                match_type = "stc_mismatch"
        else:
            if not current_stc:
                match_type = "missing_stc"
            elif current_stc not in sheet_stc_map:
                match_type = "stc_not_in_sheet"
            else:
                match_type = "unmapped_store"

        item = {
            "screen_id": screen_id,
            "current_stc": current_stc,
            "expected_stc_final": expected_stc,
            "store_code": store_code,
            "store_location": store_loc,
            "retailer": retailer,
            "label": label,
            "issue_type": match_type,
            "is_stc_match": (current_stc == expected_stc and expected_stc is not None)
        }
        
        if is_11106_related:
            stc_11106_list.append(item)
            
        if not item["is_stc_match"] and current_stc:
            all_mismatches.append(item)

    # Sort
    stc_11106_list.sort(key=lambda x: (x["issue_type"], x["screen_id"]))
    all_mismatches.sort(key=lambda x: (x["issue_type"], x["store_location"], x["screen_id"]))

    result = {
        "generated_at": datetime.now().isoformat(),
        "final_sheet_source": {
            "title": "Stores (AMTH) 2026-11-16",
            "spreadsheet_id": SPREADSHEET_ID,
            "tab": "Stores (5)",
            "total_stores": len(sheet_stores)
        },
        "summary": {
            "total_targetr_screens": len(screens),
            "stc_11106_screens_count": len(stc_11106_list),
            "stc_11106_exact_matches": sum(1 for x in stc_11106_list if x["is_stc_match"]),
            "stc_11106_mismatches": sum(1 for x in stc_11106_list if not x["is_stc_match"]),
            "total_screens_with_mismatch": len(all_mismatches)
        },
        "stc_11106_details": stc_11106_list,
        "all_mismatches": all_mismatches
    }

    output_path = 'c:/OMG/target-r-assistance/stc_mismatched_screens.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
    print(f"Generated {output_path} successfully!")
    print(f"Total 11106 screens: {len(stc_11106_list)} (Matches: {result['summary']['stc_11106_exact_matches']}, Mismatches: {result['summary']['stc_11106_mismatches']})")
    print(f"Total screens with STC mismatch across Target-R: {len(all_mismatches)}")

asyncio.run(main())
