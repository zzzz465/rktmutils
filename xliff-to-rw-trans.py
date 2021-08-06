from collections import defaultdict
from dataclasses import dataclass
import os
import string
import sys
from typing import List
import xml.etree.ElementTree as etree
import shutil
import pathlib

# 폴더 쪼개는 기준 = Keyed 폴더 이외의 것은 모두 DefInjected 폴더
# 폴더의 구조 = Keyed 이외의 것은 DefInjected 내에 폴더+노드 중 폴더 를 생성
# 파일의 이름 규칙 = 출력하는 파일이 Core.xliff 라면 Core 로 생성
# 파일을 쪼개는 기준 = 폴더 당 파일 한개로 퉁치면 될 듯

@dataclass
class Data:
    defType: string
    defPath: string
    value: string

xliff_path = os.path.abspath(sys.argv[1])
filename_no_ext = pathlib.Path(xliff_path).stem
xliff_document = etree.parse(xliff_path)
base_dir_name = str(pathlib.Path(xliff_path).parent.absolute())
output_file_name = filename_no_ext + '.xml'

keyed: List[Data] = []
defInjected = defaultdict(list)

for trans_unit in xliff_document.findall(r'//{*}trans-unit'):
    resname = trans_unit.attrib['resname']
    value = trans_unit.find(r'{*}target').text

    key, defPath = resname.split('+')

    data = Data(key, defPath, value)

    if key == 'Keyed':
        keyed.append(data)
    else:
        defInjected[key].append(data)

output_dir = os.path.join(base_dir_name, 'output')
keyed_dir = os.path.join(output_dir, 'Keyed')
defInjected_dir = os.path.join(output_dir, 'DefInjected')

# clear output dir
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

# write keyed
pathlib.Path(keyed_dir).mkdir(parents=True, exist_ok=True)
keyed_file_name = filename_no_ext + '.xml'

root = etree.Element('LanguageData')
xml_document = etree.ElementTree(root)

for data in keyed:
    node = etree.SubElement(root, data.defPath)
    node.text = data.value

file_path = os.path.join(keyed_dir, output_file_name)
pathlib.Path(file_path).touch(exist_ok=True)
etree.indent(xml_document, space=' ', level=0)
xml_document.write(file_path, encoding='utf-8', xml_declaration=True)

# write DefInjected
for defType, datas in defInjected.items():
    def_dir = os.path.join(defInjected_dir, defType)
    pathlib.Path(def_dir).mkdir(parents=True, exist_ok=True)

    
    root = etree.Element('LanguageData')
    xml_document = etree.ElementTree(root)
    
    for data in datas:
        node = etree.SubElement(root, data.defPath)
        node.text = data.value

    file_path = os.path.join(def_dir, output_file_name)
    pathlib.Path(file_path).touch(exist_ok=True)
    etree.indent(xml_document, space=' ' * 4, level=0)
    xml_document.write(file_path, encoding='utf-8', xml_declaration=True)