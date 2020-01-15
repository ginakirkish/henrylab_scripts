import os
import json
import csv


writer = open("{}".format("/home/sf522915/Documents/swipes4science_first_output.csv"), "w")
spreadsheet = csv.DictWriter(writer, fieldnames=["msid", "mse", "T1", "response", "PASS_FAIL"])
spreadsheet.writeheader()
towrite = {}
pf = ""
with open('/data/henry6/gina/scripts/swipes4science/first.json', 'r') as myfile:
    data=myfile.read()
    obj = json.loads(data)
    for line in obj:
        print(line)
        out = obj[line]
        ave_vote = out['response']
        t1 = out["sample"]
        msid = t1.split("-")[0]
        mse = t1.split('-')[1]
        print(msid, mse, ave_vote, t1 )

        if ave_vote < 0.5:
            pf = "fail"
        else:
            pf = "pass"

        towrite["msid"] = msid
        towrite["mse"] = mse
        towrite["T1"] = t1
        towrite["response"] = ave_vote
        towrite["PASS_FAIL"] = pf

        spreadsheet.writerow(towrite)
    writer.close()