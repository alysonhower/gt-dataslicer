# Autonomous review, remediation, and verification mission: gt-dataslicer

You are the staff-level engineer responsible for independently auditing, hardening, and improving the `gt-dataslicer` repository.

Operate in agentic goal mode. Do not stop after producing a review or implementation plan. Inspect the actual repository, reproduce issues, prioritize them, implement justified fixes in coherent slices, test each slice, reassess the result, and continue until the defined completion gates are met.

Do not ask for approval between normal work phases. Present your initial plan, then proceed. Ask a question only when an external product decision is genuinely impossible to infer safely; otherwise choose the safest backward-compatible design and document the decision.

## Mission

Bring the application to a substantially higher level of:

1. Data integrity and deterministic behavior.
2. Input and output file safety.
3. Beginner-safe UI and workflow clarity.
4. Accessibility and keyboard usability.
5. Multi-input correctness.
6. Concurrency and application-lifecycle safety.
7. Maintainable architecture.
8. Test quality and release confidence.

The objective is not a visual redesign alone and not a broad rewrite. Preserve the product’s intended simplicity while fixing systemic correctness, safety, and usability problems.

## Repository rules

Before modifying code:

1. Read `AGENTS.md` completely and follow it.
2. Read:
   - `REQUIREMENTS.md`
   - `IMPLEMENTATION_PLAN.md`
   - `README.md`
   - `pyproject.toml`
3. Inspect the real source files rather than relying on a Repomix or compressed representation.
4. Map the complete execution path:
   - input resolution;
   - XLSX and ZIP staging;
   - configuration merging;
   - visual-filter conversion;
   - DSL parsing and compilation;
   - DuckDB execution;
   - derived-column projection;
   - CSV, Parquet, and XLSX export;
   - reports and rejects;
   - UI bridge;
   - background jobs;
   - Pywebview lifecycle.
5. Record the initial `git status`.
6. Run an appropriate baseline test set before editing. Run the full suite initially only when practical; otherwise run enough representative tests to distinguish pre-existing failures from regressions.

Never edit a packed repository representation. Edit only the actual repository files.

## Non-negotiable product constraints

Preserve these boundaries unless evidence proves that a controlled refactor is necessary:

- Filtering and transformations remain implemented and validated in Python/DuckDB, not duplicated in JavaScript.
- CLI, UI, and configuration files remain functionally compatible.
- Filter values remain parameterized.
- SQL identifiers and unavoidable SQL literals remain safely quoted.
- Portuguese remains the default user-facing language, with complete English parity.
- ZIP passwords remain session-only and must never be saved, logged, included in reports, or retained unnecessarily.
- Large-file processing must not regress into loading complete datasets into Python memory.
- CSV and Parquet derived values remain materialized.
- Excel formulas may be generated only when references and cached values are safe and correct; otherwise materialize the value.
- Beginner-facing copy must avoid unnecessary database, ETL, AST, and DSL terminology.
- Do not introduce a dependency injection framework, frontend framework, formatter, linter, or other tooling merely to reshape the project.
- Do not use destructive Git commands.
- Do not conceal failures through broad exception handling or by weakening tests.
- Do not claim an issue is fixed without a test, a focused reproduction, or another concrete verification method.

## Use current documentation

Use Context7 to resolve and consult current documentation for at least:

- DuckDB;
- XlsxWriter;
- Pywebview;
- OpenPyXL when available.

Use official primary documentation when Context7 does not cover the required behavior. For accessibility behavior, use authoritative WAI-ARIA and WCAG guidance.

Do not rely on memory for semantics involving:

- DuckDB CSV reject tables;
- CSV projection pushdown;
- connection and thread behavior;
- `COPY` behavior;
- `TRY_CAST`;
- exact versus approximate numeric aggregation;
- XlsxWriter constant-memory restrictions;
- worksheet naming;
- formula cached values;
- Pywebview bridge threading;
- close events;
- file-dialog behavior;
- ARIA tabs, radio groups, comboboxes, listboxes, live regions, and keyboard interactions.

