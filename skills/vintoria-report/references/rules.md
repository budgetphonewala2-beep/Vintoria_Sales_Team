# vintoria-report — rules, terminal output, errors and cross-skill use

## PDF report

### Error Handling

#### reportlab Not Installed
```
The PDF generation requires the reportlab Python library.
Install it by running: pip install reportlab

Shall I install it for you?
```

#### Python Not Available
```
Python 3 is required for PDF generation but was not found.
Please install Python 3 from https://python.org and then run:
  pip install reportlab
```

#### Script Not Found
```
The PDF generation script was not found at
<SCRIPTS>/ops/generate_pdf_report.py.
Re-run the AI Sales Team installer (install.sh) to restore it.
```

#### No Report Data
```
SALES-REPORT.md was not found in the current directory.
Run `vintoria-report` first to generate the pipeline report, then run
`vintoria-report` to create the PDF version.
```

#### PDF Generation Failed
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

### Output Specifications

- **File Name:** `SALES-REPORT-{YYYY-MM-DD}.pdf` (using current date)
- **Page Size:** Letter (8.5" x 11")
- **Orientation:** Portrait for most pages, landscape for wide tables if needed
- **Color Scheme:** Professional blues and grays with color-coded score indicators
- **Font:** Helvetica or similar sans-serif for readability
- **Margins:** 0.75 inch on all sides
- **Expected Length:** 4-8 pages depending on number of prospects

---

### Important Rules

1. ALWAYS check for SALES-REPORT.md before attempting PDF generation. Never generate a PDF from scratch without the markdown report.
2. ALWAYS check for reportlab before running the script. Provide clear installation instructions if missing.
3. Clean up temporary files (_pdf_input.json) on success. Keep them on failure for debugging.
4. The JSON input must be valid JSON. Validate it before passing to the script.
5. If the PDF script fails, provide the full error output to help the user debug.
6. Never modify the original SALES-REPORT.md file during PDF generation.
7. Report the final PDF file path, size, and page count to the user after successful generation.
8. If prospect data is incomplete, still generate the PDF with available data rather than failing. Mark missing data as "N/A" in the PDF.

## Pipeline report

### Quality Standards

1. **Data Integrity:** Only include data actually found in the prospect files. Never fabricate scores, contacts, or details.
2. **Honest Assessment:** If the pipeline is weak, say so. Don't sugarcoat a pipeline full of C-grade prospects.
3. **Actionable Output:** Every section must answer "so what?" and "what do I do next?"
4. **Consistent Formatting:** All tables must be aligned and readable. All scores on the same scale.
5. **Comparative Analysis:** Help the user understand how prospects compare to each other, not just individual scores.
6. **Time-Sensitive:** Weekly focus should reflect actual urgency, not just highest scores.
7. **Complete Coverage:** Every prospect found must appear in the dashboard. No prospect should be silently excluded.

---

### Important Rules

1. Read ALL prospect files before starting the report. Do not write the report incrementally.
2. If a prospect file is malformed or missing key data, include the prospect with a note about missing data rather than excluding it.
3. Sort prospects by score in all tables (highest first).
4. Use consistent number formatting (scores as integers, percentages with one decimal).
5. The report should be 250-350 lines of substantive content.
6. Write the file to disk using the Write tool. Confirm to the user what was written.
7. After writing, give the user a brief verbal summary of the pipeline status and top recommendation.
8. If you find more than 20 prospect files, still include all of them but note that a large pipeline benefits from segmentation.
