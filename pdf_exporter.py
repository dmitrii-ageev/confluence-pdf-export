#!/usr/bin/env python3
"""
This program downloads a Confluence Space as PDF file.
You need Scroll PDF Plugin installed on your Confluence server.
https://www.k15t.com/software/scroll-pdf-exporter

User name and the password could be defined in pdf_exporter.ini or ~/.pdf_exporter.ini files.
Here is a file example:

---[ pdf_exporter.ini ]---
[Defaults]
file_name = confluence_space.pdf

[Authentication]
username = admin
password = admin

[Confluence]
server_url = https://confluence.server.com
page_id = 55903552
template_id = com.k15t.scroll.pdf.default-template-documentation
scope = descendants
--------------------------

Dmitrii Ageev <d.ageev@gmail.com>

"""

import scroll_pdf_export
import configparser
import os.path

OPTIONS={'Defaults': ['file_name'], 'Confluence': ['server_url', 'page_id', 'template_id', 'scope'], 'Authentication': ['username', 'password']}
CONFIG_FILE='pdf_exporter.ini'

# Load the configuration file
options = dict()
config = configparser.ConfigParser()
if config.read([CONFIG_FILE, os.path.expanduser('~/.' + CONFIG_FILE)]):
    for section in OPTIONS.keys():
        if config.has_section(section):
            options[section] = dict()
            for option in OPTIONS[section]:
                if config.has_option(section, option):
                    options[section][option] = config.get(section, option)
                else:
                    raise ValueError("A mandatory option (%s - %s) doesn't present in the configuration file!" % (section, option))
        else:
            raise ValueError("A mandatory section (%s) doesn't present in the configuration file!" % section)
else:
    raise ValueError("Can't find a config file")

# Download a PDF file
pdf_export = scroll_pdf_export.ScrollPDFExport(options['Confluence']['server_url'],
                                               options['Confluence']['template_id'],
                                               options['Confluence']['page_id'],
                                               {'scope': options['Confluence']['scope']},
                                               (options['Authentication']['username'], options['Authentication']['password']),
                                               False)

print('The downloaded file name is: %s' % pdf_export.download_pdf_file(options['Defaults']['file_name']))
