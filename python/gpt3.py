#!python3

import os
import openai
import json
from icecream import ic
import typer
import sys
from rich import print
from loguru import logger
import re


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


# GPT performs poorly with trailing spaces (wow this function was writting by gpt)
def remove_trailing_spaces(str):
        return re.sub(r'\s+$', '', str)

@app.command()
def py(tokens:int=typer.Option(50)):
    prompt = "\n".join(sys.stdin.readlines())
    response = gpt3.Completion.create(engine="davinci-codex",
                                      temperature=0.5,
                                      prompt=remove_trailing_spaces(prompt),
                                      max_tokens=tokens
                                      )
    response_text = response.choices[0].text
    print(f"{prompt}\n{response_text}")

@app.command()
def stdin(tokens:int=typer.Option(50), responses:int=typer.Option(1)):
    prompt = "".join(sys.stdin.readlines())
    if responses == 1:
        response_text = do_complete(prompt, tokens)
        print(f"[bold]{prompt}[/bold] {response_text}")
    else:
        response = openai.Completion.create(engine="davinci", n=responses, prompt=remove_trailing_spaces(prompt), max_tokens=tokens, stop=["\n"])
        for c in response.choices:
            print (f"{c.text}")

        #ic(response)
        #ic(response.choices[0].text)
        return response.choices[0].text


@app.command()
def tldr(tokens:int = typer.Option(200)):
    prompt = "".join(sys.stdin.readlines())
    prompt_in = prompt+ "\ntl;dr:"
    response_text = do_complete(prompt_in, tokens)
    print(f"{prompt}\n**TL;DR:** {response_text}")

@app.command()
def eli5(tokens:int=typer.Option(200)):
    prompt_input = "".join(sys.stdin.readlines())
    prompt=f'''My second grader asked me what this passage means:
"""{prompt_input}
"""
I rephrased it for him, in plain language a second grader can understand:
      '''
    response = gpt3.Completion.create(engine="davinci",
      temperature=0.5,
      prompt=remove_trailing_spaces(prompt),
      max_tokens=tokens,
      top_p=1,
      frequency_penalty=0.2,
      presence_penalty=0,
      stop=["\"\"\""]
)
    response_text = response.choices[0].text
    print(response_text)


def do_complete(prompt, max_tokens):
    response = openai.Completion.create(engine="davinci", prompt=remove_trailing_spaces(prompt), max_tokens=max_tokens)

    #ic(response)
    #ic(response.choices[0].text)
    return response.choices[0].text

@app.command()
def complete(prompt:str, tokens:int=typer.Option(50)):
    response_text = do_complete(prompt, tokens)
    print(f"[bold]{prompt}[/bold] {response_text}")


if __name__ == "__main__":
    @logger.catch
    def app_with_loguru():
        app()
    app_with_loguru()
