---
name: quashing-application
description: Draft a court-ready Word (.docx) Criminal Application (APL) under Section 528 BNSS before the Bombay High Court (Nagpur Bench by default) to quash an FIR, charge-sheet or RCC, in the house format and drafting style of a practising Nagpur advocate — boxed cause title, Times New Roman 14 pt, double spacing, lettered grounds and prayers, solemn affirmation. Use whenever asked to prepare, redraft or check an APL / quashing petition / s.528 (old s.482) application, including matrimonial cruelty (BNS 85 / IPC 498A) matters.
---

# Quashing application (APL, s.528 BNSS) — Bombay High Court

Produce a lawyer-review draft that reads like the advocate's own filing, built on the record and on verified law. Use the `indian-law` skill's evidence rules and tools throughout: [source and evidence rules](../indian-law/SKILL.md), [research method](../indian-law/references/research.md), [retrieval tools](../indian-law/references/retrieval.md).

## Inputs and confidentiality

- Needed: FIR (and charge-sheet/RCC papers if filed), any earlier complaints, roznama/order sheet, matrimonial or other pending proceedings, the advocate's instructions and, if supplied, the advocate's own sample APL.
- Matter papers, extracted text and the output stay in the authorised matter workspace. Never write client documents, names or extracts into this plugin, global memory or unrelated services.
- If the instruction text and the uploaded record disagree (FIR number, police station, parties, sections, stage), the record controls: draft on the record and report the conflict prominently. Do not merge two matters.
- Scanned PDFs: render pages to images (e.g. PyMuPDF), raise contrast, crop dense passages at higher DPI, and read every relevant page — FIR narrative, charge-sheet summary, accused particulars, witness statements, earlier complaints, counselling-cell record, order sheet. Note blank/illegible pages.

## Workflow

1. **Fix the matter identity and stage** from the record: court/bench, FIR no./date/police station/district, sections, place and period of occurrence, charge-sheet no./date, RCC no./court, current orders (summons, warrants), parties with ages/occupations/addresses and relationships. Record discrepancies between documents (ages, addresses, dates) instead of silently choosing one.
2. **Analyse** using [quashing-checklist.md](references/quashing-checklist.md): individual role of each accused, ingredients of every invoked offence against official text, temporal applicability (IPC vs BNS for acts before 01/07/2024), contradictions with earlier complaints, nature of witnesses, delay and sequence, interim relief appropriate to the stage, and honest prospects per applicant.
3. **Verify law** with the evidence tools: fetch the official statute PDF (India Code) and judgments (api.sci.gov.in / Bombay HC), `check_quote` every quotation and record the PDF page. Cite only VERIFIED authority, or authority quoted inside a later official judgment (say "as reproduced in …"). Unverified leads go in the separate authorities note, never in the application. [authorities.md](references/authorities.md) lists authorities already checked — re-check before relying on them.
4. **Write the matter spec** (JSON) in the matter workspace following [example-apl.json](assets/example-apl.json) and the house style in [drafting-style.md](references/drafting-style.md). Use `[FACT REQUIRED: …]` / `[TO BE CONFIRMED: …]` for anything not in the record or instructions — never invent dates, ages, authorisations, previous-proceedings statements or annexure contents.
5. **Render** with the bundled template:

   ```sh
   uv run --script <skill>/scripts/build_apl.py <matter>/apl-spec.json --out <matter>/APL-draft.docx
   ```

   The script refuses to write inside the plugin and reports numbered paragraphs, grounds, prayers, annexure labels and unresolved placeholders. The template is [apl-template.docx](assets/apl-template.docx); each `[[role]]` paragraph is a formatting prototype.
6. **Quality-check** with the checklist's final section; render page 1 (e.g. macOS `qlmanage -t`) to confirm the boxed cause title.
7. **Deliver**: the .docx, a separate authorities note (citation, proposition, verification status, official URL, how used; adverse authorities included), and a short list of conflicts, placeholders and the advocate's decisions. State the honest view of prospects per applicant.

## Boundaries

A draft is not filing, verification on oath, or advice to any party. Do not assert that one applicant may swear for others without instructions. Do not describe a document as false or fabricated without a sound basis; prefer "inconsistent", "improved version", "silent about". Keep the complainant's allegations as allegations.
