#!/usr/bin/env python3

import io
import os
import re
import sys
import zipfile

from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


def fix_zip_filename(name):
    try:
        raw_name = name.encode('cp437')
    except UnicodeEncodeError:
        raw_name = name.encode()

    return raw_name.decode('utf-8', errors="replace")


def process_pdf(fin):
    with io.BytesIO() as fout:
        extract_text_to_fp(fin, fout, output_type="html", layoutmode="loose", laparams=LAParams(), strip_control=True)
        soup = BeautifulSoup(fout.getvalue(), "lxml")

    for item in soup(lambda e: re.search(r"position\s*:\s*absolute", e.get("style", "")) is not None):
        item["style"] = ""

    return soup


def process_txt(fin):
    soup = BeautifulSoup("<body></body>", "lxml")

    for line in fin:
        p_tag = soup.new_tag('p')
        p_tag.string = line.decode(errors="replace").strip()
        soup.body.append(p_tag)

    return soup


def process_zip(path):
    app_name = re.sub(r'(?:\.html|\.txt)?\.zip$', '', os.path.basename(path))
    # workaround: some policies are not naming correctly
    app_name = app_name.replace('_', '.')

    with zipfile.ZipFile(path) as myzip:
        html_files = dict()
        shared_prefix = None

        for info in myzip.infolist():
            fixed_name = fix_zip_filename(info.filename)
            file_ext = os.path.splitext(fixed_name)[-1].lower()

            # skip directories and files created by macOS
            path_components = tuple(os.path.normpath(fixed_name).split(os.sep))
            if fixed_name.endswith('/') or any(p.startswith('.') or p == "__MACOSX" for p in path_components):
                continue

            if file_ext not in ['.html', '.txt', '.pdf']:
                continue

            shared_prefix = os.path.commonprefix([shared_prefix or path_components[:-1], path_components[:-1]])

            with myzip.open(info) as fin:
                if file_ext == '.html':
                    html_files[path_components] = BeautifulSoup(fin, "lxml")
                elif file_ext == '.pdf':
                    html_files[path_components] = process_pdf(fin)
                else:
                    html_files[path_components] = process_txt(fin)

    # strip common directories in the zip file
    html_files = {k[len(shared_prefix):]: v for k, v in html_files.items()}

    # find top-level HTMLs and concatenate to one file
    single_soup = None

    for path_components, soup in html_files.items():
        if len(path_components) > 1:
            continue

        while True:
            iframe_list = soup("iframe", src=True)
            if not iframe_list:
                break

            for iframe in iframe_list:
                iframe_src = iframe["src"]

                if iframe_src.startswith("./"):
                    relpath = tuple(os.path.normpath(iframe_src).split(os.sep))
                    nest_soup = html_files.get(relpath, BeautifulSoup())

                    replaced_tag = soup.new_tag("div")
                    if nest_soup.body is not None:
                        for children in nest_soup.body(recursive=False):
                            replaced_tag.append(children)

                    iframe.replace_with(replaced_tag)
                else:
                    iframe.extract()

        # skipped by Policheck's preprocessor
        for item in soup(["script", "style", "head", "nav", "header", "footer", "aside"]):
            item.extract()

        # other tags not likely useful
        for item in soup(["button", "select", "form", "iframe", "img", "svg"]):
            item.extract()

        for item in soup(lambda e: re.search(r"display\s*:\s*none", e.get("style", "")) is not None):
            item.extract()

        if single_soup is None:
            single_soup = soup
        else:
            single_soup.body.append(single_soup.new_tag('br'))
            for elem in soup.body(recursive=False):
                single_soup.body.append(elem)

    return app_name, str(single_soup)


def main():
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".zip"):
                fullpath = os.path.join(root, filename)
                app_name, html = process_zip(fullpath)

                with open(os.path.join(output_dir, app_name + ".html"), "w") as fout:
                    fout.write(html)


if __name__ == "__main__":
    main()
