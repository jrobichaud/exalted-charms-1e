---
name: build-docs
description: Build the Sphinx documentation and optionally preview it
argument-hint: [--preview]
disable-model-invocation: true
allowed-tools: Bash(cd *), Bash(make *), Bash(sphinx-autobuild *), Bash(open *)
---

# Build Documentation

Build the Sphinx HTML documentation and optionally start a live preview server.

## Instructions

1. **Check if preview mode is requested**
   - If `$1` is "--preview" or "preview", start the autobuild server
   - Otherwise, just build the docs once

2. **Build documentation**

   **One-time build:**
   ```bash
   cd docs && make html
   ```

   **Preview mode (live reload):**
   ```bash
   cd docs && sphinx-autobuild . _build/html
   ```

3. **Report results**
   - For one-time build: confirm build completed and show output path
   - For preview mode: show the URL where docs can be viewed (usually http://127.0.0.1:8000)
   - If there are build warnings or errors, display them

4. **Optional: Open in browser**
   - If preview mode, offer to open the browser automatically
   - On macOS: `open http://127.0.0.1:8000`

## Examples

- "/build-docs" - build once
- "/build-docs --preview" - build and start live preview server
- "/build-docs preview" - alternative syntax for preview mode