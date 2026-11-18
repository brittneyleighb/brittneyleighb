<div align="center">

![Animated green phosphor terminal showing current technical focus](assets/retro-terminal.svg)

![Rotating roles](assets/role-loop.svg)

**MS Computer Science student focused on operating systems, distributed systems, developer tools, and interaction design.**

`$` [cd bit-foundry-labs](https://github.com/bit-foundry-labs) · `$` [ls project-index](#project-index) · `$` [cat field-notes](#field-notes)

</div>

## /now

```text
$ cat /now
RESEARCH   Embers Kernel: capabilities, IPC, and memory ownership
BUILDING   Sakura Study App and Mindful Moments
STUDYING   Internet Architecture & Protocols
```

```text
$ git status --short
LAST SHIP       profile terminal interface · 2026-11-18
NEXT MILESTONE  Embers Kernel IPC v1
```

## /featured/embers-kernel

```
             ┌──────────────────────┐
             │   EMBERS KERNEL      │
             │  Rust · no_std       │
             └──────────┬───────────┘
                        │ capabilities · IPC · memory ownership
              ┌─────────▼─────────┐
              │  trusted kernel   │
              └─────────┬─────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
   user-space services         deterministic tests
```

![Animated cascading ASCII character rain](assets/ascii-rain.svg)

[**Embers Kernel**](https://github.com/bit-foundry-labs/embers-kernel) is a Rust-first microkernel research project exploring capability-based isolation, predictable resource control, and a small trusted computing base.

Early-stage research, not a finished or benchmark-proven kernel.

### /collaborate

Interested in helping? The most useful starting points are Rust/`no_std`, QEMU-based testing, documentation, and review of capability or IPC design. Begin with the [contributor guide](https://github.com/bit-foundry-labs/embers-kernel/blob/main/CONTRIBUTING.md), then choose a scoped task from the [roadmap](https://github.com/bit-foundry-labs/embers-kernel/blob/main/docs/CONTRIBUTOR_ROADMAP.md) or [open issues](https://github.com/bit-foundry-labs/embers-kernel/issues).

## /project-map

```text
SYSTEMS RESEARCH
├── Embers Kernel ── capability isolation · IPC · memory ownership
├── Emberglass OS ── desktop UX · local-first AI boundaries
└── Forge Loop ──── approved local agent execution

APPLICATION WORK
├── Mindful Moments ─ bilingual mindfulness + journaling
└── Sakura Study App ─ study workflows for iPad and iPhone
```

## /project-records

<details>
<summary><code>$ open embers-kernel --details</code></summary>

<br>

**Stack:** Rust, `no_std`, x86-64, QEMU  
**Current focus:** capability model, protected memory, IPC guarantees  
**Public repository:** [bit-foundry-labs/embers-kernel](https://github.com/bit-foundry-labs/embers-kernel)

</details>

<details>
<summary><code>$ open emberglass-os --details</code></summary>

<br>

**Stack:** Rust, Linux-native desktop technologies  
**Current focus:** activity-centered UX and local-first AI boundaries  
**Availability:** private research project

</details>

<details>
<summary><code>$ open forge-loop --details</code></summary>

<br>

**Current focus:** explicit approvals, execution limits, and evidence reporting for local agent work  
**Availability:** private developer-tool project

</details>

<details>
<summary><code>$ open mindful-moments --details</code></summary>

<br>

**Stack:** Flutter, Supabase  
**Current focus:** bilingual daily activities and saved journal entries  
**Availability:** private app project

</details>

## /project-index

**Systems:** [Raft KV Store](https://github.com/brittneyleighb/raft-project) · [Neural Trace](https://github.com/brittneyleighb/neural-trace)

**Apps + games:** [Café Nebula](https://github.com/brittneyleighb/cafe-nebula) · Ándale (private)

## /field-notes

[Operating systems](https://github.com/brittneyleighb/notes-on-operating-systems) · [Database design](https://github.com/brittneyleighb/database-design-master-reference) · [Programming languages](https://github.com/brittneyleighb/programming-languages-comparison) · [Git cheatsheet](https://github.com/brittneyleighb/git-github-cheatsheet)

<details>
<summary><code>$ cat operator-notes</code></summary>

<br>

I care about:

- Local-first software that remains useful without a permanent network dependency.
- Explicit permissions, resource boundaries, and systems whose behavior can be inspected.
- Reproducible builds and tests that make claims checkable.
- Interfaces that make powerful technical work feel understandable.

</details>

<details>
<summary><code>$ sudo make coffee</code></summary>

<br>

```text
make: *** No hardware target detected. Stop.
hint: back to the keyboard.
```

</details>

[**Bit Foundry Labs**](https://github.com/bit-foundry-labs) · [**Email**](mailto:brittneyleighb@gmail.com)
