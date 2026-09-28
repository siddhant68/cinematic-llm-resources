# DaVinci Resolve and MCP first-time autonomous setup

Use this document before the first real editing session. **Do not assume DaVinci Resolve is already installed.** When Resolve is absent, the fresh AI agent owns the download, installation, first launch, dependency setup, MCP configuration, and disposable verification described below.

The selected integration is the open-source `samuelgursky/davinci-resolve-mcp` project. It is a third-party MCP server, not an official Blackmagic product, although it uses Resolve's supported scripting interfaces.

## Required end state

Setup is complete only when the agent has produced all of the following:

- a current stable DaVinci Resolve installation from an official Blackmagic source
- the installed edition, version, architecture, install path, and activation state recorded
- a successful Resolve launch and disposable local project test
- required local dependencies installed and verified
- the MCP configured for the active AI client in compound mode
- a successful read-only MCP connection test
- one harmless reversible write followed by readback in a disposable `_mcp_` project or timeline
- `planning/DAVINCI_MCP_SETUP_REPORT.md` with evidence and any remaining limitations

A missing Resolve installation is setup work, not a reason to stop or ask the user to install the application manually.

## Installation authority and boundaries

The fresh agent is authorized to:

- inspect the operating system, CPU architecture, GPU, memory, free disk space, and existing installations
- use available browser, desktop-control, terminal, and package-manager tools
- download the current **stable** Resolve installer from Blackmagic Design
- install Resolve and ordinary prerequisites such as Node.js, Python, and FFmpeg
- launch and restart Resolve or the MCP client when needed
- create and remove disposable test projects whose names begin with `_mcp_`
- configure the active MCP client after backing up its configuration

The agent must not:

- purchase DaVinci Resolve Studio or enter payment details without explicit authorization
- invent, expose, or store a Studio activation key in logs, prompts, reports, or skill folders
- bypass operating-system security, antivirus, Gatekeeper, driver-signing, or license controls
- download Resolve from mirrors, software aggregators, torrents, or unofficial repackagers
- install a beta build unless `EPISODE_BRIEF.json` explicitly permits it
- downgrade to an obsolete free build merely to recover an old scripting loophole
- reboot the computer unless the episode brief permits it or the user approves the exact reboot
- touch production media or a real project during setup

The agent should interrupt the user only for a genuine non-automatable gate such as an administrator credential/UAC approval, a Studio license activation, personal information required by the official download form that the agent is not authorized to invent, or an operating-system restart. Ask for the single exact action, then continue setup. Do not delegate routine downloading, installation, configuration, or testing back to the user.

## Edition decision

Use this decision order:

1. **Studio license available:** Install the latest stable DaVinci Resolve Studio release compatible with the machine. Studio is the preferred production path because direct external scripting and key AI finishing features are available there.
2. **Studio license not available, but free fallback allowed:** Install the latest stable free DaVinci Resolve release from Blackmagic Design. Record that the selected MCP's direct external scripting path is unavailable in the free edition.
3. **Free-edition MCP bridge:** Attempt the upstream in-app bridge only when the installed Resolve version is explicitly supported by the current MCP documentation and the bridge passes an end-to-end disposable test. Do not report success from installation alone.
4. **Bridge unavailable:**
   - Continue in GUI-only mode only when the agent has dependable desktop control, `EPISODE_BRIEF.json` permits that fallback, and a disposable edit/readback/render test succeeds.
   - Otherwise stop before the production edit and report that a Studio license or another approved control path is required.

Do not silently replace Resolve with Palmier when Resolve setup fails. A fallback that changes the agreed quality and source-preservation workflow requires an explicit decision.

### Important free-edition limitation

The MCP project's current documentation says free-edition bridge behavior is version-sensitive, and recent Resolve releases may no longer expose the Python script path used by the bridge. Treat free-edition automation as a verified-at-runtime fallback, not as a dependable promise.

When the free edition is used, also verify whether planned features are actually available. For example, Magic Mask and some AI audio tools are Studio features; use manual tracked Fusion masks/rotoscoping or revise the plan rather than pretending those tools ran.

## Phase 1 — Machine and compatibility preflight

Before downloading anything, record:

```text
operating system and version
CPU architecture
GPU model and driver status
installed memory
free system-disk space
free project/media-disk space
existing Resolve or Blackmagic components
active AI/MCP client
available browser and desktop-control capability
Node.js/npm/npx status
Python status
ffmpeg/ffprobe status
Studio license availability: yes / no / unknown
```

Then:

1. Check current Blackmagic minimum requirements for the chosen stable release.
2. Reject an incompatible installer architecture.
3. Prefer a stable release over a public beta.
4. Preserve at least enough free disk space for the application, cache, proxies, render cache, and project backups.
5. Do not install into a container, headless host, or remote machine that cannot run Resolve's graphical application and GPU pipeline.

## Phase 2 — Download and install DaVinci Resolve

