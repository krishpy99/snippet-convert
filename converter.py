import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET


def unzip_file(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir


def convert_sublime_to_luasnip(content):
    root = ET.fromstring(content)
    trigger = root.find('tabTrigger').text
    content = root.find('content').text
    lua_snippet = f"""
local ls = require("luasnip")
local s = ls.snippet
local t = ls.text_node

ls.add_snippets("all", {{
    s("{trigger}", {{
        t([[{content}]]),
    }}),
}})
"""
    return lua_snippet


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.sublime-snippet'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                lua_content = convert_sublime_to_luasnip(content)
                new_file_path = file_path[:-16] + '.lua'
                with open(new_file_path, 'w') as f:
                    f.write(lua_content)
                os.remove(file_path)