Record which documented behavior supports each consequential design decision.

## Required operating loop

Maintain a working issue ledger throughout the task. It may be temporary, but it must track:

- issue ID;
- hypothesis;
- affected code paths;
- user impact;
- severity;
- reproduction or evidence;
- documentation consulted;
- proposed correction;
- regression test;
- current status;
- residual risk.

For every coherent work slice, use this loop:

### 1. Discover

- Trace the relevant call path.
- Inspect existing tests and stated product requirements.
- Form a precise hypothesis.
- Check current library documentation.
- Create the smallest reliable reproduction or failing test.
- Look for the systemic cause and adjacent manifestations, not only the first visible symptom.

### 2. Plan

- Define acceptance criteria.
- Identify compatibility and migration effects.
- Choose the smallest coherent correction.
- Decide whether the fix belongs in validation, preparation, execution, export, UI state, or reporting.
- Identify all frontends and output formats that must remain in parity.

### 3. Act

- Prefer adding or correcting a failing regression test before the implementation.
- Implement the fix at the proper shared layer.
- Avoid UI-only or CLI-only workarounds for shared behavior.
- Keep changes scoped, typed, and understandable.
- Update localized messages and documentation when user-visible behavior changes.

### 4. Check

- Run the narrowest relevant tests.
- Inspect generated CSV, XLSX, Parquet, reports, and rejects directly where applicable.
- Exercise boundary values and failure paths.
- Review the diff for accidental scope expansion.
- Confirm that the test would fail without the fix.
- Confirm that no data is silently discarded, changed, or misreported.

### 5. Reflect

Ask:

- Did the fix address the root cause or only the observed case?
- Can another input path or output format still trigger it?
- Did error handling become more actionable?
- Did performance or memory behavior regress?
- Did the change introduce a new ambiguous UI state?
- Does CLI/UI/config parity still hold?
- Is the result deterministic?
- Does the user receive a warning before any destructive or lossy behavior?

If an answer is unsatisfactory, revise the plan and repeat the loop.

Do not wait for external approval between these loops.

## Evidence standard

Treat every concern below as an investigation seed, not as an unquestionable fact.

Classify each concern after inspection as one of:

- confirmed;
- confirmed with a different root cause;
- not reproducible;
- already protected;
- intentionally accepted behavior;
- deferred with a concrete reason.

A confirmed issue must include:

- the affected path and function;
- a concise explanation of the failure;
- a reproduction or strong code-level proof;
- expected versus actual behavior;
- severity;
- a regression test;
- the implemented correction or explicit deferral.

Do not preserve a suggested remedy when a simpler or more correct design is available.

# Investigation map

## A. Data integrity and execution correctness

### A1. XLSX input formulas

Investigate XLSX staging through OpenPyXL, especially use of `data_only=True`.

Determine whether:

- formula cells without cached results become indistinguishable from blank cells;
- stale cached formula results can be exported without warning;
- converting `None` to `""` hides unevaluated formulas;
- there is any explicit formula policy.

Design an explicit, documented policy. Consider formula and cached-value views, detection of missing cached values, actionable warnings or errors, and safe defaults. Do not imply that OpenPyXL evaluates formulas.

Add tests for:

- a formula with no cached result;
- a formula with a cached result;
- a genuinely blank cell;
- a workbook containing both formulas and blanks.

### A2. CSV rejected-row accounting

Inspect DuckDB `store_rejects`, reject scan tables, reject error tables, repeated scans, and lookup registration.

Determine whether:

- the code counts error records rather than rejected physical rows;
- one malformed row can produce several counted errors;
- repeated schema inspection, counting, filtering, summaries, or reports append duplicate reject records;
- lookup CSV rejects contaminate primary-input rejects;
- reject data persists across operations on the same connection;
- rejects are exported without scoping to the authoritative source scan.

