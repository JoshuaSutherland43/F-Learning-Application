import subprocess
import tempfile
import os
import time
import uuid
import re

TIMEOUT_SECONDS = 12


def run_fsharp(code: str, stdin_text: str = ""):
    """Run an F# script via `dotnet fsi` and capture stdout/stderr with a timeout.
    Returns dict: stdout, stderr, success, timed_out, duration_ms
    """
    tmp_dir = tempfile.gettempdir()
    fname = os.path.join(tmp_dir, f"fsprep_{uuid.uuid4().hex}.fsx")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(code)

    start = time.time()
    timed_out = False
    stdout = ""
    stderr = ""
    success = False
    try:
        proc = subprocess.run(
            ["dotnet", "fsi", "--use:" + fname] if False else ["dotnet", "fsi", fname],
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        success = proc.returncode == 0 and not _looks_like_error(stderr)
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = (e.stdout or "") if isinstance(e.stdout, str) else ""
        stderr = "Execution timed out after {}s. Check for infinite loops or infinite recursion (e.g. missing a base case).".format(
            TIMEOUT_SECONDS
        )
        success = False
    except FileNotFoundError:
        stderr = "dotnet SDK / F# Interactive (fsi) was not found on this machine. Cannot execute F# code."
        success = False
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass

    duration_ms = int((time.time() - start) * 1000)
    return {
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
        "success": success,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
    }


def _looks_like_error(stderr: str) -> bool:
    if not stderr:
        return False
    markers = ["error FS", "Unhandled exception", "error:", "Exception of type"]
    return any(m in stderr for m in markers)


def run_with_test_cases(user_code: str, harness: str):
    """Run user_code followed by a harness snippet that exercises it and prints
    results in a fixed, parseable format (one line per test: 'PASS' or 'FAIL:<detail>').
    Returns the raw run_fsharp result; caller inspects stdout lines.
    """
    full = user_code.rstrip() + "\n\n" + harness
    return run_fsharp(full)


def grade_code_write(meta: dict, user_code: str):
    """Build and run the grading script for a code_write question.

    If meta['reference_solution'] is present, it is wrapped in its own F# module
    (`module RefImpl = ...`) so its internal helper names can NEVER collide with
    whatever the student happens to name their own helpers -- the harness's calls
    to `referenceXxx` are automatically rewritten to `RefImpl.referenceXxx`.

    If meta['reference_solution'] is None (used whenever the starter code already
    declares a discriminated union / record type, since F# types are nominal and
    a second, separately-declared copy of the same type name is either a compile
    error or an incompatible type), the harness is expected to compare the
    student's functions against literal expected values already baked into the
    harness text, and only the student's code + harness are run.

    Returns (run_result, passed_count, total_count).
    """
    reference_solution = meta.get("reference_solution")
    harness = meta["harness"]

    if reference_solution:
        indented = "\n".join(
            ("    " + line if line.strip() else "") for line in reference_solution.split("\n")
        )
        wrapped_ref = "module RefImpl =\n" + indented
        qualified_harness = re.sub(r"\breference([A-Z]\w*)", r"RefImpl.reference\1", harness)
        script = wrapped_ref + "\n\n" + user_code.rstrip() + "\n\n" + qualified_harness
    else:
        script = user_code.rstrip() + "\n\n" + harness

    result = run_fsharp(script)
    lines = result["stdout"].splitlines()
    pass_lines = [l for l in lines if l.startswith("PASS")]
    fail_lines = [l for l in lines if l.startswith("FAIL")]
    total = len(pass_lines) + len(fail_lines)
    passed = len(pass_lines)
    return result, passed, total
