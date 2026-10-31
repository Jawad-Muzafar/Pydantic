# Problems without pydantic
# There is not method to validate the data, so if the data is not in the correct format, it will raise an error.
# Demo code to show the problems without pydantic
def validate_data(data):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    if "name" not in data or not isinstance(data["name"], str):
        raise ValueError("Name must be a string")
    if "age" not in data or not isinstance(data["age"], int):
        raise ValueError("Age must be an integer")
    if "email" not in data or not isinstance(data["email"], str):
        raise ValueError("Email must be a string")
    return True
# We have to write a lot of code to validate the data, and it is not reusable. If we want to validate another data structure, we have to write the validation code again.