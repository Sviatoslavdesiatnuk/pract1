# SysML v2 Automotive Knowledge Base

## SECTION 1: SYNTAX RULES (SysML v2 Textual Notation)
These rules define valid syntax for generating SysML v2 state machines.

1.  **Structure:** All state machines must be wrapped in a `package`.
2.  **Definitions:** Use `item def` for signals/events and `state def` for the state machine logic.
3.  **Initialization:** Every state definition must have an initial node defined as: `entry; then StateName;`.
4.  **Transitions:**
    * Format: `transition t_name from SourceState to TargetState { ... }`
    * Trigger: Use `accept EventName;` inside the transition.
    * Guard: Use `if condition;` inside the transition.
    * Effect: Use `do ActionName;` inside the transition.
5.  **Actions:** Use `entry do ActionName;` for state entry actions and `do ActionName;` for ongoing activities.
6.  **Terminators:** All statements must end with a semicolon `;`.

## SECTION 2: SAFETY CONSTRAINTS (ISO 26262)
These rules must be strictly followed for automotive safety compliance.

1.  **RULE: Safety State.** Every system MUST have a dedicated `SafeState` (or `EmergencyMode`) where the system goes in case of critical failure.
2.  **RULE: Escape Transition.** There MUST be a high-priority transition from the main operational state (usually a composite state) to the `SafeState` triggered by a `Fault` or `Error` event.
3.  **RULE: No Deadlocks.** Every state (except Final) MUST have at least one outgoing transition.
4.  **RULE: Determinism.** Guard conditions from a single state MUST be mutually exclusive (e.g., `x > 5` and `x <= 5`).
5.  **RULE: Reachability.** All states must be reachable from the initial state.
6.  **RULE: Initialization.** All composite states MUST have an internal `entry; then ...` statement.

## SECTION 3: GOLDEN PATTERNS (Design Patterns)
Use these examples as templates for specific automotive behaviors.

### Pattern 1: The Watchdog Timer
*Description:* A mechanism to detect system freezes. If the software does not "kick" (reset) the watchdog within a specific time, the system resets.

**Code Template:**
```sysmlv2
package WatchdogPattern {
    item def ClockTick;
    item def SoftwareAliveSignal;
    item def ResetCommand;

    state def WatchdogLogic {
        entry; then Monitoring;

        state Monitoring {
            entry; then Counting;
            
            state Counting;
            
            // If software signals it is alive, reset the counter (Self-transition)
            transition refresh from Counting to Counting {
                accept SoftwareAliveSignal;
            }
            
            // If time runs out without a signal -> Fault
            transition timeout from Counting to ErrorMode {
                accept ClockTick; 
                // implicitly assumes counter reached limit
            }
        }

        state ErrorMode {
            entry do SystemReset;
        }

        transition recovery from ErrorMode to Monitoring {
            accept ResetCommand;
        }
    }
}
```