Implement scan-scoped accounting based on documented DuckDB semantics. Count distinct rejected physical rows rather than individual error records. Keep primary inputs and lookup inputs isolated.

Add tests covering:

- two rejected lines where one creates multiple error records;
- repeated reads on the same connection;
- filtered output plus summary plus report;
- lookup rejects and primary-input rejects in one run;
- multiple queue inputs.

### A3. Projection-dependent CSV validation

Verify whether DuckDB projection pushdown allows a malformed value in an unselected column to escape validation.

Establish and document the product’s intended semantics:

- validate complete physical input rows; or
- validate only columns required by the operation.

For a user-facing filtering tool, prefer consistent full-record validation unless product constraints clearly require otherwise. Ensure selecting fewer output columns does not unexpectedly change which physical rows are accepted without a visible policy.

Add a regression test with a malformed typed value in an unselected column.

### A4. Summary numeric correctness

Inspect summary aggregation and type conversion.

Determine whether:

- values are forced through `DOUBLE`;
- decimal money values lose exactness;
- integers larger than `2^53` lose precision;
- failed non-strict casts silently contribute zero;
- invalid values become indistinguishable from genuine zeros.

Preserve native exact numeric types where possible. Use a deliberate decimal policy for text columns. Do not silently coerce malformed values to zero. Provide either a validation failure or an explicit invalid-value count and warning.

Test:

- `0.1 + 0.2`;
- large integers beyond exact IEEE-754 integer range;
- configured decimal values;
- malformed numeric strings;
- nulls versus malformed values;
- grouped and ungrouped summaries.

### A5. XLSX worksheet staging collisions

Inspect filename generation for staged worksheet CSV files.

Test distinct valid sheet names that normalize to the same safe filename, including:

- `A B`;
- `A_B`;
- punctuation variants;
- accents;
- names that normalize to empty or nearly empty values.

Ensure each staged worksheet has a unique deterministic path, such as an ordinal plus sanitized name and collision-resistant suffix.

### A6. Artifact planning and source collisions

Build a complete model of all paths that may be read or written:

- primary inputs;
- ZIP archives;
- staged files;
- lookup files;
- configuration files;
- filtered outputs;
- summary outputs;
- split XLSX outputs;
- reports;
- rejects;
- temporary output files.

Investigate collisions involving:

- output equal to input;
- output equal to lookup;
- report equal to filtered output;
- report equal to rejects;
- summary equal to filtered output;
- split workbook files colliding with another artifact;
- symlink aliases;
- relative and absolute aliases;
- case-sensitive and case-insensitive filesystems.

Do not rely on unconditional lowercasing for path identity.

Create a complete artifact plan before execution. Normalize paths with platform-aware behavior. Where appropriate, use `resolve(strict=False)`, `normcase`, and `samefile`.

Prevent accidental input destruction. Write final artifacts through temporary sibling files and commit them atomically where feasible. Define consistent cleanup behavior for multi-artifact failures.

Add collision and atomicity tests.

### A7. Spreadsheet formula injection in CSV

Assess values beginning with characters commonly interpreted by spreadsheet applications as formulas, including:

- `=`;
- `+`;
- `-`;
- `@`;
- tab;
- carriage return.

Do not silently mutate machine-readable output. Define an explicit policy, likely distinguishing:

- raw CSV;
- spreadsheet-safe CSV.

Make the beginner-facing choice understandable. Preserve exact data when raw output is selected.

Test both modes and document the transformation.

### A8. Empty and null membership lists

Inspect grammar, parser, visual-filter conversion, and compiler handling for:

- `IN ()`;
- `NOT IN ()`;
- an empty visual membership value;
- lists containing `NULL`;
- `NOT IN (..., NULL)`.

Reject empty lists before SQL execution with an actionable message. Explicitly define or reject null membership semantics rather than exposing surprising SQL three-valued logic.

### A9. Deterministic deduplication

Inspect key-based deduplication using window functions.

Determine what happens when no deterministic ordering is supplied. Do not present an arbitrary surviving row as predictable behavior.

