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
    ic(result)
    return result.stdout

# generated via [gpt.py2json](https://tinyurl.com/23dl535z)

class AstGrepResponse(BaseModel):
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

    class MetaVariables1(BaseModel):
        class Single(BaseModel):
            string_value: str
            integer_value: int

        single: Single
        multi: dict
        transformed: dict

    text: str
    range: Range
    file: str
    lines: str
    language: str
    metaVariables: MetaVariables1
    ruleId: str
    severity: str
    note: Optional[str] = ""
    message: str


@app.command()
def to_doc():
    """Pulls documentation from the codebase"""
    ic("Pulling documentation from the codebase")
    result = run_ast_grep()
    # load the json into a JsonResponse object
    ast_grep_response = AstGrepResponse.model_validate_json(result.stdout)


    ic(ast_grep_response)

if __name__ == "__main__":
    app()
