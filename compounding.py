import requests
import json
import time
from tabulate import tabulate

#lbank stuff
lbank_xcc_url = requests.get("https://api.lbkex.com/v1/ticker.do?symbol=xcc_usdt")
lbank_xcc_dict = json.loads(lbank_xcc_url.text)
print(lbank_xcc_dict["ticker"]["latest"])
xcc_price = lbank_xcc_dict["ticker"]["latest"]

lbank_xch_url = requests.get("https://api.lbkex.com/v1/ticker.do?symbol=xch_usdt")
lbank_xch_dict = json.loads(lbank_xch_url.text)
print(lbank_xch_dict["ticker"]["latest"])
xch_price = lbank_xch_dict["ticker"]["latest"]

#foxypool stuff

#xcc
foxypool_xcc_stats = requests.get("https://api2.foxypool.io/api/v2/chives-og/rewards")
foxypool_xcc_stats_dict = json.loads(foxypool_xcc_stats.text)
xcc_profit_per_tib_per_month = (foxypool_xcc_stats_dict["dailyRewardPerPiB"] / 1024) * 30
#xch
foxypool_xch_stats = requests.get("https://api2.foxypool.io/api/v2/chia-og/rewards")
foxypool_xch_stats_dict = json.loads(foxypool_xch_stats.text)
xch_profit_per_tib_per_month = (foxypool_xch_stats_dict["dailyRewardPerPiB"] / 1024) * 30

#variables
tib_price = float(23)
xch_tib = float(371)
xcc_tib = float(635)
watt_tib = 0.772
usd_watt_tib_month = float((watt_tib/1000) * 0.1 * 24 * 30)

#1 = 100% chia, 0 = 100% chives
chia_chives_split = 0.00

stats_dict = {"XCC Price": ["$" + str(xcc_price)], "XCH Price": ["$" + str(xch_price)], "Chives USD/TiB/Month": ["$" + str(xcc_profit_per_tib_per_month * xcc_price)], "Chia USD/TiB/Month": ["$" + str(xch_profit_per_tib_per_month * xch_price)], "Per TiB Cost": ["$" + str(tib_price)], "Chia/Chives Split": ["$" + str(chia_chives_split)]}

compound_dict = {"Month": list(range(0,49)), "Chia TB": [], "Chives TB": [], "Chia TB Increase": [], "Chives TB Increase": [], "XCH Rev": [], "XCC Rev": [], "Chia USD Rev": [], "Chives USD Rev": [], "Total USD Rev": [], "Total USD Profit": [], "Estimated Watts": [], "Electric Costs": []}

for i in compound_dict["Month"]:
    if i == 0:
        compound_dict["Chia TB"].append(xch_tib)
        compound_dict["Chives TB"].append(xcc_tib)
        compound_dict["XCH Rev"].append(xch_profit_per_tib_per_month * xch_tib)
        compound_dict["XCC Rev"].append(xcc_profit_per_tib_per_month * xcc_tib)
        compound_dict["Chia USD Rev"].append(compound_dict["XCH Rev"][i] * xch_price)
        compound_dict["Chives USD Rev"].append(compound_dict["XCC Rev"][i] * xcc_price)
        compound_dict["Total USD Rev"].append(compound_dict["Chia USD Rev"][i] + compound_dict["Chives USD Rev"][i])
        compound_dict["Estimated Watts"].append((xch_tib + xcc_tib) * watt_tib)
        compound_dict["Electric Costs"].append(compound_dict["Estimated Watts"][i] * usd_watt_tib_month)
        compound_dict["Total USD Profit"].append(compound_dict["Total USD Rev"][i] - compound_dict["Electric Costs"][i])
        compound_dict["Chia TB Increase"].append(compound_dict["Total USD Profit"][i] * chia_chives_split / tib_price)
        compound_dict["Chives TB Increase"].append(compound_dict["Total USD Profit"][i] * (1 - chia_chives_split) / tib_price)
    else:
        compound_dict["Chia TB"].append(compound_dict["Chia TB"][i-1] + compound_dict["Chia TB Increase"][i-1])
        compound_dict["Chives TB"].append(compound_dict["Chives TB"][i-1] + compound_dict["Chives TB Increase"][i-1])
        compound_dict["XCH Rev"].append(xch_profit_per_tib_per_month * compound_dict["Chia TB"][i])
        compound_dict["XCC Rev"].append(xcc_profit_per_tib_per_month * compound_dict["Chives TB"][i])
        compound_dict["Chia USD Rev"].append(compound_dict["XCH Rev"][i] * xch_price)
        compound_dict["Chives USD Rev"].append(compound_dict["XCC Rev"][i] * xcc_price)
        compound_dict["Total USD Rev"].append(compound_dict["Chia USD Rev"][i] + compound_dict["Chives USD Rev"][i])
        compound_dict["Estimated Watts"].append((compound_dict["Chia TB"][i] + compound_dict["Chives TB"][i]) * watt_tib)
        compound_dict["Electric Costs"].append(compound_dict["Estimated Watts"][i] * usd_watt_tib_month)
        compound_dict["Total USD Profit"].append(compound_dict["Total USD Rev"][i] - compound_dict["Electric Costs"][i])
        compound_dict["Chia TB Increase"].append(compound_dict["Total USD Profit"][i] * chia_chives_split / tib_price)
        compound_dict["Chives TB Increase"].append(compound_dict["Total USD Profit"][i] * (1 - chia_chives_split) / tib_price)


print(tabulate(stats_dict, headers="keys", floatfmt=".4f", tablefmt="fancy_grid"))
print(tabulate(compound_dict, headers="keys", floatfmt=".2f", tablefmt="fancy_grid"))

text_tables = tabulate(stats_dict, headers="keys", floatfmt=".4f", tablefmt="grid") + "\n" + tabulate(compound_dict, headers="keys", floatfmt=".2f", tablefmt="grid")

f = open("test.txt","w")
f.write(text_tables)
f.close()


html_text = '''
<!DOCTYPE html>
<html>
    <head>
	    <title>CCCT</title>
	    <meta charset="utf-8">
	    <style>
table {
  border-collapse: collapse;
  width: 100%;
}

th, td {
  text-align: left;
  padding: 8px;
}

tr:nth-child(even){background-color: #f2f2f2}

th {
  background-color: #04AA6D;
  color: white;
}
</style>
    </head>
    <body>
'''
html_text = html_text + tabulate(stats_dict, headers="keys", floatfmt=".4f", tablefmt="html") + "<br /><br />" + tabulate(compound_dict, headers="keys", floatfmt=".2f", tablefmt="html")
html_text = html_text + "</body></html>"
file = open("test.html","w")
file.write(html_text)
file.close()
