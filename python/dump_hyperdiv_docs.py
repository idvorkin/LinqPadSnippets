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

app = typer.Typer(no_args_is_help=True)
console = Console()

extract_documentation_ast_grep_rule = """# A rule to find the markdown to be dumped
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

def run_ast_grep_scan():
    """
    Execute an AST-grep scan using a predefined rule.

    This function writes the AST-grep rule to a temporary file,
    runs the 'sg scan' command with the rule, and returns the
    scan results as a JSON string.

    Returns:
        str: The JSON output of the AST-grep scan.

    Raises:
        Exception: If there's an error running AST-grep.
    """
    # write the rule to a temporary file (because I can't get inline to work)
    with tempfile.NamedTemporaryFile(
        mode="w", delete=True, suffix=".yaml"
    ) as temp_file:
        temp_file_path = temp_file.name
        Path(temp_file_path).write_text(extract_documentation_ast_grep_rule)
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


def cleanup_markdown_for_output(s):
    """
    Clean up and format a string containing code or documentation.

    This function performs the following operations:
    1. Removes surrounding quotes or triple quotes if present.
    2. Strips leading and trailing empty or whitespace-only lines.
    3. Removes common indentation from all lines.

    Args:
        s (str): The input string to be cleaned up.

    Returns:
        str: The cleaned and formatted string.
    """
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


def extract_file_contents():
    """Extract hyperdiv documentation from the docs codebase - run it from hyperdiv-docs/hyperdiv_docs/pages > doc.md"""
    result = run_ast_grep_scan()
    hits = json.loads(result)
    # write to tmp.json file
    with open("tmp.json", "w") as f:
        json.dump(hits, f, indent=4)
    # convert to a list of AstGrepHit objects
    hits = [AstGrepHit(**hit) for hit in hits]
    file_content = {}
    for hit in hits:
        if hit.file not in file_content:
            file_content[hit.file] = f"# FILE: {hit.file} \n"
        file_content[hit.file]+=(cleanup_markdown_for_output(hit.metaVariables.single.MD.text)+"\n")
    return file_content

def file_ordered_by_menu():

    # Clever, call list_files, then pass that to GPT when you have a picture of the menu
    # and then ask it to sort the list for you!
    # ![](https://raw.githubusercontent.com/idvorkin/ipaste/main/20240922_165631.webp)

    file_order = """./introduction/overview.py
    ./introduction/docs_overview.py
    ./guide/getting_started.py
    ./guide/components.py
    ./guide/interactivity.py
    ./guide/component_props.py
    ./guide/layout.py
    ./guide/conditional_rendering.py
    ./guide/loops.py
    ./guide/state.py
    ./guide/modular_apps.py
    ./guide/tasks.py
    ./guide/pages_and_navigation.py
    ./guide/using_the_app_template.py
    ./guide/matplotlib_charts.py
    ./guide/static_assets.py
    ./guide/deploying.py
    ./guide/plugins.py
    ./extending_hyperdiv/overview.py
    ./extending_hyperdiv/plugins.py
    ./extending_hyperdiv/custom_assets.py
    ./extending_hyperdiv/built_in_components.py
    ./extending_hyperdiv/new_components.py
    ./reference/cli.py
    ./reference/design_tokens.py
    ./reference/prop_types.py
    ./reference/icons.py
    ./reference/components.py
    ./reference/env_variables.py"""
    # remove leading spaces
    file_order = [file.strip() for file in file_order.split("\n")]
    return file_order


@app.command()
def list_files():
    """ List all files in the documentation.
You can ask GPT to sort these based on what the menu looks like (see filer_ordered_by_menu) """
    file_content = extract_file_contents()
    # print files in order
    for file in file_content.keys():
        print(file)

@app.command()
def to_docs():
    file_content = extract_file_contents()
    file_in_order = file_ordered_by_menu()
    if len(file_content.keys()) != len(file_in_order):
        ic(len(file_content.keys()), len(file_in_order))
        missing_files = set(file_content.keys()) - set(file_in_order)
        ic(missing_files)
        print("Error: Number of files in the documentation does not match the number of files in the order list")
        return

    # print files in order
    for file in file_in_order:
        print(file_content[file])


if __name__ == "__main__":
    app()
