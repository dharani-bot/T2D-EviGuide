from pathlib import Path
import ast

p = Path("app.py")

if not p.exists():
    print("ERROR: app.py not found. Open the T2D-EviGuide project folder first.")
    raise SystemExit(1)

s = p.read_text(encoding="utf-8-sig")

needle = '                    if status == "VERIFIED"'

if "References Found" in s and "total_references_found" in s:
    print("Counters already exist; no change needed.")

elif needle not in s:
    print("ERROR: Target line not found. File unchanged.")

else:
    addition = '''                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "References Found",
                        verification.get("total_references_found", 0)
                    )
                    col2.metric(
                        "Verified",
                        verification.get("total_verified", 0)
                    )
                    col3.metric(
                        "Needs Review",
                        verification.get("total_unverified", 0)
                    )

'''

    updated = s.replace(needle, addition + needle, 1)

    try:
        ast.parse(updated)
    except SyntaxError as e:
        print("ERROR: Syntax check failed. File unchanged.")
        print(e)
        raise SystemExit(1)

    backup = Path("app_before_counter_edit.py")

    if not backup.exists():
        backup.write_text(s, encoding="utf-8")

    p.write_text(updated, encoding="utf-8")

    print("SUCCESS: Counters inserted.")
    print("Backup saved as:", backup)
    print("Syntax check: passed")