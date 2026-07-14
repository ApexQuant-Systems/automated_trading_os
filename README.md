# Automated Trading OS (APEX Engine v4.0)

## 1. Purpose
An institutional-grade, multi-asset quantitative research and unsupervised cloud execution infrastructure platform. Strategy cartridges run entirely decoupled as plugins separate from the permanent operational engine kernel.

## 2. Unidirectional Dependency Architecture
Data Layer ➔ Market Intelligence ➔ Strategy Plugins ➔ Risk Firewall ➔ Execution Plugs
* Higher layers read state blocks from lower matrices.
* Lower levels remain 100% blind to higher configurations (Broker adapter never knows entry rules).

## 3. Module Maturity Ladder
* **L1 (Implemented):** Structural code compiled inside package.
* **L2 (Unit Tested):** Local file assertion tests return 100% pass verification.
* **L3 (Integration Tested):** Survives out-of-process data flow interactions.
* **L4 (Regression Protected):** Changes lock automated rollback check gates.
* **L5 (Frozen Keys):** Sealed production asset; immutable without design proposal documentation.

## 4. Git Invariance Workflow
* Direct development changes to the `main` branch are permitted only during Phase 0 initialization.
* Downstream features must be engineered inside isolated `dev-module-X.X` branches.
* Commits must follow structural patterns mapping to primitives: `infra(core):` or `test(risk):`.