1. Open the official Blackmagic DaVinci Resolve product or support page.
2. Identify the current stable release and the correct platform/architecture.
3. Select Studio only when a valid license is available or the user has explicitly authorized activation. Otherwise use the free edition when fallback is allowed.
4. Download the installer directly from Blackmagic Design. Complete the official download form only with authorized information; never fabricate identity or contact details.
5. Verify that the downloaded package came from a Blackmagic domain and passes the platform's normal publisher/signature checks.
6. Run the native installer using the standard application location unless the environment requires another documented path.
7. Install the Resolve application. Skip unrelated hardware-panel drivers or utilities when clearly optional and no such hardware is present; do not remove components required by Resolve.
8. Preserve any existing Blackmagic configuration and project libraries. Never uninstall or overwrite an existing installation without first exporting/backing up project databases and receiving approval.
9. Launch Resolve after installation.
10. Complete first-run configuration with conservative local defaults. Do not enable cloud collaboration, upload media, or sign into unrelated services unless the episode brief authorizes it.
11. Create a local disposable project library and a project named `_mcp_install_test`.
12. Record the exact installed edition and version from Resolve itself, not only from the installer filename.

### Platform notes

- **Windows:** Use the signed official Windows installer for the detected architecture. A UAC prompt can require one user approval. Do not disable Windows security or install unsigned substitutes.
- **macOS:** Use the official disk image/package and allow Gatekeeper to verify the developer signature. An administrator password can require one user action. Do not remove quarantine flags to bypass a failed signature check.
- **Linux:** Use Blackmagic's official Linux package and current dependency guidance. Verify supported distribution, GPU, and driver requirements before installation. Do not force-install on an incompatible distribution merely to complete the checklist.

## Phase 3 — First launch and Resolve verification

With `_mcp_install_test` open:

1. Confirm the Edit, Fusion, Color, Fairlight, and Deliver pages open.
2. Create an empty timeline using the intended delivery frame rate and resolution.
3. Import only a generated test card or harmless temporary clip; never import production media during setup.
4. Add a title, make one trim or transform, and render a very short local test.
5. Verify the rendered file with `ffprobe` and play representative frames.
6. Record GPU warnings, codec limitations, missing features, crashes, or performance blockers.
7. Remove or retain the disposable project according to the setup report, but do not leave it confused with the real project.

Resolve is not considered installed successfully merely because the installer completed. It must launch and perform this disposable edit/render test.

## Phase 4 — Install prerequisites

Install missing prerequisites through trusted official installers or the operating system's normal package manager:

- Node.js LTS with `npm`/`npx` for the MCP bootstrap
- Python 3.10 or newer; prefer 3.10–3.12 when the installed Resolve/MCP combination has no reason to require a newer version
- `ffmpeg` and `ffprobe`

Record versions and executable paths. Do not install packages into random Python environments. The MCP setup creates or identifies its managed environment; optional Python packages must be installed into that environment.

## Phase 5 — Configure Resolve scripting

### Studio path

Open Resolve and set:

```text
DaVinci Resolve > Preferences > System > General
External scripting using: Local
```

The exact wording can vary by platform/version. Use permitted desktop control to make the change and restart Resolve when required. Prefer Local over Network unless Resolve and the MCP intentionally run on different machines.

### Free-edition bridge path

Do not assume the Studio preference enables scripting in the free edition. Follow the **current** upstream `Free edition (in-app bridge)` instructions only when they state that the installed Resolve version is supported. The bridge must run from Resolve's Scripts menu and pass authenticated loopback read/write tests. If Python scripts do not appear or the bridge cannot connect, classify the bridge as unavailable rather than repeatedly forcing it.

## Phase 6 — Install and configure the MCP

With Resolve open and a disposable project loaded, run:

```bash
npx davinci-resolve-mcp setup
```

The installer should:

- install a managed copy in the user application-data directory
- create its managed Python environment
- detect Resolve paths
- configure only the active MCP client unless multiple clients were deliberately requested
- use compound mode by default

Back up the client's configuration before changing it and merge the MCP entry without deleting unrelated servers or comments.

For an explicit multi-client setup only when needed:

```bash
npx davinci-resolve-mcp setup --clients all
```

Then run:

```bash
npx davinci-resolve-mcp doctor
```

Restart or reload the MCP client after configuration changes. An exit code of zero is not sufficient evidence of connectivity.

## Phase 7 — Connection and disposable write test

Perform a read-only test:

1. Read the Resolve edition and version.
2. Read the current project and timeline.
3. Read timeline settings.
4. List media-pool roots without modifying them.
5. Inspect available MCP capabilities, server version, transport, and server mode.

Then perform a disposable write/readback test:

1. Use only `_mcp_install_test` or another `_mcp_` project.
2. Create an empty `_mcp_` timeline if needed.
3. Add a harmless marker or title.
4. Read the change back through the MCP.
5. Make one reversible transform or text change when supported.
6. Read that change back.
7. Render a few seconds from the disposable timeline when the MCP exposes a safe render path.
8. Verify the output file independently.
9. Remove or retain the test project safely.

Do not open, import, relink, transcode, rename, move, or modify production assets during these tests.

## Optional analysis dependencies

Install only the capabilities required for the episode, into the MCP-managed environment:

