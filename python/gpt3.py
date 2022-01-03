#!python3

import os
import openai
import json
from icecream import ic
import typer
import sys
from rich import print as print
import rich
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
    return re.sub(r"\s+$", "", str)


@app.command()
def py(tokens: int = typer.Option(50)):
    prompt = "\n".join(sys.stdin.readlines())
    response = gpt3.Completion.create(
        engine="davinci-codex",
        temperature=0.5,
        prompt=remove_trailing_spaces(prompt),
        max_tokens=tokens,
    )
    response_text = response.choices[0].text
    print(f"{prompt}\n{response_text}")


@app.command()
def stdin(tokens: int = typer.Option(50), responses: int = typer.Option(1)):
    prompt = "".join(sys.stdin.readlines())
    if responses == 1:
        response_text = do_complete(prompt, tokens)
        print(f"[bold]{prompt}[/bold] {response_text}")
    else:
        response = openai.Completion.create(
            engine="davinci",
            n=responses,
            prompt=remove_trailing_spaces(prompt),
            max_tokens=tokens,
            stop=["\n"],
        )
        for c in response.choices:
            print(f"{c.text}")

@app.command()
def tldr(tokens: int = typer.Option(50), responses: int = typer.Option(1)):
    prompt = "".join(sys.stdin.readlines())
    prompt_in = prompt + "\ntl;dr:"
    response = openai.Completion.create(
        engine="davinci",
        n=responses,
        prompt=remove_trailing_spaces(prompt_in),
        max_tokens=tokens,
        stop=["\n"],
    )
    print(f"{prompt}")
    for c in response.choices:
        print(f"**TL;DR:** {c.text}")

@app.command()
def answer(tokens: int = typer.Option(50), responses: int = typer.Option(4)):
    prompt = "".join(sys.stdin.readlines())
    # clean input
    is_markdown = prompt.startswith("**")
    prompt = prompt.removeprefix("Q:")
    prompt = prompt.removeprefix("**Q:**")
    prompt = prompt.strip()
    prompt_in = f'''This is a conversation between a human and a brilliant AI. If a question is "normal" the AI answers it. If the question is "nonsense" the AI says "I don't understand the question"

Q: What is human life expectancy in the United States?
A: Human life expectancy in the United States is 78 years.

Q: How do you sporkle a morgle?
A: I don't understand the question

Q: Who was president of the United States before George W. Bush?
A: Bill Clinton was president of the United States before George W. Bush.

Q: How many rainbows does it take to jump from Hawaii to seventeen?
A: I don't understand the question

Q: How does an umbrella work
A: An umbrella works by using a series of spokes to keep the rain from falling on you.

Q: How many bonks are in a quoit?
A: I don't understand the question

Q: Which colorless green ideas speak furiously
A: I don't understand the question

Q: {prompt}
A:'''
    response = openai.Completion.create(
        temperature=0.3,
        engine="davinci",
        n=responses,
        prompt=remove_trailing_spaces(prompt_in),
        max_tokens=tokens,
        stop=["\n\n"],
    )
    if is_markdown:
        print(f"**Q:** {prompt}")
    else:
        print(f"Q: {prompt}")

    for c in response.choices:
        print(f"**A:**{c.text}")

@app.command()
def eli5(tokens: int = typer.Option(200)):
    prompt_input = "".join(sys.stdin.readlines())
    prompt = f'''My second grader asked me what this passage means:
"""{prompt_input}
"""
I rephrased it for him, in plain language a second grader can understand:
      '''
    response = gpt3.Completion.create(
        engine="davinci",
        temperature=0.5,
        prompt=remove_trailing_spaces(prompt),
        max_tokens=tokens,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0,
        stop=['"""'],
    )
    response_text = response.choices[0].text
    print(response_text)

@app.command()
def complex(tokens: int = typer.Option(200)):
    prompt_input = "".join(sys.stdin.readlines())
    prompt = f'''The human asks the AI to make a simple description more complicated. The AI responds by writing a verbose response full of jargon to explain a simple concept.

Human: explain how to use a drinking fountain.

AI: To activate the mechanized dihydrogen monoxide dispensary service station, use the flanges to provide a downward force to the simple circular activation console and continue to apply force until the pneumatic system begins operating as intended, which can be surmised at a time when the dihydrogen monoxide travels in a parabolic arc which at is greatest exceeds three inches from the rounded excess liquid receptacle. Once hydration is completed, cease applying force to the console and regard whether or not the dispensary has ceased expelling contents as expected.

Human: explain how to play with a dog

AI: Being a typical domesticated animal, having been genetically selected for controllability, trainability, and general anthropomorphic features and functions, the typical dog possesses highly specialized and developed feeding behavior. The typical feeding behavior involves routine sustenance intake which can be observed by monitoring changes in animal size. Routine sustenance intake involves active and passive feeding habits, and one can gauge animal health by observing the relative levels of hydration. During training, reward conditioned reinforcement is applied. This involves the practice of rewarding targeted behaviors through the application of reinforcers, with the provision that the targeted behavior is observed. Relevant to the discussion at hand is the typical active and passive behavior exhibited by a typical dog.

Human: {prompt_input}
AI:'''
    response = gpt3.Completion.create(
        engine="davinci",
        temperature=0.5,
        prompt=remove_trailing_spaces(prompt),
        max_tokens=tokens,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0,
        stop=['\n']
    )
    response_text = response.choices[0].text
    print(response_text)


def do_complete(prompt, max_tokens):
    response = openai.Completion.create(
        engine="davinci", prompt=remove_trailing_spaces(prompt), max_tokens=max_tokens
    )

    # ic(response)
    # ic(response.choices[0].text)
    return response.choices[0].text


@app.command()
def complete(prompt: str, tokens: int = typer.Option(50)):
    response_text = do_complete(prompt, tokens)
    print(f"[bold]{prompt}[/bold] {response_text}")


def configure_width_for_rich():
    # need to think more, as CLI vs vim will be different
    c = rich.get_console()
    is_from_vim = c.width == 80
    if is_from_vim:
        # Not sure how to fix, deal with later
        # vim can handle wide stuff
        # c.set_width(400)
        # c.update_dimensions(width=4000, height=c.height )
        pass

@logger.catch
def app_with_loguru():
    configure_width_for_rich()
    app()

if __name__ == "__main__":

    app_with_loguru()
