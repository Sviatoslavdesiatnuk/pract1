# Test Plan for Car Power Window

## System Under Test: `CarWindowSystem`
**Goal:** Verify logic correctness and ISO 26262 safety compliance.

### Test Case 1: Normal Operation (Happy Path)
**Objective:** Verify window opens and closes under normal conditions.

| Step | Input Event | Expected Current State | Expected Output Action |
| :--- | :--- | :--- | :--- |
| 1 | (Initial Start) | Idle | None |
| 2 | Send `UpCommand` | MovingUp | startMotorUp |
| 3 | Send `StopCommand` (or release button) | Idle | stopMotor |
| 4 | Send `DownCommand` | MovingDown | startMotorDown |

---

### Test Case 2: Safety Interruption (The Pinch)
**Objective:** Verify that Obstacle Detection overrides movement immediately.

| Step | Input Event | Expected Current State | Expected Output Action |
| :--- | :--- | :--- | :--- |
| 1 | Ensure system is in `Idle` | Idle | - |
| 2 | Send `UpCommand` | MovingUp | startMotorUp |
| 3 | **Send `ObstacleDetected`** | **SafeState** | **lockSystem / stopMotor** |
| 4 | Send `UpCommand` (User tries to press button again) | SafeState | (Ignored/No Action) |

---

### Test Case 3: System Recovery (Reset)
**Objective:** Verify that the system can return to normal operation after a safety lock.

| Step | Input Event | Expected Current State | Expected Output Action |
| :--- | :--- | :--- | :--- |
| 1 | Ensure system is in `SafeState` | SafeState | lockSystem |
| 2 | Send `ResetCommand` | Idle | (System Ready) |
| 3 | Send `UpCommand` | MovingUp | startMotorUp |