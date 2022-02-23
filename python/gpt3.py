#!python3

import os
import openai
import json
from icecream import ic
import typer
import sys
from rich import print as rich_print
import rich
from loguru import logger
import re
original_print = print
is_from_console=False

text_model_best = 'text-davinci-001'
code_model_best = 'code-davinci-001'

def bold_console(s):
    if (is_from_console):
        return f"[bold]{s}[/bold]"
    else:
        return s


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
        engine=code_model_best,
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
        print(f"{bold_console(prompt)} {response_text}")
    else:
        response = openai.Completion.create(
            engine=text_model_best,
            n=responses,
            prompt=remove_trailing_spaces(prompt),
            max_tokens=tokens,
            stop=["\n"],
        )
        for c in response.choices:
            print(f"{c.text}")

@app.command()
def tldr(tokens: int = typer.Option(50), responses: int = typer.Option(1), debug:bool=False):
    prompt = "".join(sys.stdin.readlines())
    prompt_to_gpt = remove_trailing_spaces(prompt) + "\ntl;dr:"
    response = openai.Completion.create(
        engine=text_model_best,
        n=responses,
        prompt=prompt_to_gpt,
        max_tokens=tokens,
        stop=["\n\n"],
    )
    if (debug):
        ic(prompt_to_gpt)
        print (prompt_to_gpt)
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
    prompt_in = f'''I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with "Unknown".
Q: What is human life expectancy in the United States?
A: Human life expectancy in the United States is 78 years.

Q: Who was president of the United States in 1955?
A: Dwight D. Eisenhower was president of the United States in 1955.

Q: Which party did he belong to?
A: He belonged to the Republican Party.

Q: What is the square root of banana?
A: Unknown

Q: How does a telescope work?
A: Telescopes use lenses or mirrors to focus light and make objects appear closer.

Q: Where were the 1992 Olympics held?
A: The 1992 Olympics were held in Barcelona, Spain.

Q: How many squigs are in a bonk?
A: Unknown

Q:
    '''
    response = openai.Completion.create(
        temperature=0.3,
        engine=text_model_best,
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
def notes(tokens: int = typer.Option(200), debug:bool=False):
    prompt_input = "".join(sys.stdin.readlines())
    prompt = f'''What are 5 key points I should know when studying {prompt_input}?'''
    prompt_to_gpt =  remove_trailing_spaces(prompt)
    response = gpt3.Completion.create(
        engine=text_model_best,
        temperature=0.5,
        prompt=prompt_to_gpt,
        max_tokens=tokens,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0,
        stop=['"""'],
    )
    if debug:
        ic(prompt_to_gpt)
    response_text = response.choices[0].text
    print(prompt_input)
    print("eli5:"+response_text)

@app.command()
def eli5(tokens: int = typer.Option(200), debug:bool=False):
    prompt_input = "".join(sys.stdin.readlines())
    prompt = f'''Summarize this for a second-grade sudent:
{prompt_input}'''
    prompt_to_gpt =  remove_trailing_spaces(prompt)
    response = gpt3.Completion.create(
        engine=text_model_best,
        temperature=0.5,
        prompt=prompt_to_gpt,
        max_tokens=tokens,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0,
        stop=['"""'],
    )
    if debug:
        ic(prompt_to_gpt)
    response_text = response.choices[0].text
    print(prompt_input)
    print("eli5:"+response_text)

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
        engine=text_model_best,
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
        engine=text_model_best, prompt=remove_trailing_spaces(prompt), max_tokens=max_tokens
    )

    # ic(response)
    # ic(response.choices[0].text)
    return response.choices[0].text


@app.command()
def complete(prompt: str, tokens: int = typer.Option(50)):
    response_text = do_complete(prompt, tokens)
    print(f"[bold]{prompt}[/bold] {response_text}")

@app.command()
def debug():
    ic(print)
    ic(rich_print)
    ic(original_print)
    c = rich.get_console()
    ic(c.width)
    ic(is_from_console)
    print("long line -aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

def configure_width_for_rich():
    global is_from_console
    # need to think more, as CLI vs vim will be different
    c = rich.get_console()
    is_from_console = c.width != 80
    if is_from_console:
        print = rich_print
    else:
        print = original_print

@logger.catch
def app_with_loguru():
    configure_width_for_rich()
    app()

if __name__ == "__main__":

    app_with_loguru()
