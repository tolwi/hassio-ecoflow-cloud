# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

EcoFlow Cloud Integration is a Home Assistant custom component that connects to EcoFlow power stations via their cloud APIs and MQTT brokers. It supports both private API (username/password) and public API (access/secret keys) authentication methods.

## Development Setup

For setting up the development environment, refer to `docs/Contribution.md` for dev container setup with VS Code.

### Common Development Tasks

Available VS Code tasks (run via `Ctrl+Shift+P` → "Tasks: Run Task"):
- **Reset homeassistant**: Sets up fresh Home Assistant config directory with necessary folders (config, .storage, deps) and basic configuration.yaml
- **Generate Docs**: Updates device documentation by running `docs/gen.py` which generates device summaries and creates individual device markdown files
- **Run Home Assistant Core**: Starts local Home Assistant instance for testing the integration

## Testing & Quality

**Important**: There are currently no automated tests. All testing must be done manually by running Home Assistant locally and testing the integration.

After making changes:
1. Test manually with Home Assistant using the "Run Home Assistant Core" task
2. Run the "Generate Docs" task to update device documentation 
3. Replace the "Current state" section in README.md with content from generated `summary.md`

## Architecture

### API Clients
- **Private API** (`api/private_api.py`): Uses username/password authentication with `api.ecoflow.com`
- **Public API** (`api/public_api.py`): Uses access/secret key authentication with `api-e.ecoflow.com`  
- **MQTT Client** (`api/ecoflow_mqtt.py`): Handles real-time device communication via MQTT

### Device Registry
The `devices/registry.py` maintains an ordered dictionary of all supported devices with their corresponding device classes:
- **Internal devices**: Use private API and direct MQTT communication
- **Public devices**: Use public API endpoints

### Device Structure
- Each device type has both `internal/` and `public/` implementations
- Device classes inherit from `BaseDevice` and handle entity creation
- Protocol buffers are used for binary message parsing (in `devices/internal/proto/`)

### Entity Types
Supports all standard Home Assistant entity types:
- Sensors (battery levels, power measurements, temperatures)
- Switches (AC/DC outputs, features toggles)
- Numbers (charge levels, power limits)
- Selects (timeout settings, charge currents)
- Buttons (device controls)

### Configuration
- Config flow handles device discovery and authentication
- Migration logic in `__init__.py` handles config version upgrades (currently v9)
- Device options include refresh periods, power steps, and diagnostic modes

## Key Files

- `__init__.py`: Main integration setup, config migration, device initialization
- `config_flow.py`: Configuration UI flow for adding devices
- `devices/registry.py`: Central device registry mapping device types to classes
- `api/ecoflow_mqtt.py`: MQTT client for real-time device communication
- `devices/internal/proto/`: Protocol buffer definitions for binary message parsing

## Development Notes

- Device support is added by implementing both internal and public versions
- Each device defines its available sensors, switches, numbers, and selects
- Protocol buffer files are generated from `.proto` definitions
- The integration supports device hierarchies (parent/child relationships)
- Diagnostic mode provides additional debugging sensors
- Entity availability is managed through MQTT connection status

## Dependencies

Key external dependencies:
- `paho-mqtt>=2.1.0`: MQTT client communication
- `protobuf>=5.29.1`: Binary message parsing
- `jsonpath-ng>=1.7.0`: JSON data extraction
- `homeassistant>=2024.5.5`: Home Assistant core

## Scripts Directory

Contains debugging and testing utilities:
- MQTT capture tools for protocol analysis
- Delta Pro 3 specific testing utilities
- Configuration templates for MQTT debugging