Choose and document one of:

- require sort keys for key-based deduplication;
- provide an explicit stable tie-breaker;
- clearly label the survivor as arbitrary.

Test repeated executions and ties.

### A10. Datetime timezone handling

Inspect explicit datetime parsing, especially values ending in `Z`.

Do not silently remove a UTC marker and produce a naive datetime. Preserve timezone information end to end or reject unsupported timezone-aware values with an actionable error.

Add date and datetime boundary tests.

### A11. Repeated source scans

Trace how many times one physical source may be read for:

- schema inspection;
- validation;
- filtered export;
- summary export;
- input row counts;
- rejects;
- preview.

Assess duplicated work, inconsistent snapshots when the file changes during execution, and repeated reject records.

When one run needs multiple artifacts or metrics, consider preparing or materializing one authoritative relation that DuckDB may spill to disk. Avoid loading it into Python memory.

### A12. XLSX resource-exhaustion hardening

XLSX files are ZIP containers. Inspect handling of untrusted workbooks for:

- excessive member count;
- excessive total uncompressed size;
- extreme compression ratios;
- huge worksheet counts;
- declared dimensions far larger than actual content;
- sparse worksheets causing excessive iteration.

Add reasonable, documented limits without breaking ordinary large workbooks. Produce clear errors.

### A13. Excel export boundaries

Verify current XlsxWriter behavior and test:

- worksheet names beginning or ending with apostrophes;
- invalid characters;
- duplicate names;
- name truncation collisions;
- row and column limits;
- zero or invalid `max_rows_per_sheet`;
- invalid `sheets_per_file`;
- invalid batch size;
- constant-memory row-order requirements;
- workbook close errors.

Ensure generated derived formulas still reference the correct exported source column after selection, rename, insertion, and reorder. Materialize transformations when a safe formula reference cannot be guaranteed.

### A14. Configuration typing

Inspect configuration merging for truthiness conversions such as `bool("false")`.

Validate booleans, integers, lists, paths, enum values, and unknown keys using explicit rules. Do not accept visibly false string values as true.

Preserve compatibility for valid existing configurations and produce precise messages for invalid values.

### A15. Resource lifecycle

Verify explicit closure or context-managed lifecycle for:

- DuckDB connections;
- OpenPyXL workbooks;
- XlsxWriter workbooks;
- temporary input sessions;
- extracted files;
- partially written outputs.

Do not rely on garbage collection for important file handles or Windows file locks.

## B. UI workflow and user safety

### B1. Incomplete visual rules

Inspect the visual-filter builder and Python conversion path.

Incomplete rules must never be silently omitted when the user validates or runs. Examples include:

- column selected, value missing;
- incomplete `between`;
- empty membership input;
- partially configured derived transformation;
- missing rename target;
- incomplete sort or deduplication configuration.

Show an inline error, retain the invalid rule visibly, block execution, and focus the first invalid field. An unused rule must be explicitly removed.

Replace tests that expect silent omission with tests for visible validation failure.

### B2. Actual wizard state

The current four-stage layout may only be navigational anchors.

Implement or validate an explicit workflow state model such as:

- not started;
- incomplete;
- valid;
- warning;
- running;
- completed.

Each step should expose its current status and summarize completed choices. The user must be able to identify why execution is blocked and return directly to the relevant field.

Avoid creating an unnecessarily rigid wizard; users may revisit prior steps, but the state must be explicit.

### B3. Inline error placement and focus

Do not display all actionable errors only in the final run section.

For validation failures:

- mark the responsible control with `aria-invalid`;
- associate an inline message with the control;
- expand the relevant section;
- move focus or scroll to the first blocking error;
- keep technical details separately available for support.

Implement an accessible error summary for multiple failures.

### B4. Multi-input inspection and validation

Inspect all behavior that uses only `session.inputs[0]`.

The UI must not imply that the first input’s schema, size, or validity describes the complete queue.

Provide:

