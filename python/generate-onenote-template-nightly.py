import os
import schedule


def generateOneNoteTemplates():
    app = '\\gits\\onom\\OneNotePieMenu\\bin\\debug\\OneNotePieMenu'
    os.system(f'{app} template')


nightlyExecutionTime = "2:00"
print(f"Generation scheduled every day @ {nightlyExecutionTime}")
schedule.every().day.at(nightlyExecutionTime).do(generateOneNoteTemplates)
generateOneNoteTemplates()
while True:
    schedule.run_pending()
