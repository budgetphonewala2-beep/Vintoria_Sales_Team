# sales-report-pdf — Rules, errors and integration


## Error Handling

### reportlab Not Installed
```
The PDF generation requires the reportlab Python library.
Install it by running: pip install reportlab

Shall I install it for you?
```

### Python Not Available
```
Python 3 is required for PDF generation but was not found.
Please install Python 3 from https://python.org and then run:
  pip install reportlab
```

### Script Not Found
```
The PDF generation script was not found at
<SCRIPTS>/generate_pdf_report.py.
Re-run the AI Sales Team installer (install.sh) to restore it.
```

### No Report Data
```
SALES-REPORT.md was not found in the current directory.
Run `sales-report` first to generate the pipeline report, then run
`sales-report-pdf` to create the PDF version.
```

### PDF Generation Failed
If the Python script exits with an error:
1. Capture the error output
2. Check for common issues:
   - Invalid JSON input (malformed data)
   - File permission errors
   - Disk space issues
   - reportlab version incompatibility
3. Report the specific error to the user with a suggested fix
4. Keep the `_pdf_input.json` file for debugging (don't delete it on failure)

---

## Output Specifications

- **File Name:** `SALES-REPORT-{YYYY-MM-DD}.pdf` (using current date)
- **Page Size:** Letter (8.5" x 11")
- **Orientation:** Portrait for most pages, landscape for wide tables if needed
- **Color Scheme:** Professional blues and grays with color-coded score indicators
- **Font:** Helvetica or similar sans-serif for readability
- **Margins:** 0.75 inch on all sides
- **Expected Length:** 4-8 pages depending on number of prospects

---

## Important Rules

1. ALWAYS check for SALES-REPORT.md before attempting PDF generation. Never generate a PDF from scratch without the markdown report.
2. ALWAYS check for reportlab before running the script. Provide clear installation instructions if missing.
3. Clean up temporary files (_pdf_input.json) on success. Keep them on failure for debugging.
4. The JSON input must be valid JSON. Validate it before passing to the script.
5. If the PDF script fails, provide the full error output to help the user debug.
6. Never modify the original SALES-REPORT.md file during PDF generation.
7. Report the final PDF file path, size, and page count to the user after successful generation.
8. If prospect data is incomplete, still generate the PDF with available data rather than failing. Mark missing data as "N/A" in the PDF.
