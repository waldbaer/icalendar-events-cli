# Spec Delta

## MODIFIED Requirements

### Requirement: Human-readable event lines

Each human-readable event line SHALL start with `<start> -> <end> [<duration> sec]`, left-aligned and padded to 70
characters, where the duration is the number of whole seconds between start and end. It SHALL continue with
` | <summary>`, then ` | Description: <description>` when the event has a description, then
` | Location: <location>` when the event has a location.

#### Scenario: Event with a location

- **WHEN** a selected event has the location `BW` and no description
- **THEN** its line ends with ` | <summary> | Location: BW`

#### Scenario: Event without description or location

- **WHEN** a selected event has neither a description nor a location
- **THEN** its line ends with ` | <summary>`

#### Scenario: Event with description and location

- **WHEN** a selected event has the description `Schulferien 2025` and the location `BW`
- **THEN** its line ends with ` | <summary> | Description: Schulferien 2025 | Location: BW`
