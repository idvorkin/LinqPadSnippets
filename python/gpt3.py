#!python3

import os
import openai
import json
from icecream import ic
import typer
import os
import openai
import sys
from rich import print


# Load your API key from an environment variable or secret management service

def setup_gpt():
    PASSWORD = "replaced_from_secret_box"
    with open(os.path.expanduser("~/gits/igor2/secretBox.json")) as json_data:
        SECRETS = json.load(json_data)
        PASSWORD = SECRETS["openai"]
    openai.api_key = PASSWORD
    return openai

gpt3 = setup_gpt()
app = typer.Typer()

@app.command()
def stdin(max_tokens:int=20):
    prompt = "".join(sys.stdin.readlines()) response_text = do_complete(prompt, max_tokens)
    print(f"[bold]{prompt}[/bold] {response_text}")


def do_complete(prompt, max_tokens):
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=max_tokens)

    #ic(response)
    #ic(response.choices[0].text)
    return response.choices[0].text

@app.command()
def complete(prompt:str, max_tokens=10):
    response_text = do_complete(prompt, max_tokens)
    print(f"[bold]{prompt}[/bold] {response_text}")




if __name__ == "__main__":
    app()
