# Pydantic for patient management system
import re
import json
from pathlib import Path
from typing import List, Optional, Annotated, Literal
from pydantic import BaseModel, Field, EmailStr, model_validator, field_validator, ValidationError

DATA_FILE = Path("data.json")


class Patient(BaseModel):
    id: Annotated[int, Field(gt=0, title="Patient ID", description="The unique identifier for the patient", examples=[1])]
    name: Annotated[str, Field(title="Patient Name", min_length=1, max_length=100, description="The full name of the patient", examples=["Muhammad Ali"])]
    age: Annotated[int, Field(gt=0, le=100, title="Patient Age", description="The age of the patient in years", examples=[10])]
    gender: Annotated[Literal["Male", "Female", "Other"], Field(title="Patient Gender", examples=["Male"])]
    marital_status: Annotated[Optional[str], Field(title="Marital Status", description="The marital status of the patient", examples=["Single"])] = None
    address: Annotated[Optional[str], Field(title="Address", description="The address of the patient", examples=["123 Main St"])] = None
    email: Annotated[EmailStr, Field(title="Email", examples=["muhammad.ali@example.com"])]
    contact_number: Annotated[str, Field(title="Contact Number", description="The contact number of the patient", examples=["+921234567890"])]
    emergency_contact: Annotated[Optional[str], Field(title="Emergency Contact", description="The emergency contact number of the patient", examples=["+921234567891"])] = None

    # Contact numbers must be +92 followed by exactly 10 digits (12 digits total)
    @field_validator("contact_number", "emergency_contact")
    @classmethod
    def check_contact(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"\+92\d{10}", v):
            raise ValueError("Number must start with +92 followed by exactly 10 digits (12 digits total)")
        return v

    # Emergency contact is required if the patient is older than 50
    @model_validator(mode="after")
    def validate_emergency_contact(self):
        if self.age > 50 and not self.emergency_contact:
            raise ValueError("Emergency contact is required for patients above 50 years of age.")
        return self


# ---------- File handling ----------

def load_data() -> list:
    """Read all saved patients from data.json. Returns an empty list if the file is missing or empty."""
    if not DATA_FILE.exists():
        return []
    text = DATA_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"Warning: {DATA_FILE} is not valid JSON. Fix or delete it, then run again.")
        raise SystemExit(1)


def save_patient(patient: Patient) -> None:
    """Append one patient to data.json without losing the existing records."""
    records = load_data()
    records.append(patient.model_dump(mode="json"))
    DATA_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------- Input handling ----------

def ask(field: str, prompt: str, data: dict, optional: bool = False, transform=None):
    """Ask for a single field. On invalid input, show the error and ask again immediately."""
    while True:
        raw = input(prompt).strip()

        if optional and raw == "":
            return None
        if transform:
            raw = transform(raw)

        try:
            # Validate using the Patient model itself, so rules are defined only once
            Patient(**{**data, field: raw})
        except ValidationError as e:
            # Only look at errors for this field; other fields are not filled in yet
            errors = [err for err in e.errors() if err["loc"] == (field,)]
            if errors:
                for err in errors:
                    print("  Invalid input:", err["msg"].removeprefix("Value error, "))
                continue
        return raw


def input_patients() -> List[Patient]:
    patients = []
    # IDs already saved in data.json
    existing_ids = {record["id"] for record in load_data()}

    while True:
        data = {}

        # Patient ID (duplicate check against the file and this session)
        while True:
            data["id"] = ask("id", "Enter patient ID: ", data)
            pid = int(data["id"])
            if pid in existing_ids:
                print("  This ID already exists, please enter a different one.")
            else:
                break

        data["name"] = ask("name", "Enter patient name: ", data)
        data["age"] = ask("age", "Enter patient age: ", data)
        data["gender"] = ask("gender", "Enter patient gender (Male/Female/Other): ", data, transform=str.title)
        data["marital_status"] = ask("marital_status", "Enter marital status (optional): ", data, optional=True)
        data["address"] = ask("address", "Enter address (optional): ", data, optional=True)
        data["email"] = ask("email", "Enter email: ", data)
        data["contact_number"] = ask("contact_number", "Enter contact number (+92XXXXXXXXXX): ", data)

        # Emergency contact is mandatory for patients older than 50
        needs_emergency = int(data["age"]) > 50
        if needs_emergency:
            print("  (Patient is over 50, emergency contact is required)")
        data["emergency_contact"] = ask(
            "emergency_contact",
            "Enter emergency contact (+92XXXXXXXXXX): " if needs_emergency
            else "Enter emergency contact (optional): ",
            data,
            optional=not needs_emergency,
        )

        # Final validation (model_validator runs here), then save immediately
        patient = Patient(**data)
        save_patient(patient)
        patients.append(patient)
        existing_ids.add(patient.id)
        print(f"  Validation passed, patient saved to {DATA_FILE}.\n")

        cont = input("Do you want to add another patient? (yes/no): ").strip().lower()
        if cont != "yes":
            break

    return patients


if __name__ == "__main__":
    patients = input_patients()
    print(f"\n{len(patients)} patient(s) added:")
    for p in patients:
        print(p)