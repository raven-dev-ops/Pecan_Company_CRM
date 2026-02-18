import json
import os
import subprocess
import sys
import tempfile


def run(cmd: list[str]) -> None:
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)


def safe_join_labels(labels: list[str]) -> str:
    return ",".join(labels)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/create_issues.py issues.json")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    labels = data.get("labels_to_create", [])
    issues = data.get("issues", [])

    try:
        subprocess.check_call(["gh", "--version"], stdout=subprocess.DEVNULL)
    except Exception:
        print("Error: GitHub CLI (gh) not found. Install it and run `gh auth login` first.")
        sys.exit(2)

    for lab in labels:
        name = lab["name"]
        color = lab.get("color", "ededed")
        desc = lab.get("description", "")
        cmd = ["gh", "label", "create", name, "--color", color, "--force"]
        if desc:
            cmd += ["--description", desc]
        run(cmd)

    for issue in issues:
        title = issue["title"].strip()
        body = issue.get("body", "").rstrip() + "\n"
        label_list = issue.get("labels", [])

        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".md") as tf:
            tf.write(body)
            body_path = tf.name

        try:
            cmd = ["gh", "issue", "create", "--title", title, "--body-file", body_path]
            if label_list:
                cmd += ["--label", safe_join_labels(label_list)]
            run(cmd)
        finally:
            try:
                os.remove(body_path)
            except OSError:
                pass

    print("\nDone. Issues created successfully.")


if __name__ == "__main__":
    main()
