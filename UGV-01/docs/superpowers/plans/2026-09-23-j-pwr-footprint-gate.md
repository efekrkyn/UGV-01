# J-PWR Footprint Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bind the proposed J-PWR electrical pinout to the installed KiCad 10 Mega-Fit 2×2 footprint and reject any pad swap that puts ACT_BUS next to 5V_CONTROL.

**Architecture:** Keep one JSON map for four nets and wire gauges. A small stdlib check reads the KiCad footprint pads, verifies two positives are diagonal, and proves a deliberately swapped map fails.

**Tech Stack:** Python 3 stdlib, KiCad 10 footprint text.

**Spec:** [PWR–MCU interface](../../pwr_mcu_interface.md).

## Global Constraints

- Electrical map: pad 1 `ACT_BUS`, pads 2/3 `PGND_A`/`PGND_B`, pad 4 `5V_CONTROL`.
- Connector MPN `768290004`; footprint `Connector_Molex:Molex_Mega-Fit_76829-0004_2x02_P5.70mm_Vertical`.
- This checks PCB pad geometry only; cable-side cavity orientation still requires producer drawing/sample check.

## Review Focus

- ACT_BUS/5 V swapped to adjacent pads must fail the map check.
- Missing or duplicate pad/net must fail.
- A 1×4 footprint under the same connector name must fail the 2×2 coordinate check.
- A disconnected GND pin must fail the four-net check.
- The checked part/footprint must not be presented as a released crimp drawing.

---

### Task 1: Connector map and pad check

**Files:**
- Create: `config/pwr_mcu_connector.json`
- Create: `tests/check_pwr_mcu_connector.py`
- Modify: `docs/pwr_mcu_interface.md`

**Interfaces:**
- Consumes: installed KiCad footprint text and J-PWR pinout in the spec.
- Produces: JSON `pins` array with `{pad,net,awg}` and one runnable check.

- [x] **Step 1:** Write test that loads the JSON and footprint, verifies the four unique pad names and that positive pad coordinates differ in both X and Y; mutate pad 4 to pad 2 and require a failure.
- [x] **Step 2:** Run `python3 tests/check_pwr_mcu_connector.py`; failed while JSON was absent.
- [x] **Step 3:** Add the four-pin JSON map and link it from the interface document, recording KiCad's pad coordinates and courtyard. State the mating housing wire-side orientation remains open.
- [x] **Step 4:** Run the same check, `python3 tests/check_design.py` and `python3 tests/check_mcu_pinmap_integration.py`; all passed.

No commit is planned: the project directory is presently untracked in its parent repository.