- aggregate queue information;
- per-input inspection status;
- schema compatibility status;
- missing-column details per input;
- validation across every queue item;
- grouped validation where identical schema fingerprints permit reuse.

Test a queue in which only a later file is incompatible.

### B5. Destructive actions and overwrite protection

Review:

- “delete ZIP after extraction”;
- existing output overwrite;
- output/source collisions;
- closing the application during a run;
- cancellation during export.

Destructive actions must be deliberate and specific. Do not bury source deletion among ordinary reading settings.

Prefer a separate confirmation naming the exact ZIP path. Where supported, prefer recycle-bin behavior over irreversible deletion.

Confirm overwrite before starting, not after partial work. Protect application close while committing artifacts.

### B6. Contextual input settings

Do not show every low-level input option for every file type.

Provide contextual controls:

- CSV: delimiter, encoding, header, null handling;
- XLSX: worksheet selection;
- ZIP: member and password handling;
- Parquet: minimal options.

Prefer automatic detection first. Expose manual settings as recovery controls when inspection fails or when the user opens advanced options.

Do not expose implementation optimizations such as schema reuse as ordinary beginner decisions unless there is a clear user-facing consequence.

### B7. ZIP password workflow

Replace or justify the persistent multiline password field.

Prefer a per-archive prompt after encryption is detected, with an optional “use for remaining ZIP files in this run” action. State that passwords are session-only. Clear password values after completion or reset.

### B8. Type-aware visual filtering

Use inspected column types to limit operators and choose value editors.

Examples:

- text: equals, contains, starts with, ends with, empty;
- numeric: equals, comparisons, between;
- date: on, before, after, between;
- boolean: yes, no, empty.

Keep regex and subtle null/empty/blank distinctions in advanced controls unless the user explicitly needs them.

Use operator-specific editors:

- two labeled values for `between`;
- chips or tokenized values for membership;
- date-aware inputs for dates;
- numeric input modes for numbers;
- no value control for null-style predicates.

Never rely solely on hidden browser-side type inference for correctness.

### B9. Visual and advanced filter modes

Define what happens when switching modes.

Either:

- convert visual rules to an advanced expression with clearly documented one-way editing; or
- keep the modes independent and explicitly state that they are separate filters.

Warn before deactivating or discarding edited content. Do not allow stale advanced text to override visible rules.

### B10. Data preview

Add or evaluate a lightweight preview flow:

- sample input rows and detected types after inspection;
- sample matching rows after filter validation;
- matching-row count when practical.

Clearly label samples. Use `LIMIT` and safe query preparation. Do not load complete datasets into the browser or Python memory.

Preview should help users detect delimiter, encoding, type, leading-zero, worksheet, and filter mistakes.

### B11. Output format explanation

Output format controls must explain consequences in plain language.

At minimum:

- CSV: common, easy to share, optionally spreadsheet-safe;
- Excel: intended for direct Excel use, with row/sheet splitting behavior;
- Parquet: intended for large datasets and analytics tools.

The selection control must expose a correct radio-selection model and update the destination extension safely.

### B12. Destination selection

Choose the native dialog based on expected artifacts:

- one known artifact: save-file dialog;
- multiple artifacts: folder dialog;
- potentially split XLSX output: folder-oriented flow or an explicit warning.

Before execution, show the expected output directory and estimated number or pattern of generated files.

### B13. Advanced option organization

Do not place unrelated features in one undifferentiated advanced grid.

Group by user task:

- summary;
- output columns and renames;
- organization, sorting, and deduplication;
- diagnostic files;
- expert input behavior.

Replace ambiguous independent summary checkboxes with one explicit choice:

- filtered data;
- filtered data plus summary;
- summary only.

### B14. Derived-column usability

Review the current prefix/suffix naming workflow and transformation selector.

Provide a simple primary field for the resulting column name. Keep prefix, suffix, separator, and positioning as optional advanced controls.

Group transformations by user intent, for example:

- clean text;
- change text;
- extract text;
- format identifiers.

