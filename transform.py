import json

import pandas as pd

with open("./data.json") as f:
    json_data = json.load(f)["classes"]

df = pd.DataFrame(json_data)
df = df[
    ["crse_id", "enrollment_total", "instruction_mode", "strm", "subject", "meetings"]
]

df_meetings = df.explode("meetings")
df_meetings = df_meetings.join(pd.json_normalize(df_meetings["meetings"]))
df = pd.concat([df.drop(columns=["meetings"]), df_meetings])

print(df)
