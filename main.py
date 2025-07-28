import sys
import os
import json
import tabulate
from datetime import date, datetime


key_word_tuple = ("--file", "--report", "--errors", "--date")

def main(arguments = sys.argv):
    params = {
        "--file": list(),
        "--report": list(),
        "--errors": list(),
        "--date": list(),
    }
    report = {"average": False,
              }
    param = None
    for arg in arguments[2:]:
        if arg in key_word_tuple:
            param = arg
            continue
        if param is None:
            print(*key_word_tuple, sep="\n")
            break
        params[param].append(arg)
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
            try:
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
                                params["--errors"].append(err)
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
            except FileNotFoundError:
                params["--errors"].append(f"Файл {file_name} не существует!")
                continue
            except Exception as err:
                params["--errors"].append(err)
                continue



    urls = dict()
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


        urls[url]["average_response_time_by_days"] = urls[url].setdefault("average_response_time_by_days", list())
        if new_day_record.date() in days:
            urls[url]["average_response_time_by_days"].append(response_time)
            urls[url]["total_by_day"] = urls[url].setdefault("total_by_day", 0) + 1
            urls[url][str(new_day_record.date())] = urls[url].setdefault(str(new_day_record.date()), 0) + 1

    first_tab_row = ['Number', 'URL', 'Total']
    tabulate_rows = [first_tab_row, ]
    stroke_num = 0
    title_flag = False
    for url, url_dict in urls.items():
        if params["--date"] and params["--report"]:
            len_records = len(url_dict['average_response_time_by_days'])
            sum_records = sum(url_dict['average_response_time_by_days'])
            average =  sum_records / (len_records if len_records>0 else sum_records)
            if len_records == 0:
                average = 0
            tabulate_row = [stroke_num, url, url_dict['total_by_day'], average]
            tabulate_rows.append(tabulate_row)
            if not title_flag:
                first_tab_row.append("Average by all days in \'--date\' parameter")
                title_flag = True
                for d in days:
                    day_count = url_dict.get(str(d), False)
                    if day_count:
                        tabulate_row.append(day_count)
                for d in days:
                    first_tab_row.append(str(d))
        elif params["--date"]:
            tabulate_row = [stroke_num, url, url_dict['total_by_day']]
            tabulate_rows.append(tabulate_row)
            if not title_flag:
                title_flag = True

        elif params["--report"]:
            if not title_flag:
                first_tab_row.append("Average")
                title_flag = True
            len_records = len(url_dict['response_time'])
            sum_records = sum(url_dict['response_time'])
            average =  sum_records / (len_records if len_records>0 else sum_records)
            if len_records == 0:
                average = 0
            tabulate_row = [stroke_num, url, url_dict['total'], average]
            tabulate_rows.append(tabulate_row)

        else:
            tabulate_row = [stroke_num, url, url_dict['total']]
            tabulate_rows.append(tabulate_row)
        stroke_num += 1
    if "--errors" in sys.argv:
        print(*params["--errors"], sep="\n")
    print(tabulate.tabulate(tabulate_rows))
    return (urls, params)
main()