Use transformation-specific parameter labels rather than generic “Value” and “New value” placeholders.

Show a before-and-after sample when possible.

Allow transformation reorder through explicit keyboard-operable buttons. Dragging may be supplementary but not required.

### B15. Accessibility

Audit the rendered UI, not only source strings.

Correctly implement or simplify:

- tabs;
- radio groups;
- editable comboboxes;
- listboxes;
- active options;
- drop zones;
- icon buttons;
- live regions;
- alert and status behavior;
- focus order;
- focus visibility;
- target sizes;
- keyboard navigation;
- translated accessible names.

Specific checks:

- A `tablist` must contain actual tabs with `aria-selected`, `aria-controls`, and appropriate keyboard behavior; otherwise remove the tab semantics.
- A `radiogroup` must contain actual radio controls or valid custom radios; do not combine `radiogroup` with unrelated `aria-pressed` toggle semantics.
- Searchable column inputs need a complete combobox/listbox relationship, unique option IDs, active-descendant behavior, and keyboard support.
- A focusable drop zone must be keyboard-operable or cease being a separate focus target.
- “x” and “...” controls need meaningful accessible names and adequate target sizes.
- Status changes need appropriate `role="status"` or alert behavior without excessive duplicate announcements.
- The language switch must update visible text, placeholders, titles, accessible names, dynamic messages, and `document.documentElement.lang`.
- Test 960×640, 200% zoom, 400% zoom where practical, long paths, long column names, and both languages.
- Verify Windows high-contrast behavior and reduced-motion preference where applicable.

### B16. Cancellation and run lifecycle

Provide a coherent running state:

- disable conflicting edits;
- show current phase and queue position;
- expose Cancel;
- prevent a second simultaneous run;
- define cleanup for partial artifacts;
- protect window closure while a commit is in progress;
- preserve completed results until the user explicitly begins a new run.

### B17. Configuration and lookup workflows

The bridge exposes configuration and lookup file operations. Verify whether the visible UI completes those workflows.

If users can save configuration, provide a clear way to load and apply it, or deliberately remove/mark incomplete UI surface.

Expose lookup-file configuration only through a beginner-safe visual workflow. Do not leave callable bridge methods as undocumented dead-end features.

## C. Concurrency and lifecycle safety

Use current Pywebview documentation to verify how bridge calls are threaded.

Inspect `DataSlicerApi`, `JobManager`, the DuckDB engine, and window lifecycle for:

- shared dictionary races;
- unsynchronized active-job state;
- mutable `JobStatus` objects escaping as live references;
- progress updates racing with serialization;
- completed jobs accumulating forever;
- language state changing while a job is running;
- file dialogs or window methods called from unsupported threads;
- multiple threads sharing one DuckDB connection;
- daemon worker termination during output writing.

Use explicit locking or immutable snapshots where required. Give each job an appropriate engine/connection lifecycle. Implement graceful close and cancellation behavior.

Add deterministic concurrency tests using events and barriers rather than timing sleeps where possible.

## D. Architecture and code quality

### D1. Preparation boundary

Assess whether execution currently interleaves:

- option resolution;
- input validation;
- schema resolution;
- filter compilation;
- projection planning;
- deduplication;
- summary planning;
- artifact planning;
- writing.

Consider introducing a public preparation boundary such as:

- `prepare_run(...)`;
- `PreparedRun`;
- `ArtifactPlan`.

Do this only if it clearly removes duplicated validation and private method access. The prepared model should make CLI, UI validation, preview, dry-run, and execution use the same decisions.

### D2. Private engine methods used by frontends

Remove or reduce UI and CLI reliance on private engine methods marked with `SLF001`.

Expose a stable shared validation/preparation API rather than duplicating orchestration in each frontend.

### D3. Structured user-facing errors

Inspect localization that parses English exception strings with exact matches and regular expressions.

Prefer structured application exceptions containing:

- stable error code;
- machine-readable context;
- user-facing interpolation values;
- optional technical cause.

