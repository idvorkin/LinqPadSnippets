#!python3
from __future__ import annotations

import typer
from icecream import ic
from rich.console import Console
import subprocess
import json
from pydantic import BaseModel
from typing import Optional
import tempfile
from pathlib import Path

app = typer.Typer()
console = Console()


ast_grep_rule = """# A rule to find the markdown to be dumped
# https://ast-grep.github.io/guide/rule-config.html#rule
id: main
language: python
rule:
  any:
    - pattern: hd.markdown($MD)
    - pattern: p.title($MD)
    - pattern: p.header($MD)
    - pattern: docs_markdown($MD)
    - pattern: code_example($MD, B)
"""


def run_ast_grep():
    # write the rule to a temporary file (because I can't get inline to work)
    with tempfile.NamedTemporaryFile(
        mode="w", delete=True, suffix=".yaml"
    ) as temp_file:
        temp_file_path = temp_file.name
        Path(temp_file_path).write_text(ast_grep_rule)
        result = subprocess.run(
            ["sg", "scan", "--rule", temp_file_path, "--json"],
            capture_output=True,
            text=True,
        )
        if result.stderr:
            print(result.stderr)
            raise Exception("Error running ast-grep")
        return result.stdout


# generated via [gpt.py2json](https://tinyurl.com/23dl535z)
class AstGrepHit(BaseModel):
    class Range(BaseModel):
        class ByteOffset(BaseModel):
            start: int
            end: int

        class Position(BaseModel):
            line: int
            column: int

        byteOffset: ByteOffset
        start: Position
        end: Position

    class MetaVariables(BaseModel):
        class Single(BaseModel):
            class MDType(BaseModel):
                text: str

            MD: MDType
            string_value: str | None = None
            integer_value: int | None = None

        single: Single
        multi: dict
        transformed: dict

    text: str
    range: Range
    file: str
    lines: str
    language: str
    metaVariables: MetaVariables
    ruleId: str
    severity: str
    note: Optional[str] = ""
    message: str


def cleanup_output_string(s):
    # if string is wrapped with " , ' or """, remove it from the front and back
    if s.startswith('"""') and s.endswith('"""'):
        s = s[3:-3]
    elif s.startswith("'") and s.endswith("'"):
        s = s[1:-1]
    elif s.startswith('"') and s.endswith('"'):
        s = s[1:-1]

    # Remove leading and trailing empty or whitespace-only lines
    lines = s.split("\n")

    # Remove leading empty or whitespace-only lines
    while lines and not lines[0].strip():
        lines.pop(0)

    if len(lines) >= 1 and lines[0].startswith("    "):
        # Find the minimum indentation level
        min_indent = len(lines[0]) - len(lines[0].lstrip())

        # Remove the minimum indentation from all lines
        lines = [line[min_indent:] for line in lines]

    # Join the remaining lines back into a string
    s = "\n".join(lines)

    return s


@app.command()
def to_doc():
    """Extract hyperdiv documentation from the docs codebase - run it from hyperdiv-docs/hyperdiv_docs/pages > doc.md"""
    ic("Pulling documentation from the codebase")
    result = run_ast_grep()
    hits = json.loads(result)
    # write to tmp.json file
    with open("tmp.json", "w") as f:
        json.dump(hits, f, indent=4)
    # convert to a list of AstGrepHit objects
    hits = [AstGrepHit(**hit) for hit in hits]
    last_file = None
    for hit in hits:
        file_suffix = ""
        if hit.file != last_file:
            last_file = hit.file
            file_suffix = f"({last_file})"
        print(cleanup_output_string(hit.metaVariables.single.MD.text) + file_suffix)


if __name__ == "__main__":
    app()
