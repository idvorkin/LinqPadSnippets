#!python3
from __future__ import annotations

import typer
from icecream import ic
from rich.console import Console
import subprocess
import os
import json
from pydantic import BaseModel
from typing import Optional

app = typer.Typer()
console = Console()

def run_ast_grep():
    result = subprocess.run(["sg", "scan", "--rule", os.path.expanduser("~/tmp/docpuller.yaml"), "--json"], capture_output=True, text=True)
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
    lines = s.split('\n')
    
    # Remove leading empty or whitespace-only lines
    while lines and not lines[0].strip():
        lines.pop(0)
    

    if len(lines) >= 1 and lines[0].startswith('    '):
        # Find the minimum indentation level
        min_indent = len(lines[0]) - len(lines[0].lstrip())
        
        # Remove the minimum indentation from all lines
        lines = [line[min_indent:] for line in lines]
    
    
    # Join the remaining lines back into a string
    s = '\n'.join(lines)
    



    return s

@app.command()
def to_doc():
    """Pulls documentation from the codebase"""
    ic("Pulling documentation from the codebase")
    result = run_ast_grep()
    hits = json.loads(result)
    # write to tmp.json file
    with open("tmp.json", "w") as f:
        json.dump(hits, f, indent=4)
    # convert to a list of AstGrepHit objects
    hits = [AstGrepHit(**hit) for hit in hits]
    for hit in hits:
        print(cleanup_output_string(hit.metaVariables.single.MD.text))
if __name__ == "__main__":
    app()