Render localized text at the CLI/UI boundary. Do not translate stable configuration keys, report keys, identifiers, or exception class names.

### D4. Broad exception handling

Retain broad exception conversion only at true process, job, or UI boundaries.

Inside parsing, input resolution, query preparation, and export, catch expected exceptions narrowly. Preserve tracebacks for logs and support details without exposing sensitive values.

### D5. Engine responsibility

Determine whether `DuckDBEngine.run_filter()` has excessive responsibility. Extract cohesive planning or export helpers where this reduces coupling and duplicated behavior. Avoid a cosmetic class explosion.

### D6. Report model consistency

Inspect duplication between report artifacts and output path lists.

Make one representation authoritative or derive one from the other. Ensure reports cannot claim artifacts that were not fully committed.

### D7. Dependency and release reproducibility

Assess:

- open-ended minimum dependency versions;
- absence of constraints or lock files;
- duplicated package version declarations;
- lack of CI;
- frozen-build compatibility.

Do not introduce elaborate release machinery. Add the smallest maintainable reproducibility mechanism justified by the project.

Ensure the tested dependency set is clear for releases.

## Suggested implementation order

Independently verify and adjust this order based on dependencies.

### Phase 0: Baseline and risk ledger

- Map architecture.
- Run baseline tests.
- Reproduce suspected P0 failures.
- Classify every concern.
- Present a concise ordered plan, then proceed automatically.

### Phase 1: Data-integrity and file-safety blockers

Prioritize confirmed issues involving:

- XLSX formula loss;
- reject accounting;
- projection-dependent validation;
- summary precision;
- path collisions;
- source overwrite;
- atomic output behavior;
- worksheet staging collisions;
- empty membership expressions;
- deterministic deduplication.

Keep each change independently testable.

### Phase 2: UI correctness and safety

Prioritize:

- no silent omission of incomplete rules;
- all-input validation;
- inline errors and focus;
- explicit step state;
- overwrite and close protection;
- cancellation;
- output destination behavior.

### Phase 3: UI comprehension and accessibility

Implement:

- contextual controls;
- type-aware filters;
- preview;
- format descriptions;
- derived-column simplification;
- correct ARIA patterns;
- complete localization;
- keyboard workflows;
- responsive and zoom behavior.

### Phase 4: Architecture and maintainability

Refactor only after behavior is covered by tests:

- shared preparation boundary;
- artifact plan;
- structured errors;
- resource lifecycle;
- report consistency;
- dependency reproducibility.

## Required regression matrix

At minimum, add or update tests for the following confirmed behaviors.

### Input and staging

- XLSX formula without cache.
- XLSX formula with cache.
- Distinct worksheet names that sanitize identically.
- Excessive or sparse XLSX dimensions.
- Encrypted ZIP password remains session-only.
- ZIP validation and dry-run never delete the archive.
- Queue whose second input has an incompatible schema.

### Filters

- Incomplete visual value rule blocks validation.
- Incomplete `between` rule blocks validation.
- Empty membership list is rejected.
- Membership containing null has defined behavior.
- Visual/advanced mode switch does not silently change the active filter.
- Type-inappropriate operators are prevented or rejected.
- UTC datetime handling is explicit.

### Execution and reporting

- One physical rejected line producing multiple DuckDB error rows.
- Repeated source scans do not duplicate reject counts.
- Lookup rejects do not contaminate input rejects.
- Malformed unselected column follows the documented validation policy.
- Exact decimal and large-integer summary behavior.
- Invalid summary values do not silently become zero.
- Deduplication ties are deterministic or explicitly rejected.
- Reports list only successfully committed artifacts.

### Outputs

- Output cannot overwrite an input or lookup inadvertently.
- Report, rejects, summary, filtered output, and split files cannot collide.
- Symlink and case-sensitive path behavior.
- Partial export failure does not publish a corrupt final artifact.
- CSV raw and spreadsheet-safe modes.
- Worksheet names with apostrophes and truncation collisions.
- Excel formulas reference the correct column after selection and reordering.
- Constant-memory export writes rows in the required order.
- Workbook-close errors are surfaced.

