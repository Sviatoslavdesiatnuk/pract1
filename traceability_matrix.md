# ISO 26262 Traceability Matrix
**Project:** Car Power Window System
**Date:** Week 3, Day 5

| ID Вимоги | Опис Вимоги (Requirement) | Елемент Архітектури (Code Logic) | ID Тесту (Verification) | Статус |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Система має відкривати та закривати вікно за командою водія. | `Idle --> MovingUp` <br> `Idle --> MovingDown` | **Test Case 1** (Normal Operation) | ✅ PASS |
| **REQ-02** | (Safety) Система має негайно зупинити рух при виявленні перешкоди. | `MovingUp --> SafeState : ObstacleDetected` | **Test Case 2** (Safety Interruption) | ✅ PASS |
| **REQ-03** | (Safety) Після аварійної зупинки система має бути заблокована. | `state SafeState { ... }` (No exit except Reset) | **Test Case 2** (Step 4 check) | ✅ PASS |
| **REQ-04** | Система може повернутися до роботи тільки після ручного скидання помилки. | `SafeState --> Idle : ResetCommand` | **Test Case 3** (Recovery) | ✅ PASS |