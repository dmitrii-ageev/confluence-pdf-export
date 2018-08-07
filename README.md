# scroll-pdf-export

 **scroll_pdf_export.py** Python module for asynchronous export Atlassian Confluence Space or Page with Scroll PDF Export plugin.
 https://www.k15t.com/software/scroll-pdf-exporter

 Class constructor expects to get server_url, template_id, and page_id. These parameters are mandatory!
 Optional parameters are: options and auth.

**Example:**
```
pdf_export = ScrollPDFExport('http://my.confluence.server', 'Documents', '1234134', {'scope': 'current'}, ('admin', 'mypassword'), False)
pdf_export.download_pdf_file('my_file_name.pdf')
```

## Supported options

     scope          : "current" or "descendants"
     locale         : A valid  BCP 47  language tag, e.g. 'en-US' or 'de'.
     versionId      : The ID of the version of the content to be exported (default value: currently published version).
     variantId      : The ID of the variant of the content to be exported (default value: 'all').
     languageKey    : The language key of the translation to be exported (default value: the space's default language).

## Changelog

    v1.0.1 - 2018-08-07
        * Initial version

## TODO

    * Add synchronous export support
    * Add a progress bar

## Author

 Dmitrii Ageev <d.ageev@gmail.com>

 License to use, modify, and distribute under the GPLv2
 https://www.gnu.org/licenses/gpl-2.0.txt
