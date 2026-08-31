# Security Policy and Safety Boundaries

## Supported Versions
Only the latest major version is actively supported with security updates.

## Reporting a Vulnerability
Please email security@example.com to report vulnerabilities.

## Safety Boundaries
### No Hardware Control
This platform is an analysis and scheduling tool and operates in a completely isolated software simulation environment. It does **not** have the capability to interface with, command, control, or manipulate physical RF hardware or radios.

### Software Simulation Only
All models and schedulers operate on simulated data and configurations. Decisions made by the platform are meant for research and simulated performance evaluations.

### Abstract Channels F1..FN
Any channels referred to by the system (e.g., F1, F2, ... FN) are abstract identifiers mapped to arbitrary configurations in memory. They do not correlate to active, physical spectrum bands unless explicitly bound in a secure, compliant testing environment.
