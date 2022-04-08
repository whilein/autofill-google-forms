import argparse
import requests

parser = argparse.ArgumentParser(description='Фейковые ответы на гугл формы')

parser.add_argument('--names', type=str,
                    help='Локация имён')

parser.add_argument("id", type=str,
                    help='Имя формы')

parser.add_argument("-с", "--count", type=int,
                    help='Количество')

parser.add_argument("-e", "--entry", action='append', nargs=2, metavar=('id', 'value'), help='Данные формы')

args = parser.parse_args()

form = args.id

class Value:
    def get_value():
        pass

class ValueFile(Value):
    def __init__(self, file):
        self.counter = 0

        with open(file, 'r') as f:
            self.values = list(map(lambda value: value.strip(), f.readlines()))

    def __repr__(self):
        return "File{of=%s}" % self.values

    def __str__(self):
        return "File{of=%s}" % self.values

    def get_value(self):
        try:
            return self.values[self.counter]
        finally:
            self.counter += 1

class ValueString(Value):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value

    def get_value(self):
        return self.value

def wrap(raw):
    if (raw.startswith("FILE:")):
        return ValueFile(raw[5:])
    
    return ValueString(raw)

entries = {}

for entry in args.entry:
    entries[entry[0]] = wrap(entry[1])

url = "https://docs.google.com/forms/d/e/%s/formResponse" % form

for _ in range(args.count):
    data = {
        "partialResponse": "[null,null,\"0\"]",
        "pageHistory": 0,
        'draftResponse':[]
    }

    for (k, v) in entries.items():
        data["entry.%s" % k] = v.get_value()

    headers = {'Referer':'https://docs.google.com/forms/d/e/%s/viewform'% k,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}

    requests.post(url, data=data, headers=headers)