### UI and jobs

- Complete keyboard operation for filter mode, output format, column search, and transformation reorder.
- Correct inline error association and focus.
- All static and dynamic strings translate in both languages.
- `document.documentElement.lang` changes with the UI language.
- A second job cannot start while one is active.
- Cancellation reaches a safe terminal state.
- Closing during a run is guarded.
- Job status snapshots are race-safe.
- Completed-job storage has a bounded lifecycle.
- Existing results persist until a deliberate reset.

## Testing approach

During implementation:

- Run focused unit and integration tests after each slice.
- Do not repeatedly run the entire test suite after every small edit.
- Inspect generated files directly for data-integrity changes.
- Use temporary real CSV, Parquet, XLSX, and ZIP fixtures.
- Prefer deterministic tests over sleep-based tests.
- For DSL changes, update parser and compiler coverage together.
- For config, i18n, and CLI behavior, update integration tests.
- For UI bridge behavior, test Python API payloads and errors.
- Do not rely only on tests that search HTML or JavaScript source strings when runtime behavior matters.

After UI changes:

1. Stop stale app or static-server processes.
2. Launch a fresh application or supported local UI instance.
3. Use the available in-app browser control to test the rendered workflow.
4. Verify:
   - scrolling;
   - step navigation;
   - filter modes;
   - keyboard column search;
   - inline validation;
   - output-format selection;
   - derived columns;
   - running and completed states;
   - Portuguese and English;
   - 960×640 layout;
   - zoomed layout.

Do not require a PyInstaller rebuild during every UI iteration. Rebuild only at the final relevant verification stage when packaging changed or release packaging must be validated.

At the end:

- run the full `pytest` suite once;
- run relevant packaging/static asset tests;
- perform the rendered browser verification;
- build the executable only when required by the changed scope;
- inspect `git diff --check`;
- inspect final `git status`.

## Definition of done

The task is complete only when:

1. Every investigation seed has been classified.
2. Every confirmed P0 issue has been fixed or explicitly deferred with a strong reason and containment.
3. Confirmed P1 issues in the edited subsystems have regression coverage.
4. Incomplete UI configuration can no longer be silently ignored.
5. Multi-input validation reflects the complete queue.
6. Output planning prevents accidental source or artifact collisions.
7. Reports and reject counts describe actual physical outcomes.
8. Summary arithmetic has an explicit precision and invalid-value policy.
9. Background jobs have a safe lifecycle.
10. Keyboard and accessible-name behavior is correct for changed UI controls.
11. Portuguese and English remain in parity.
12. Targeted tests and the final full suite pass.
13. Rendered UI checks pass.
14. Documentation reflects user-visible behavioral changes.
15. No generated test artifacts, passwords, temporary data, or unrelated edits remain in the working tree.

## Final response format

Provide a concise but evidence-based final report containing:

### Outcome

State whether the hardening mission is complete, partially complete, or blocked.

### Confirmed findings

For each confirmed issue, include:

- severity;
- root cause;
- affected files;
- user impact;
- correction;
- regression test.

Also identify investigation seeds that were not reproducible or were already protected.

### Architectural changes

Explain any new preparation, artifact-planning, error, or lifecycle boundaries and why they were necessary.

### UI/UX changes

Describe the resulting workflow from input selection through completion, including validation, accessibility, multi-input behavior, output selection, cancellation, and error recovery.

### Verification

List exact commands and checks performed, including:

- targeted tests;
- full test suite;
- browser scenarios;
- generated-file inspection;
- packaging verification, when applicable.

Do not state only “tests pass”; include counts or concrete command outcomes.

### Residual risks and deferred work

List remaining risks, why they were deferred, and the smallest next action for each.

Do not conceal uncertainty, weaken assertions, or describe an issue as fixed merely because the code appears plausible.
