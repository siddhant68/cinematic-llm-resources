# DaVinci Resolve installation and MCP setup

The bundle targets the open-source `samuelgursky/davinci-resolve-mcp` server. It is a third-party integration that uses Resolve scripting interfaces.

Read the bundle-level `DAVINCI_MCP_FIRST_TIME_SETUP.md` and generate a passing setup report before a real edit. **Resolve is not assumed to be installed.** When absent, the agent must download the current compatible stable installer from Blackmagic Design, install Resolve and prerequisites, launch it, complete a disposable edit/render test, and only then configure the MCP.

## Edition rule

- Prefer DaVinci Resolve Studio when a valid license is available. Studio provides the dependable direct external-scripting path and the intended AI finishing feature set.
- Do not purchase Studio, expose a key, or invent registration details.
- When the episode brief allows a free fallback, install the current stable free edition and verify the current upstream in-app bridge end to end. Bridge support is version-sensitive; installation alone is not proof.
- If the bridge fails, continue through GUI-only control only when explicitly allowed and a disposable edit/readback/render test succeeds. Otherwise mark setup blocked.
- Never install an old free release solely to regain a scripting path.

## Current setup summary

With Resolve open and a disposable project loaded:

```bash
npx davinci-resolve-mcp setup
npx davinci-resolve-mcp doctor
```

For Studio, set External scripting using to Local. Restart or reload Resolve and the MCP client after configuration changes. Back up the client configuration and configure only the active client unless multiple clients are deliberately requested.

The upstream project recommends compound mode for most assistants. Verify current modes and capabilities from the installed version rather than hard-coding old tool lists.

## Read-only proof

Before editing, read:

- Resolve edition/version and activation state without revealing license data
- MCP version, transport, and server mode
- current project and timeline
- timeline settings
- media-pool roots and offline media
- capability report
- operation risk/dry-run/readback/trace availability

Then use a disposable `_mcp_` project/timeline for one reversible write/readback test and a short independently verified render when supported.

## Configuration check

```bash
python scripts/check_mcp_config.py path/to/mcp-config.json
```

This checks configuration shape only; it does not prove Resolve connectivity.

## Boundary rule

A feature absent from live discovery is unavailable for the session even when older documentation described it. Report UI-only operations or missing Studio-only features rather than faking completion.
