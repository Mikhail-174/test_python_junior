import sys
import os
from main import main
import pytest

#с указанием файла, с особым отчётом, без даты
params_1 = ("python", "main.py",
          "--file", "example1.log",
          "--report", "average",
            )
#с указанием абсолютного пути файла, с особым отчётом, с датой
absoulte_path = ""
search_dir = os.getcwd()
for dirpath, dirnames, filenames in os.walk(search_dir):
    if "example1.log" in filenames:
        absolute_path = os.path.join(dirpath, "example1.log")
params_2 = ("python", "main.py",
            "--file", absolute_path,
            "--report", "average",
            "--date", "2025-06-22",
            )
#без указания файлов, с особым отчётом, с датой
params_3 = ("python", "main.py",
            "--file",
            "--report", "average",
            "--date", "2025-06-22",
            )

#без указания файлов, без особого отчёта, с датой
params_4 = ("python", "main.py",
            "--file",
            "--date", "2025-06-22",
            )

#без указания файлов, с особым отчётом, без даты
params_5 = ("python", "main.py",
            "--file",
            "--report", "average",
            )

#без указания файлов, без особого отчёта, без даты
params_6 = ("python", "main.py",
            "--file",
            )

@pytest.mark.parametrize("params", [params_1, params_2, params_3, params_4, params_5])
def test_parse_arguments(params):
    urls = main(params)[0]
    assert len(urls.keys()) == 5


params_7 = ("python", "main.py",
            "--file", "русско_китайский_словарь.pdf", "русско_китайский_словарь.log",
            )
params_8 = ("python", "main.py",
            "--file", "example1.log", "example2.log", "fuckyou.log", "fuckyou2.log",
            )
@pytest.mark.parametrize("params", [params_7, params_8])
def test_bad_filename(params):
    urls, arguments_dict = main(params)
    assert len(arguments_dict["--errors"]) > 5

