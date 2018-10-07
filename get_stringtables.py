arma3pbos = [
    "Addons/3den_language",
    "Addons/language_f",
    "Addons/language_f_beta",
    "Addons/language_f_bootcamp",
    "Addons/language_f_epa",
    "Addons/language_f_epb",
    "Addons/language_f_epc",
    "Addons/language_f_exp_a",
    "Addons/language_f_exp_b",
    "Addons/language_f_gamma",
    "Addons/languagemissions_f",
    "Addons/languagemissions_f_beta",
    "Addons/languagemissions_f_bootcamp",
    "Addons/languagemissions_f_epa",
    "Addons/languagemissions_f_epb",
    "Addons/languagemissions_f_epc",
    "Addons/languagemissions_f_exp_a",
    "Addons/languagemissions_f_gamma",
    "Argo/Addons/language_f_argo",
    "Argo/Addons/language_f_patrol",
    "Argo/Addons/languagemissions_f_patrol",
    "Curator/Addons/language_f_curator",
    "Expansion/Addons/language_f_exp",
    "Expansion/Addons/languagemissions_f_exp",
    "Heli/Addons/language_f_heli",
    "Heli/Addons/languagemissions_f_heli",
    "Jets/Addons/language_f_destroyer",
    "Jets/Addons/language_f_jets",
    "Jets/Addons/language_f_sams",
    "Jets/Addons/languagemissions_f_jets",
    "Kart/Addons/language_f_kart",
    "Kart/Addons/languagemissions_f_kart",
    "Mark/Addons/language_f_mark",
    "Mark/Addons/language_f_mp_mark",
    "Mark/Addons/languagemissions_f_mark",
    "Mark/Addons/languagemissions_f_mp_mark",
    "Orange/Addons/language_f_orange",
    "Orange/Addons/languagemissions_f_orange",
    "Tacops/Addons/language_f_tacops",
    "Tacops/Addons/languagemissions_f_tacops",
    "Tank/Addons/language_f_tank",
    "Tank/Addons/languagemissions_f_tank"
]

import sys
import os.path
import tempfile
import xml.etree.ElementTree
import json

TOOL = "mikero\\ExtractPbo.exe"
COMMAND = f"{TOOL} -P"

keys = 0

if not os.path.isfile(TOOL):
    print(f"{TOOL} is required")

try:
    arma3path = sys.argv[1]
except IndexError:
    print("Arma 3 Path is required as an argument")
    sys.exit(1)

sourcePBOs = []

for pbo in arma3pbos:
    if os.path.isfile(os.path.join(arma3path, pbo+".pbo")):
        sourcePBOs.append([pbo, os.path.join(arma3path, pbo+".pbo")])
    elif os.path.isfile(os.path.join(arma3path, pbo+".ebo")):
        print(f"{pbo} is an epo, and can not be unpacked.")
    else:
        print(f"{pbo} was not found")

for pbo, source in sourcePBOs:
    dest = os.path.join(tempfile.gettempdir(),"a3stringtables",pbo.replace("/","_"))
    cmd = f"{COMMAND} \"{source}\" \"{dest}\""
    print(cmd)
    os.system(cmd)

strings = {}

def find_rec(node, element):
    def _find_rec(node, element, result):
        for el in node.getchildren():
            _find_rec(el, element, result)
        if node.tag == element:
            result.append(node)
    res = list()
    _find_rec(node, element, res)
    return res

for root, dirs, files in os.walk(os.path.join(tempfile.gettempdir(),"a3stringtables")):
    path = root.split(os.sep)
    for file in files:
        if file == "stringtable.xml":
            print(os.path.join("\\".join(path),file))
            e = xml.etree.ElementTree.parse(os.path.join("\\".join(path),file)).getroot()
            for key in find_rec(e, 'Key'):
                keys += 1
                languages = {}
                for lang in list(key):
                    languages[lang.tag] = lang.text
                strings[key.attrib['ID']] = languages

with open('docs/stringtable.json', 'w') as f:
    f.write(json.dumps(strings))
print(f"{keys} keys were written to stringtable.json")
