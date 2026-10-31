
# Patient Management System (Pydantic)

A command-line patient registration tool built to practice **Pydantic v2**. It collects patient details from the user, validates every field the moment it is entered, and saves valid records to `data.json`.

## Features

- Field-by-field validation: if one input is wrong, only that field is asked again
- Validation rules are defined once, in the `Patient` model, and reused by the input loop
- Unique patient IDs, checked against `data.json` and the current session
- Pakistani contact number validation (`+92` followed by 10 digits)
- Emergency contact is mandatory for patients older than 50
- Records are saved to `data.json` immediately after validation

## Validation Rules

| Field                 | Rule                                                          |
| --------------------- | ------------------------------------------------------------- |
| `id`                | Integer greater than 0, must be unique                        |
| `name`              | 1 to 100 characters                                           |
| `age`               | Integer, greater than 0 and at most 100                       |
| `gender`            | `Male`, `Female` or `Other` (input is auto-capitalized) |
| `marital_status`    | Optional text                                                 |
| `address`           | Optional text                                                 |
| `email`             | Valid email address (`EmailStr`)                            |
| `contact_number`    | Must match `+92` + 10 digits (12 digits total)              |
| `emergency_contact` | Same format as contact number. Required if age is above 50    |

## Pydantic Features Used

- `BaseModel`
- `Annotated` with `Field` (constraints, titles, descriptions, examples)
- `Literal` for fixed choices
- `EmailStr` for email validation
- `@field_validator` for contact number checks
- `@model_validator(mode="after")` for the cross-field emergency contact rule

## Requirements

- Python 3.9 or newer
- `pydantic` v2
- `email-validator`

## Installation

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

Example `requirements.txt`:

```
pydantic[email]>=2
```

## Usage

```powershell
python main.py
```

Example session:

```
Enter patient ID: 1
Enter patient name: Muhammad Ali
Enter patient age: 60
Enter patient gender (Male/Female/Other): male
Enter marital status (optional):
Enter address (optional): 123 Main St
Enter email: ali@example.com
Enter contact number (+92XXXXXXXXXX): +923001234567
  (Patient is over 50, emergency contact is required)
Enter emergency contact (+92XXXXXXXXXX): +923011234567
  Validation passed, patient saved to data.json.

Do you want to add another patient? (yes/no): no
```

If an input is invalid, the error is shown right away and the same question is asked again:

```
Enter contact number (+92XXXXXXXXXX): 03001234567
  Invalid input: Number must start with +92 followed by exactly 10 digits (12 digits total)
Enter contact number (+92XXXXXXXXXX):
```

## Data Format

Records are stored in `data.json` as a list of objects:

```json
[
  {
    "id": 1,
    "name": "Muhammad Ali",
    "age": 60,
    "gender": "Male",
    "marital_status": null,
    "address": "123 Main St",
    "email": "ali@example.com",
    "contact_number": "+923001234567",
    "emergency_contact": "+923011234567"
  }
]
```

## Project Structure

```
Pydantic/
├── main.py            # Patient model, input loop, file handling
├── data.json          # Saved patient records (created automatically)
├── requirements.txt
├── .gitignore
└── README.md
```

## Future Improvements

- Search, update and delete patients
- Switch from JSON file to SQLite
- Expose the system as a REST API with FastAPI
- Unit tests for the validators

## License

This project is for learning purposes.
