#!/usr/bin/env python3
from datetime import date
from datetime import datetime
from pyfiglet import Figlet
import click


@click.command()
@click.argument("dateoffset", default=date.today())
def printZachAge(dateoffset: date) -> None:
    """
    A little tool to help compute Zach's age in week for
    http://ig66.blogspot.com

    With no paramaters uses today's date.
    dateoffset takes format MM/DD/YY
    """

    isDatePassedIn = isinstance(dateoffset, str)
    if isDatePassedIn:
        dateoffset = datetime.strptime(dateoffset, "%x").date()

    figlet = Figlet(font="big")
    print(figlet.renderText("Zach Age"))

    zachBirthday = date(2010, 4, 22)
    age = dateoffset - zachBirthday
    ageInWeeks = age.days / 7

    print(f"Age in weeks:{round(ageInWeeks):d}")


if __name__ == "__main__":
    printZachAge()