- `numpy` for supported analysis/balancing helpers
- `librosa` for beat, bar, and phrase detection
- `openai-whisper` for permitted local transcription
- `open_clip_torch` for supported visual-similarity workflows
- `transformers` for supported audio embeddings
- `opencv-python` for additional frame analysis

Model weights have licenses separate from the software package. Record exact models and licenses before commercial use.

## Setup report requirements

Write `planning/DAVINCI_MCP_SETUP_REPORT.md` with:

```text
setup timestamp
operating system and architecture
hardware compatibility result
installer source page and downloaded filename
package signature/publisher verification
installed Resolve edition and exact version
Studio activation state without exposing the key
install path
first-launch result
disposable GUI edit/render evidence
Node, Python, ffmpeg, and ffprobe versions/paths
MCP package version and managed install path
active MCP client and backed-up config path
server mode and transport
Resolve scripting setting or free-edition bridge details
read-only connection evidence
disposable write/readback evidence
render verification evidence
available and missing capabilities
manual intervention required, if any
production readiness: PASS / CONDITIONAL / BLOCKED
exact next action
```

`PASS` requires a verified control path and disposable readback. `CONDITIONAL` must name the unavailable features and approved workaround. `BLOCKED` must state the smallest user action needed; it must not hide the failure by switching tools.

## Copy-paste autonomous setup prompt

Give the following block to a fresh agent together with this file:

```text
FIRST-TIME DAVINCI RESOLVE + MCP AUTONOMOUS SETUP

DaVinci Resolve is not assumed to be installed. You are authorized to perform all routine, non-destructive local setup needed to install DaVinci Resolve, launch and verify it, install prerequisites, connect this AI session through the current samuelgursky/davinci-resolve-mcp package, and prove the setup in a disposable project.

1. Read DAVINCI_MCP_FIRST_TIME_SETUP.md and EPISODE_BRIEF.json before acting.
2. Do not stop merely because Resolve, Node, Python, ffmpeg, or the MCP is absent. Detect and install the missing approved components yourself using official sources or trusted system package managers.
3. Detect the OS, architecture, GPU, memory, free disk space, current AI/MCP client, available UI-control capability, and any existing Blackmagic installation.
4. Download the latest compatible stable DaVinci Resolve installer only from Blackmagic Design. Do not use a beta, mirror, repack, or old free build selected solely for scripting.
5. Install Studio when a valid Studio license is available. Otherwise install the latest stable free edition only when the episode brief permits it, then treat MCP automation as unproven until the current upstream bridge passes end to end.
6. Do not purchase Studio, expose a license key, invent registration details, bypass security, or reboot the computer without explicit permission. Ask me only for a genuine non-automatable administrator, registration, activation, or reboot gate; handle every other setup step yourself.
7. Launch Resolve, complete conservative local first-run setup, create `_mcp_install_test`, and prove a disposable edit plus short render before configuring the real workflow.
8. Install and verify Node.js LTS, an appropriate Python version, ffmpeg, and ffprobe when missing.
9. For Studio, set External scripting using to Local with permitted desktop control. For the free edition, use the in-app bridge only when the installed version is explicitly supported by the current MCP documentation and the bridge passes read/write tests.
10. Back up the active MCP client's configuration. Run `npx davinci-resolve-mcp setup`, configure only the active client in compound mode, and run `npx davinci-resolve-mcp doctor`.
11. Reload the client and perform read-only Resolve tests followed by one harmless reversible MCP write/readback in the disposable `_mcp_` project. Verify any test render independently.
12. Never open, move, rename, transcode, relink, or modify production media or a real project during setup.
13. Write `planning/DAVINCI_MCP_SETUP_REPORT.md` with all required evidence and a PASS, CONDITIONAL, or BLOCKED decision.
14. Do not begin the real edit until setup is PASS or I explicitly approve a named conditional path.

Do not ask me to download or install routine components manually. Escalate only the exact system or license gate that you cannot legally or technically complete with the tools available in the session.
```

## Recovery

When installation or connection fails:

1. Distinguish application-install failure, first-launch failure, scripting failure, MCP configuration failure, and client reload failure.
2. Verify the installer source, package integrity/signature, architecture, GPU/driver compatibility, and free disk space.
3. Confirm Resolve opens a disposable project before debugging the MCP.
4. Confirm Studio is activated when the Studio path was selected.
5. Confirm External scripting is Local for Studio.
6. Run `npx davinci-resolve-mcp doctor` again.
7. Inspect the active client's MCP config and logs.
8. Confirm the client was reloaded after configuration changes.
9. Run `npx davinci-resolve-mcp sync` when the managed installation is incomplete or stale.
10. Re-run only the disposable read/write test.

Do not solve a setup issue by weakening system security, using a pirated license, installing unofficial binaries, or silently lowering the production-quality standard.

## Source references

- DaVinci Resolve official product page: https://www.blackmagicdesign.com/products/davinciresolve
- DaVinci Resolve Studio features: https://www.blackmagicdesign.com/products/davinciresolve/studio
- Blackmagic Design support/downloads: https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion
- MCP repository: https://github.com/samuelgursky/davinci-resolve-mcp
- MCP installation guide: https://github.com/samuelgursky/davinci-resolve-mcp/blob/main/docs/install.md
