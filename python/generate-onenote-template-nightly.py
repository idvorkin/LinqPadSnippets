import datetime
import os
import schedule
import time


def generate_onenote_templates():
    app = "\\gits\\onom\\OneNotePieMenu\\bin\\debug\\OneNotePieMenu"
    system_call = f"{app} template"
    print(f"Running @ {datetime.datetime.now()}: {system_call}")
    print("++")
    os.system(system_call)
    print("--")


NIGHTLY_EXECUTION_TIME = "02:00"
print(f"Generation scheduled every day @ {NIGHTLY_EXECUTION_TIME}")
schedule.every().day.at(NIGHTLY_EXECUTION_TIME).do(generate_onenote_templates)
generate_onenote_templates()
while True:
    schedule.run_pending()
    time.sleep(1)
