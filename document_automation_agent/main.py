import subprocess

result = subprocess.run(
    [
        "osascript",
        "-e",
        'tell application "Notes" to get plaintext of note "Billable Hours"'
    ],
    capture_output=True,
    text=True
)

note_text = result.stdout

lines = note_text.splitlines()

print("Number of lines:", len(lines))

entries = []
current_entry = {}

for line in lines:
    if line.startswith("Date:"):
        if current_entry:
            entries.append(current_entry)
        current_entry = {"date": line.replace("Date:", "").strip()}

    elif line.startswith("Project:"):
        current_entry["project"] = line.replace("Project:", "").strip()

    elif line.startswith("Hours:"):
        current_entry["hours"] = line.replace("Hours:", "").strip()

    elif line.startswith("Description:"):
        current_entry["description"] = line.replace("Description:", "").strip()

if current_entry:
    entries.append(current_entry)

print("Entries found:", len(entries))

for entry in entries:
    if "hours" in entry:
        entry["hours"] = float(entry["hours"])

for i, entry in enumerate(entries, start=1):
    print(f"Entry {i}: {len(entry)} fields")

from openpyxl import Workbook

workbook = Workbook()
sheet = workbook.active
sheet.title = "Billable Hours"

sheet.append(["Date", "Project", "Hours", "Description"])

for entry in entries:
    sheet.append([
        entry.get("date", ""),
        entry.get("project", ""),
        entry.get("hours", ""),
        entry.get("description", "")
    ])

workbook.save("billable_hours.xlsx")

print("Excel file updated.")
