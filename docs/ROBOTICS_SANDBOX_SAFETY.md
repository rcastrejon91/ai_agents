# Robotics Sandbox Safety Configuration

This document describes the safety measures and configuration implemented for the Lyra bot's robotics sandbox functionality.

## Overview

The robotics sandbox has been enabled in the Lyra bot system while maintaining strict safety controls and implementing additional sandbox-specific boundaries to ensure safe operation.

## Configuration Changes

### Primary Configuration (topics.yml)

The robotics sandbox is configured in the `topics.yml` file under the `robotics` section:

```yaml
robotics:
  enabled: true                    # Sandbox is now enabled
  self_repair_enabled: false       # Self-repair remains disabled for safety
  approve_required: true           # Human approval required for all operations
```

## Safety Measures

### 1. Core Safety Constraints (Maintained)

All existing safety measures remain in place:

- **Human Approval Required**: All robotics operations require human approval before execution
- **Self-Repair Disabled**: The robot cannot modify its own hardware or software
- **Actuator Limits**: 
  - Maximum torque: 2.0 Nm
  - Maximum speed: 0.5 m/s
- **Materials Whitelist**: Only approved materials (PLA, PETG, TPU, aluminum 6061)
- **Banned Terms**: Filtering for dangerous content (weapon, explosive, lockpick, chemical dispersal)

### 2. New Sandbox-Specific Limits

Additional safety boundaries have been implemented specifically for sandbox operations:

#### Operating Area Constraints
```yaml
operating_area:
  max_radius_m: 50              # Maximum 50-meter operating radius
  require_geofence: true        # Geofencing must be active
```

#### Session Management
```yaml
session_limits:
  max_duration_minutes: 30                    # Maximum 30-minute sessions
  max_operations_per_session: 10              # Maximum 10 operations per session
  cooldown_between_sessions_minutes: 15       # 15-minute cooldown between sessions
```

#### Monitoring and Oversight
```yaml
monitoring:
  log_all_actions: true             # All actions must be logged
  video_recording_required: true    # Video recording required during operations
  real_time_telemetry: true         # Real-time monitoring active
  alert_on_anomalies: true          # Automatic anomaly detection and alerts
```

#### Safety Boundaries
```yaml
safety_boundaries:
  emergency_stop_required: true      # Emergency stop capability required
  human_supervisor_required: true    # Human supervisor must be present
  backup_systems_active: true        # Backup safety systems must be active
```

### 3. Existing Safety Infrastructure (Maintained)

The following safety infrastructure from the broader system remains active:

#### Geofencing
- Enabled geofence system with predefined safe zones
- Home/Office zone: 41.899°N, -87.941°W, 400m radius

#### Escalation Protocols
- **Observe**: Record, log, notify owner
- **Protect**: Retreat, flash light, audible alarm, call help
- **Emergency**: Live stream to owner, geolocate, call 911

#### Forbidden Actions
- Strike, shove, tase, pepper spray
- Lock bypass, weapon mounting
- Any violent or harmful actions

## Implementation Details

### Code Changes

1. **topics.yml**: Updated to enable robotics sandbox with safety constraints
2. **robot_policy.py**: Enhanced to load sandbox_limits configuration
3. **Test Coverage**: Added comprehensive tests to verify safety measures

### Policy Loading

The robotics policy is loaded by:
- `services/robot_core/robot_policy.py` - Main policy loader
- `lyra_learning.py` - Integration with Lyra learning system

### Environment Variables

The system supports environment variable overrides:
- `ROBOTICS_ENABLE`: Can enable/disable robotics functionality
- `ROBOTICS_REPAIR_ENABLE`: Can enable self-repair (use with extreme caution)

## Verification and Testing

### Automated Tests

Comprehensive test suite in `tests/test_robotics_sandbox.py` verifies:
- Sandbox enablement with safety measures intact
- Proper configuration of sandbox limits
- Environment variable override functionality
- Fallback behavior when configuration is missing

### Manual Verification

To verify the configuration:

```python
from services.robot_core.robot_policy import load_policy
policy = load_policy()

# Verify sandbox is enabled
assert policy["enabled"] is True

# Verify safety measures
assert policy["approve_required"] is True
assert policy["self_repair_enabled"] is False
assert "sandbox_limits" in policy
```

## Security Considerations

### Multi-Layer Safety

The sandbox implements multiple layers of safety:

1. **Configuration Layer**: YAML-based settings with safe defaults
2. **Policy Layer**: Code-enforced policy checks
3. **Runtime Layer**: Active monitoring and emergency stops
4. **Physical Layer**: Actuator limits and geofencing

### Fail-Safe Design

- System defaults to disabled state
- All safety measures must be explicitly configured
- Multiple independent safety systems must all be active
- Human oversight required at all levels

### Audit Trail

All robotics operations are:
- Logged with timestamps and details
- Video recorded for review
- Monitored in real-time
- Subject to anomaly detection

## Operational Guidelines

### Before Each Session

1. Verify human supervisor is present
2. Confirm emergency stop is accessible
3. Check geofencing is active
4. Ensure video recording is working
5. Review operation plan for safety

### During Operations

1. Maintain continuous human oversight
2. Monitor real-time telemetry
3. Be prepared to trigger emergency stop
4. Respect session time and operation limits

### After Each Session

1. Review logs and video recordings
2. Check for any anomalies or safety concerns
3. Document any issues or improvements needed
4. Ensure proper cooldown before next session

## Future Enhancements

Potential safety improvements being considered:
- Enhanced anomaly detection algorithms
- Integration with external safety monitoring systems
- Automated safety compliance reporting
- Advanced predictive safety measures

## Contact and Support

For questions about robotics safety configuration:
- Review this documentation first
- Check the test suite for examples
- Consult the broader safety documentation in `docs/SECURITY_CONFIGURATION.md`