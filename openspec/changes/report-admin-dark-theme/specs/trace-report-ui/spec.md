## ADDED Requirements

### Requirement: Admin dark theme aligned with ai-end

The Trace HTML report pages SHALL use a dark color palette and typography consistent with the SEAI ai-end `/admin` dashboard.

#### Scenario: Dark report home

- **WHEN** a browser opens `/report`
- **THEN** the page background SHALL be a dark surface comparable to ai-end Admin (`#0f1419` family)
- **AND** primary text SHALL be light (`#e7ecf3` family) with muted secondary labels
- **AND** accent links SHALL use the Admin accent blue (`#5b9fd4` family)
- **AND** the UI font stack SHALL prefer Segoe UI / system-ui as in ai-end Admin
