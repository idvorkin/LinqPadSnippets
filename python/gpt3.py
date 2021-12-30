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
def stdin(max_tokens:int=50):
    prompt = "".join(sys.stdin.readlines())
    response_text = do_complete(prompt, max_tokens)
    print(f"[bold]{prompt}[/bold] {response_text}")

@app.command()
def tldr(max_tokens:int=100):
    prompt = "".join(sys.stdin.readlines())
    prompt_in = prompt+ "\ntl;dr:"
    response_text = do_complete(prompt_in, max_tokens)
    print(f"{prompt}\n**TL;DR:** {response_text}")

@app.command()
def eli5(max_tokens:int=50):
    prompt_input = "".join(sys.stdin.readlines())
    prompt=f'''My second grader asked me what this passage means:
"""{prompt_input}
"""
I rephrased it for him, in plain language a second grader can understand:
      '''
    response = gpt3.Completion.create(engine="davinci",
      temperature=0.5,
      prompt=prompt,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0.2,
      presence_penalty=0,
      stop=["\"\"\""]
)
    response_text = response.choices[0].text
    print(response_text)


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
