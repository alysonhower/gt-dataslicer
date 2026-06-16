Design a detailed implementation plan for improving DataSlicer with three related features:

1. Parquet output support.
2. A simpler, more visual Step 3: “Escolha a saída”.
3. Beginner-friendly post-filter calculated/derived columns.

The plan must keep DataSlicer simple, friendly, and approachable for non-technical users. The goal is not to create a power-user data engineering tool. The goal is to make common export and cleanup tasks easy to discover, understand, and use visually.

## Current Product Context

DataSlicer already helps users:

- choose CSV, Parquet, Excel `.xlsx`, or ZIP input files;
- queue multiple input files;
- build filters visually or through the bilingual filter DSL;
- export filtered results to CSV by default or Excel optionally;
- use a Portuguese-first UI with English support;
- work with large files through the existing DuckDB-backed pipeline.

The new plan should build on the existing architecture and avoid duplicating filtering, query assembly, export, or file-handling logic in the UI.

## Feature 1: Add Parquet Output Support

Add Parquet as a supported output format alongside the existing CSV default and optional Excel output.

Requirements:

- CSV remains the default output format.
- Excel remains available as an optional output.
- Parquet is available in both CLI and UI wherever users choose output format.
- Output format resolution should support `.parquet` suffix and explicit format selection.
- Reports should record the selected output format and generated output path.
- Existing CSV and Excel behavior must remain backward compatible.
- Parquet output should materialize final filtered data values, not formulas.
- Multi-input output naming should work consistently for CSV, Excel, and Parquet.

The plan should explain how Parquet export is implemented through DuckDB, where it fits in the existing export branch, and how errors are reported.

## Feature 2: Improve Step 3 “Escolha a saída”

Step 3 currently feels too manual because users need to type paths or values in places where they should be able to choose visually.

Redesign Step 3 to be more beginner-friendly.

Requirements:

- Users choose the output format visually: CSV, Excel, or Parquet.
- Users choose where to save using a clear button or picker, not by typing paths first.
- The output path text field can remain visible as a secondary/manual control, but it should not feel like the primary workflow.
- Advanced options stay hidden unless the user opens them.
- The UI explains choices in plain language:
  - CSV: best for most cases and easy to share.
  - Excel: useful when the user wants to open the result directly in Excel.
  - Parquet: useful for larger datasets and analytics tools.
- Avoid technical jargon unless it directly helps the user decide.
- Keep the screen clean and simple.
- Make format-specific constraints understandable, especially Excel row/sheet limits.

The plan should include the intended layout, labels, user flow, and behavior when the user switches formats after already choosing an output path.

## Feature 3: Add Post-Filter Derived Columns

Add a noob-friendly feature that lets users create new columns after filtering, based on existing filtered columns.

The user should not need to write formulas manually.

Core behavior:

- Derived columns are applied after filtering.
- Users can add one or more derived columns.
- Each derived column starts from one source column selected with fuzzy search.
- By default, new columns are appended to the right side of the exported table.
- Users can optionally choose where the new column appears:
  - append to the right;
  - insert before a selected column;
  - insert after a selected column.
- The generated column name is based on the source column name.
- Users can add a prefix, suffix, or both, with optional separator.
- Example:
  - source column: `CPF`
  - prefix `LIMPO_` creates `LIMPO_CPF`
  - suffix `_FORMATADO` creates `CPF_FORMATADO`

The plan should define the internal data model for derived columns and how it is passed from UI/API/CLI/config into the existing execution pipeline.

## Derived Column Transformations

Users choose transformations from simple visual controls.

Required transformations:

- Replace text.
- Uppercase.
- Lowercase.
- Title Case.
- Trim spaces.
- Remove extra repeated spaces.
- Add text before the value.
- Add text after the value.
- Keep only numbers.
- Keep only letters.

Brainstorm and include additional useful beginner-friendly transformations. Consider operations such as:

- remove accents;
- remove punctuation;
- remove symbols;
- remove spaces;
- normalize spaces;
- pad left;
- pad right;
- take first N characters;
- take last N characters;
- remove first N characters;
- remove last N characters;
- extract text before a separator;
- extract text after a separator;
- extract text between two separators;
- split by separator and keep part number N;
- mask part of the value, for example CPF-style privacy masking;
- format only-digits CPF;
- format only-digits CNPJ;
- format only-digits phone number;
- convert empty text to a default value;
- convert null/blank to a default value;
- map values from simple pairs, for example `S -> Sim`, `N -> Não`;
- round numbers;
- multiply numeric values by a fixed number;
- divide numeric values by a fixed number;
- add a fixed number;
- subtract a fixed number;
- format dates as `DD/MM/YYYY`;
- extract year from date;
- extract month from date;
- extract day from date.

The plan should choose a realistic v1 subset and explicitly defer advanced or risky transformations.

Transformation rules:

- Transformations should be chainable where it makes sense.
- Prevent confusing chains, such as uppercase followed by lowercase, unless there is a clear reason.
- Validate required values for each transformation.
- Show a plain-language preview before export.
- Do not expose raw formulas in the main UI.
- Keep advanced controls behind “Opções avançadas”.

## Output-Specific Behavior

Define how derived columns are written for each output format:

- CSV: transformed values are materialized directly.
- Parquet: transformed values are materialized directly.
- Excel: derived columns should use generated Excel formulas that reference the original filtered cells when practical.

Excel requirements:

- Users should not see or write formulas in the main UI.
- The app generates formulas safely.
- Formula generation must correctly reference the filtered output columns.
- If a transformation is not practical as an Excel formula, the plan should define whether it is materialized before export or disabled for Excel with a friendly message.

## UX Requirements

The UI must stay simple and guided.

Requirements:

- Use plain-language labels.
- Use buttons, dropdowns, searchable selectors, toggles, and previews.
- Avoid raw formulas in the main workflow.
- Avoid spreadsheet-editor or ETL-builder complexity.
- Show friendly, actionable validation errors.
- Use fuzzy search for source columns and positioning columns.
- Show a clear summary like:
  - “Criar coluna `LIMPO_CPF` a partir de `CPF`.”
  - “Manter só números, depois adicionar prefixo `BR_`.”
- Keep optional controls hidden under “Opções avançadas”.

## CLI/API/Config Requirements

The plan should decide whether derived columns are v1 UI-only or also exposed through CLI/config.

If exposed through CLI/config, define:

- stable option names;
- JSON/YAML/TOML representation;
- validation rules;
- backward compatibility behavior.

If not exposed through CLI/config in v1, explain what internal API model is still needed so the UI can pass derived column definitions safely to Python.

## Implementation Plan Must Cover

Include:

- UI changes.
- CLI/API/config changes, if needed.
- Data model for derived columns.
- Internal transformation representation.
- How transformations compile to DuckDB SQL.
- How Excel formulas are generated.
- How CSV and Parquet derived values are exported.
- How column positioning works.
- Validation rules and friendly error messages.
- Testing strategy.
- Backward compatibility assumptions.
- Performance considerations for large files.
- A phased roadmap for implementation.
