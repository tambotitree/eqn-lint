# TODO — eqnlint Audit Suite

## v0.3.0 Release
- [ ] Add `--list` option to show available audits
- [ ] Freeze JSON schema for outputs
- [ ] Add `--quiet` and `--summary` output modes
- [ ] Implement retry/backoff for AI API calls
- [ ] Improve equation extraction to handle multi-line `align`/`gather` environments

## Backlog
- [ ] DOI/arXiv citation checker audit
- [ ] Symbol table sharing between audits
- [ ] Support for LaTeX macros in symbol extraction
- [ ] Context window optimization for large documents
- [ ] Improve error handling when AI returns invalid JSON
- [ ] Parallelize audits for large equation sets
- [ ] Option to skip equations with only numeric values
- [ ] Detect and warn about redundant or duplicate equations
- [ ] Add configuration file support for default args
- [ ] Improve verbose logging format with timestamps
- [ ] Integrate `TODO.md` scanning into CI workflow

## Notes
This file is a living checklist. Update it as features are added or ideas come up.
