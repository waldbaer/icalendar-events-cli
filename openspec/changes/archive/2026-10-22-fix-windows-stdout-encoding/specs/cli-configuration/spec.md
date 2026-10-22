# Spec Delta

## ADDED Requirements

### Requirement: Message encoding

The tool SHALL write help, version and error messages in UTF-8, on stdout and on stderr, independent of the system
locale and console code page.

#### Scenario: Error message with a character outside the code page

- **WHEN** stderr uses the cp1252 code page and the tool is run with `--filter.summary "[🎉"`
- **THEN** stderr receives the error message naming `invalid RegEx value '[🎉'` in UTF-8, with the character
  unescaped
- **AND** the tool exits with code 2
