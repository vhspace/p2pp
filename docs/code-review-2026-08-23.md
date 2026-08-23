# Post-Merge Code Review — 2026-08-23

Audit of the 12 PRs merged to `vhspace/p2pp` on 2026-08-22/23 (session batch, merged with
bot-only approval; no human code review). Each commit diff was read in full and checked
against the surrounding code for correctness, security, completeness, and consistency.

**Summary:** 4 real bugs found (issues filed — #74, #75, #76, #77), plus several
concerns/nits. The most serious: unresolved merge-conflict markers were committed to
`README.md` (#71) and `.gitignore` (#72) [#74], and PR #69's WebEngine security fix is
incomplete — `--disable-web-security` is still applied on every launch via an env var set in
`p2pp/main.py` [#75].

---

## PR #59 — docs: fix getting started typos in README

- **Verdict**: LGTM
- **Findings**: Clean as merged. Note: PR #71 (merged later) re-introduced the
  "get youstarted." typo inside a block of unresolved merge-conflict markers now present in
  `README.md`; fixing that conflict (see #72 finding / filed issue) will restore this PR's intent.

## PR #60 — fix: three small G-code generation bugs (temp-wait Y, SIDEWIPEZHOP, purge position 0)

- **Verdict**: LGTM
- **Findings**: All three fixes verified against surrounding code:
  - `calculate_temp_wait_position()` returns `[pos_x, pos_y]` (p2pp/mcf.py:77), so using
    `[1]` for Y is correct.
  - `last_posx`/`last_posy` are initialized to `None` at module level
    (p2pp/purgetower.py:33-34), so the `is not None` comparison is correct and X=0/Y=0
    towers now behave properly.
  - `v.addzop` is the parsed `SIDEWIPEZHOP` value (p2pp/p2ppparams.py:443); guard
    `> 0.0` keeps zero default behavior.
  - Nit (pre-existing): the SIDEWIPE z-hop is never lowered back within
    `create_side_wipe`; unchanged by this PR since slicer re-issues absolute Z.

## PR #63 — fix(deps): bump urllib3 pin to >=1.26.20,<2 (CVE-2024-37891)

- **Verdict**: LGTM
- **Findings**: Pin is correct (CVE fixed in 1.26.19; `<2` keeps requests-toolbelt/requests
  compatibility). All four platform requirement files include `-r requirements-common.txt`,
  so coverage is complete.
  - Nit (pre-existing): `setup.py install_requires` says `requests>=2.31.0` while
    `requirements-common.txt` says `>=2.28.0`.

## PR #64 — config_gui: JSON lastconf.conf + fix wrong-key config restore bugs

- **Verdict**: LGTM
- **Findings**: Good change set:
  - Replacing pickle with JSON removes a code-execution-on-unpickle vector. Legacy pickle
    files raise `ValueError`/`UnicodeDecodeError`/`OSError`, all caught — safely ignored.
  - `store["start_gcode"]` is the real key (read back at config/config_gui.py:304); the old
    `"startup_gcode"` write silently dropped filtered content.
  - Verified `accmode_pplus` and `bb3d_autoadd` widgets exist in `p2ppconf.ui`, so the new
    `setChecked` calls are valid.
  - Duplicate `bb_autoadd` dict key removed.

## PR #65 — Fix Palette 3 output-name checks to use the output path

- **Verdict**: Issues found → https://github.com/vhspace/p2pp/issues/77
- **Findings**:
  - **Real bug (filed)**: both P3 warnings run *before* `parse_config_parameters()`
    sets `v.palette3 = True` (`p2pp/mcf.py:1010` vs `p2pp/mcf.py:1040`;
    `v.palette3` only becomes True in `check_config_parameters`
    [p2pp/p2ppparams.py:89,102]). In a normal single-file run the checks evaluate while
    `v.palette3` is still `False`, so they remain unreachable — before *and* after this PR.
    The fix corrected *which* variable holds the output name but not the ordering bug that
    makes the checks dead code. Issue #56's symptom (no warning) persists.
  - The accessory-mode change (`gcode_file = output_file`) is correct: `os.path.join(path,
    output_file)` duplicated a relative directory component and was a no-op hazard for
    absolute paths.
  - Behavior note: when `SLIC3R_PP_OUTPUT_NAME` is absent, the `.mcfx` check now runs
    against the *input* gcode name in the KeyError fallback path — fine once the ordering
    bug is fixed, but worth knowing.

## PR #66 — Add working p2pp:main entry point for Linux gui_scripts

- **Verdict**: Concerns
- **Findings**:
  - Entry point wiring is correct and complete: `setup.py` declares `p2pp=p2pp:main`,
    `p2pp/__init__.py` defines `main()` delegating to `p2pp/main.py`; P2PP.py shim keeps
    py2app/direct invocation working. Mechanical comparison of moved code shows a faithful
    relocation (indentation-only).
  - `uifiles.find_ui()` (argv dir → `/usr/share/p2pp` → cwd) matches setup.py `data_files`
    install layout. Reasonable.
  - **Security regression carried forward**: the move preserved
    `QTWEBENGINE_CHROMIUM_FLAGS="--disable-web-security"` into `p2pp/main.py:18-20`.
    See #69 findings — this made #69's fix incomplete.
  - Note: `.ui` files live at repo root, so MANIFEST.in's `include p2pp/*.ui` and
    package_data `'p2pp': ['*.ui']` match nothing (pre-existing).

## PR #67 — Remove dead code: bedprojection module, omega profile clobber, sidewipe format typos

- **Verdict**: LGTM
- **Findings**:
  - No remaining references to `bedprojection`/`bp` anywhere after removal.
  - omega.py: removing the pre-branch assignment and the trailing clobber is right — for
    P3 the profile now stays the intended doubled 32-char string (consistent with the
    PALETTE3 parse warning that demands 32 chars), and the warning text now shows the
    actual value.
  - `{:3f}` → `{:.3f}` changes E-value precision from 6 to 3 decimals, matching blobster
    formatting as stated. Fine.

## PR #68 — fix: bump version.py to 10.2.2

- **Verdict**: LGTM
- **Findings**: Clean; `Version` formats as `10.02.02` and parses fine with
  `packaging.version` for the update check.
  - Nit: `releaseinfo` changelog dict has no `10.2.x` entries (ends at 10.0.0).

## PR #69 — fix(security): remove --disable-web-security and --insecure-content from WebEngine

- **Verdict**: Issues found → https://github.com/vhspace/p2pp/issues/75
- **Findings**:
  - **Real bug / incomplete fix (filed)**: the PR removed `QWebEngineSettings`
    attributes in `p3_upload.py`, but `--disable-web-security` is still applied on every
    launch through `QTWEBENGINE_CHROMIUM_FLAGS` set in `p2pp/main.py:18-20` (moved there
    from the old P2PP.py by #66, which merged earlier). Since P2PP.py is now just a shim
    into `main()`, all launch paths still run Chromium with web security disabled — the
    vulnerability described in issue #53 is not actually closed.
  - Functional note for the follow-up: the rotated-preview page uses `setHtml()` with a
    cross-origin `<iframe src="http://<host>:5000">`; removing the flag may break that
    preview unless it is reworked (e.g., load the URL directly, or use
    `setUrl`/local handler). Needs testing when the flag is finally removed.
  - The removed lines themselves (`LocalContentCanAccessRemoteUrls`,
    `AllowRunningInsecureContent`) had no other consumers; import cleanup is complete.

## PR #70 — fix(security): validate P3_HOSTNAME before URL interpolation

- **Verdict**: LGTM
- **Findings**: Solid little hardening fix:
  - Regex `^[A-Za-z0-9._-]+$` rejects `:`/`/`/`@`/whitespace/control chars, blocking URL
    component injection (path, userinfo, query/fragment smuggling). Input is stripped
    first, so `$`-before-trailing-newline regex semantics are not exploitable.
  - `_validated_host` in `uploadfile()` cannot be used unbound: any exception raised
    before assignment also sets `_error`, and the browser branch is gated on
    `_error is None`. Invalid hostname sets `_error`, disables retry, aborts cleanly.
  - Hostname typed into the GUI retry dialog (p3_upload.py:65,148) is validated inside
    the loop before use. Config-sourced values validated at parse time with a warning.
  - Tests included and passing (`python3 tests/test_p3_hostname_validation.py`).
  - Nits: allows dot-only/dash-leading strings (harmless in URL host position);
    IPv6 literal rejected by design (documented in tests).

## PR #71 — fix: replace tomvandeneede paths with vhspace in DMG/ZIP scripts

- **Verdict**: Issues found → https://github.com/vhspace/p2pp/issues/74 (README conflict markers)
- **Findings**:
  - **Real bug (filed)**: the commit merged with unresolved conflict markers; `README.md`
    now contains literal `<<<<<<< HEAD` / `=======` / `>>>>>>> ce4ea2b ...` blocks that
    duplicate the Getting Started section and resurrect the "get youstarted." typo that
    #59 had fixed. Still broken on master today.
  - URL replacements in `config_gui.py`, `gui.py`, `mcf.py` are fine, but incomplete:
    three `tomvandeneede` wiki/issue URLs remain in `p2pp/main.py:81,93,118` (the file
    created by #66 earlier in the same session).
  - Scope notes (acceptable but worth tracking): build scripts now hardcode
    `/Users/vhspace/...` and `c:\users\vhspace\...` personal Dropbox paths instead of
    parameterizing them; `tower/tower.py` still saves to `/Users/vhspace/Desktop/tower.png`.
  - Pre-existing AppImage issues untouched by this PR even though adjacent lines changed:
    `AppIMageBuilder.yml` copies a nonexistent `requirements.txt` (repo has
    `requirements-{common,linux,mac,win}.txt`), icon key typo `icon.icn`, and
    `exec_args` points at `usr/src/P2PP` (file is `P2PP.py`). noble/python3.12 changes
    are internally consistent.

## PR #72 — fix: untrack generated image_rc.py (755KB) + .gitignore

- **Verdict**: Issues found → https://github.com/vhspace/p2pp/issues/74, https://github.com/vhspace/p2pp/issues/76
- **Findings**:
  - **Real bug (filed)**: `.gitignore` was committed with unresolved conflict markers
    (`<<<<<<< HEAD` … `>>>>>>> dea3715 ...`). Functionally `image_rc.py` still ends up
    ignored, but the file is corrupt/confusing and will swallow future edits near those
    lines.
  - **Real bug (filed)**: untracking `image_rc.py` breaks fresh clones and Linux
    packaging: `import image_rc` runs at module level in `p2pp/gui.py:14` and
    `config/config_gui.py:11`; `setup.py` lists it in `py_modules=['version','image_rc']`;
    `MANIFEST.in` includes it. Generation exists only in the manual `convert_qrc.command`
    (requires `pyrcc5`) and no doc or CI step produces it, so a clean checkout fails with
    `ModuleNotFoundError` on launch and setuptools packaging fails on the missing module.
  - Minor: the new `p2pp/paths.py::ui_path()` is referenced nowhere and duplicates what
    `p2pp/uifiles.find_ui()` already does — dead code added in the same session.

---

## Cross-cutting observations

1. **Merge hygiene**: two of twelve commits shipped unresolved conflict markers. Whatever
   merge/approval flow produced this batch did not include even a CI-level sanity check;
   consider a lint step that greps for `<<<<<<<` in tracked files.
2. **Security fixes need a threat-model pass**: #69 declared victory over issue #53 while
   the equivalent flag remained active via env var. A follow-up checklist item for any
   "remove insecure setting" PR: grep the whole repo (all spellings/env-var forms) before
   merging.
3. Several fixes (#60, #64, #67) verified genuinely good — the session's core G-code and
   config-restoration bugs are really fixed.
