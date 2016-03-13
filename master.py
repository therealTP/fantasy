import json
import number_fire_scraper as nf
import rotowire_scraper as rw
import bball_monster_scraper as bm
import fantasy_pros_scraper as fp
import DataSuite as ds
import PlayerSuite as ps
import linksFilesCreds as lfc
import s3
import os
import NoticeSuite as ns

# open template & convert to data_dict
with open(lfc.DAILY_JSON_TEMPLATE, encoding='utf-8') as data_file:
    data_dict = json.loads(data_file.read())

# add current date to dict via "game_date" key
data_dict["game_date"] = ds.getCurrentDate()

# get raw nf data
# raw_nf_data = nf.getRawData(lfc.NF_SCRAPE_URL, lfc.NF_CREDS)

# get final nf data
# nf_data = nf.extractProjectedStats(raw_nf_data)

# add nf data to data_dict
# ds.addProjectionDictForSource("number_fire", data_dict, nf_data)

# get raw rw data
raw_rw_data = rw.getHtmlTreeFromPage(lfc.RW_LOGIN_URL, lfc.RW_CREDS, lfc.RW_SCRAPE_URL)

# get final rw data
rw_data = rw.extractProjectedStats(raw_rw_data)

# add rw data to data_dict
ds.addProjectionDictForSource("roto_wire", data_dict, rw_data)

# get raw bm data
tree = bm.getHtmlTreeFromPage(lfc.BM_LOGIN_URL, lfc.BM_USER, lfc.BM_PW, lfc.BM_SCRAPE_URL)

# get final bm data
bm_data = bm.extractProjectedStats(tree)

# add bm data to data dict
ds.addProjectionDictForSource("basketball_monster", data_dict, bm_data)

# get raw fp data
raw_fp_data = fp.getHtmlTreeFromPage(lfc.FP_LOGIN_URL, lfc.FP_USER, lfc.FP_PW, lfc.FP_SCRAPE_URL)

# get final fp data
fp_data = fp.extractProjectedStats(raw_fp_data)

# add fp data to data_dict
ds.addProjectionDictForSource("fantasy_pros", data_dict, fp_data)

# create file name from today's date, inc. data folder
json_file = ds.getCurrentDate() + ".json"

# write final data_dict to json file w/ file name
with open(json_file, 'w') as write_json:
    json.dump(data_dict, write_json)

# put json file to s3 bucket
s3_result = s3.putObjectS3(json_file, lfc.AWS_BUCKET_NAME, lfc.PROJECTIONS_FOLDER)

# delete json_file from local storage (s3 put complete)
os.remove(json_file)

# prepare e-mail body
msg = ns.createMessage(data_dict, s3_result, ps.getQueueCount())

# send e-mail to text to my phone with msg as body
ns.sendEmail(lfc.GMAIL_UN, lfc.GMAIL_PW, lfc.MAILTO, lfc.SUBJECT, msg)
