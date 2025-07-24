import sys
import os
import json
from datetime import date, datetime

arguments = sys.argv

report = {"average": False,
          }
key_word_tuple = ("--file", "--report", "--errors", "--date")
params = {
    "--file": list(),
    "--report": list(),
    "--errors": list(),
    "--date": list(),
}

param = None
for arg in arguments[2:]:
    if arg in key_word_tuple:
        param = arg
        continue
    if param is None:
        print("Нет подходящих параметров")
        print(*key_word_tuple, sep="\n")
        break
    params[param].append(arg)
print(params)
for report_param in params["--report"]:
    report[report_param] = True

days = list()
for day in params["--date"]:
    date_prm = datetime.strptime(day, "%Y-%m-%d").date()
    days.append(date_prm)

file_list_read = params['--file'] if params['--file'] else os.listdir(os.getcwd())
#если нет параметров для файлов, осуществляется поиск всех подходящих файлов
# os.getcwd() - Return a string representing the current working directory.
data = list()
for file_name in file_list_read:
    if file_name.endswith(".log") or file_name.endswith(".json"):
        with open(file_name, 'r', encoding="UTF-8") as file:
            if file_name.endswith(".log"):
                line_numer = 0
                for line in file.readlines():
                    line_numer +=1
                    try:
                        data.append(json.loads(line))
                    except json.decoder.JSONDecodeError:
                        params["--errors"].append(f"Файл {file_name} содержит некорректные данные! В строке {line_numer}")
                        continue
                    except Exception as err:
                        print(err)
                        continue
            elif file_name.endswith(".json"):
                try:
                    data.append(json.load(file))
                except json.decoder.JSONDecodeError:
                    params["--errors"].append(f"Файл {file_name} содержит некорректные данные!")
                    continue
                except Exception as err:
                    params["--errors"].append(err)
                    continue

urls = dict()
date_cnt_field_flag = False
for line_dict in data:
    url = line_dict["url"]
    urls[url] = urls.setdefault(url, dict())
    urls[url]["total"] = urls[url].setdefault("total", 0) + 1

    timestamp = line_dict["@timestamp"]
    urls[url]["@timestamp"] = urls[url].setdefault("@timestamp", list())
    # urls[url]["@timestamp"].append(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z"))
    date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
    year, month, day = date.year, date.month, date.day
    new_day_record = datetime(year, month, day)
    urls[url]["@timestamp"].append(new_day_record)

    status = line_dict["status"]
    urls[url]["status"] = urls[url].setdefault("status", dict())
    urls[url]["status"][status] = urls[url]["status"].setdefault(status, 0) + 1

    request_method = line_dict["request_method"]
    urls[url]["request_method"] = urls[url].setdefault("request_method", dict())
    urls[url]["request_method"][request_method] = urls[url]["request_method"].setdefault(request_method, 0) + 1

    response_time = line_dict["response_time"]
    urls[url]["response_time"] = urls[url].setdefault("response_time", list())
    urls[url]["response_time"].append(response_time)


    http_user_agent = line_dict["http_user_agent"]
    urls[url]["http_user_agent"] = urls[url].setdefault("http_user_agent", dict())
    urls[url]["http_user_agent"][http_user_agent] = urls[url]["http_user_agent"].setdefault(http_user_agent, 0) + 1
    #обработка
    urls[url]["average_response_time_by_days"] = urls[url].setdefault("average_response_time_by_days", list())
    if new_day_record.date() in days:
        urls[url]["average_response_time_by_days"].append(response_time)



# date_prm.day, date_prm.month, date_prm.year

if params["--date"] and params["--report"]:
    stroke_num = 0
    first_stroke = f"№\tURL address\t\ttotal\taverage"
    print(first_stroke)
    for url, url_dict in urls.items():
        len_records = len(urls[url]['average_response_time_by_days'])
        sum_records = sum(urls[url]['average_response_time_by_days'])
        average =  sum_records / (len_records if len_records>0 else sum_records)
        stroke = f"{stroke_num}\t{url}\t\t{urls[url]['total']}\t{average}"
        stroke_num += 1
        print(stroke)





