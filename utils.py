import pandas as pd
from pydantic import BaseModel, model_validator
from typing import Optional
from rapidfuzz import fuzz
import json
import os

from dotenv import load_dotenv
load_dotenv()

# load dataset once
with open("pincodes.json", 'r', encoding='utf-8') as file:
    PINCODES = json.load(file)

all_wa_grps = {
    "thiruvananthapuram": os.environ["thiruvananthapuram"],
    "kollam": os.environ["kollam"],
    "pathanamathitta": os.environ["pathanamathitta"],
    "alappuzha": os.environ["alappuzha"],
    "idukki": os.environ["idukki"],
    "ernakulam": os.environ["ernakulam"],
    "thrissur": os.environ["thrissur"],
    "palakkad": os.environ["palakkad"],
    "malappuram": os.environ["malappuram"],
    "kozhikode": os.environ["kozhikode"],
    "wayanad": os.environ["wayanad"],
    "kannur": os.environ["kannur"],
    "kasaragod": os.environ["kasaragod"],
    "kottayam": os.environ["kottayam"],
    "sathyagyanam kerala [common group)": os.environ["common"]
}

def fetch_pin(text: str):
    pin = text.strip().split(' ')[-3]
    print(f"[Extracted] pin=({pin}) from address=({text})")
    return pin

# Optimized string matching function
def is_match(a, b, threshold=85):
    """
    Return True if the fuzz ratio between a and b is above the threshold.
    """
    return fuzz.ratio(a.lower(), b.lower()) >= threshold

def fetch_grp(raw_address: str) -> str:
    """
    Fetch the correct WhatsApp group based on the district derived from the raw address.
    """
    pin = fetch_pin(raw_address)
    district = PINCODES.get(pin, "sathyagyanam kerala (common group)").lower()

    for ds in all_wa_grps:
        if is_match(ds, district):
            return all_wa_grps[ds], ds

    return all_wa_grps["sathyagyanam kerala (common group)"], "sathyagyanam kerala (common group)"

MESSAGE_TEMPLATE = """
🙏 
Join our WhatsApp group for meaningful discussions on the book GYAN GANGA. 

നമസ്തേ 🙏 
ജ്ഞാന്‍ഗംഗ പുസ്തകത്തെ കുറിച്ചുള്ള അർത്ഥപൂർണ്ണമായ ചർച്ചകൾക്കായി ഞങ്ങളുടെ WhatsApp ഗ്രൂപ്പിൽ ചേരൂക 📖✨ 

{wa_grp}
""".strip()

def build_wa_message_content(raw_address: str) -> str:
    wa_grp, district = fetch_grp(raw_address)
    return MESSAGE_TEMPLATE.format(wa_grp=wa_grp), district


class CsRecordSchema(BaseModel):
    address: str
    mobile_no: str
    status: str
    assignee: Optional[str] = None
    remarks: Optional[str] = None
    wa_message: Optional[str] = None
    wa_grp: Optional[str] = None

    @model_validator(mode='after')
    def set_wa_message(self) -> 'CsRecordSchema':
        self.wa_message, self.wa_grp = build_wa_message_content(raw_address=self.address)
        return self


def get_records(uploaded_filename):
    df = pd.read_excel(uploaded_filename)
    df = df.fillna('') # replace NaN values with empty strings
    json_data = df.to_dict(orient="records")
    return json_data

def get_interested_entries(records):
    interested_list = []
    for record in records:
        if record.get("Status").lower().strip() in [
            os.getenv("IS_1").lower().strip(),
            os.getenv("IS_2").lower().strip()
        ]:
            entry = CsRecordSchema(
                address=record.get("Address"),
                mobile_no=str(record.get("Mo. No.")),
                status=record.get("Status"),
                assignee=record.get("Assigne", ""),
                remarks=record.get("Remarks", "")
            )
            interested_list.append(entry)
    return interested_list

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xls', 'xlsx'}

