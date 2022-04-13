import argparse
import requests
import json

parser = argparse.ArgumentParser(description='Автоматические ответы на гугл формы')

parser.add_argument("id", type=str,
                    help='Имя формы')
                    
parser.add_argument("--import-file", type=str, help='Импорт значений из json файла')

parser.add_argument("-с", "--count", type=int,
                    help='Количество')

parser.add_argument("-s", "--seed", type=int,
                    help='Сид')

parser.add_argument("-e", "--entry", action='append', nargs=2, metavar=('id', 'value'), help='Данные формы')

args = parser.parse_args()

seed = args.seed or 0
form = args.id

class Value:
    def get_value():
        pass

class ValueFile(Value):
    def __init__(self, file, save = False):
        self.counter = 0
        self.file = file
        self.save = save

        with open(file, 'r') as f:
            self.values = list(map(lambda value: value.strip(), f.readlines()))

    def __repr__(self):
        return "File{from=%s}" % self.file

    def __str__(self):
        return "File{from=%s}" % self.file

    def get_value(self):
        try:
            return self.values.pop(0)
        finally:
            if self.save:
                with open(self.file, 'w') as f:
                    for value in self.values:
                        f.write(value)
                        f.write("\r\n")
                    f.flush()

class ValueString(Value):
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return "str(" + str(self.values) + ")"

    def __str__(self):
        return "str(" + str(self.values) + ")"

    def get_value(self):
        return self.values

class Entries:
    def __init__(self, entries):
        self.entries = entries

    def __repr__(self):
        return str(self.entries)

    def __str__(self):
        return str(self.entries)
    
    def wrap(raw):
        if type(raw) is str:
            if raw.startswith("FILE:"):
                return ValueFile(raw[5:])
            elif raw.startsWith("POP:"):
                return ValueFile(raw[4:], save=True)

            raw = [raw]
        
        return ValueString(raw)

    def add_entry(self, key, value):
        value = Entries.wrap(value)

        if key in self.entries.keys():
            self.entries[key].values.append(value)
        else:
            self.entries[key] = value
    
class Page:
    def __init__(self, id: int, entries: Entries):
        self.id = id
        self.entries = entries

    def __repr__(self):
        return "%s: %s" % (self.id, self.entries)

    def __str__(self):
        return "%s: %s" % (self.id, self.entries)

import_file = args.import_file

pages = {}

if import_file:
    pages = list()

    with open(import_file, "r") as file:
        for (id, entries) in json.load(file).items():
            pages.append(Page(int(id), Entries({ key:Entries.wrap(value) for (key, value) in entries.items() })))
else:
    entries = Entries({})

    for entry in args.entry:
        entries.add_entry(entry[0], entry[1])
    
    pages = list((Page(0, entries), ))

url = "https://docs.google.com/forms/d/e/%s/formResponse" % form

for i in range(args.count or 1):
    ids = ",".join([str(page.id) for page in pages])

    if len(pages) > 1:
        previousPages = [[None, int(id), entry.get_value(), 0] for page in pages[0:-1] for (id, entry) in page.entries.entries.items()]
    else:
        previousPages = None

    partialResponse = [
        previousPages,
        None,
        str(seed)
    ]

    data = {
        "partialResponse": json.dumps(partialResponse),
        "pageHistory": ids,
        'draftResponse': [],
        'fbzx': seed
    }

    for (k, v) in pages[-1].entries.entries.items():
        data["entry.%s" % k] = v.get_value()

    headers = {
        'Referer':'https://docs.google.com/forms/d/e/%s/viewform' % form,
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"
    }
    
    resp = requests.post(url, data=data, headers=headers)
    print("Request %s sent.." % i)
    with open('%s_%s.html' % (form, i), 'w', encoding='UTF-8') as f:
        f.write(resp.text)
        f.flush()