# Document Automation Agent

## Purpose

Convert work-hour records created through Vela's existing Apple Shortcut and Apple Notes workflow into Excel records for accounting and invoicing.

The agent reduces the manual work of transferring hours recorded during or after work into the accounting spreadsheet.

## Workflow

1. A Vela partner records work hours using the existing Apple Shortcut.
2. The Shortcut saves the information to an Apple Notes note named **"Billable Hours."**
3. The Python program reads the contents of that note using AppleScript.
4. The program parses the structured work-hour records.
5. The program validates the records.
6. The program checks whether records have already been added to the Excel workbook.
7. New valid records are added to the Excel workbook.
8. The resulting workbook is available for the normal accounting and invoicing process.

## Required Data

Each billable record contains:

* Date
* Project
* Hours
* Description

The expected note format is:

```text
Date: Sep 16, 2026 at 19:56
Project: Automation Agent
Hours: 2
Description: Created spec .md
```

Multiple records are stored in the same Apple Notes note.

## Scope

The agent is specifically designed for Vela's billable-hours workflow.

The current implementation handles:

* Reading the **"Billable Hours"** Apple Notes note
* Parsing structured work-hour entries
* Extracting date, project, hours, and description
* Converting the hours value into a numeric value
* Validating the required record information
* Checking for duplicate records
* Adding new records to an existing Excel workbook
* Saving the updated workbook

## Out of Scope

The agent does not:

* Generate invoices
* Send invoices
* Determine billing rates
* Contact clients
* Connect directly to accounting software
* Process arbitrary document formats
* Process PDFs, images, or scanned documents
* Use OCR
* Provide a general-purpose document management system
* Use an external AI service or LLM for processing

## Validation

The program validates billable records before adding them to the workbook.

Validation includes checking for:

* Missing required fields
* Invalid dates
* Invalid hours values
* Malformed records
* Duplicate records

Records that do not meet the expected format should not be silently added to the accounting workbook.

## Duplicate Handling

The program checks existing workbook records before adding new entries.

A billable record that has already been processed should not be added to the workbook again.

Duplicate detection is part of the current workflow and should be tested whenever changes are made to the parsing or Excel-writing logic.

## Privacy and Security

The workflow is designed to process billable-hour information locally.

Current principles include:

* Process information locally rather than sending it to external services.
* Do not place sensitive project or client information into unnecessary debug output.
* Do not store information that is unnecessary for the billing workflow.
* Keep credentials and API keys out of source code.
* Protect the resulting Excel workbook from unnecessary access.

## Human Review

The agent supports the accounting workflow but does not replace human verification.

The resulting Excel records should be reviewed as part of Vela's normal accounting and invoicing process.

## Current Implementation

The current implementation uses:

* Python
* AppleScript
* Apple Notes
* `openpyxl`
* Excel

The program runs locally on the Mac.

The current workflow does **not** use an LLM, AI model, OCR, external API, or cloud processing service.

## Current Status

The core workflow is functional:

**Apple Shortcut → Apple Notes → AppleScript → Python → validation → duplicate check → Excel**

The agent has been tested with multiple billable-hour records and successfully adds new records to the Excel workbook while preserving the existing workbook data.

The implementation should remain focused on this workflow unless the project requirements change.
