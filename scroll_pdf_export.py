"""
 scroll_pdf_export.py

 Python module for asynchronous export Atlassian Confluence Space or Page with Scroll PDF Export plugin.
 https://www.k15t.com/software/scroll-pdf-exporter

 Class constructor expects to get server_url, template_id, and page_id. These parameters are mandatory!
 Optional parameters are: options and auth

 Example:
    pdf_export = ScrollPDFExport('http://my.confluence.server', 'Documents', '1234134', {'scope': 'current'}, ('admin', 'mypassword'), False)
    pdf_export.download_pdf_file()

 Supported options:
     scope          : "current" or "descendants"
     locale         : A valid  BCP 47  language tag, e.g. 'en-US' or 'de'.
     versionId      : The ID of the version of the content to be exported (default value: currently published version).
     variantId      : The ID of the variant of the content to be exported (default value: 'all').
     languageKey    : The language key of the translation to be exported (default value: the space's default language).

 Changelog:
    v1.0.1 - 2018-08-07
        * Initial version

 TODO:
    * Add synchronous export support
    * Add a progress bar

 Dmitrii Ageev <d.ageev@gmail.com>

 License to use, modify, and distribute under the GPLv2
 https://www.gnu.org/licenses/gpl-2.0.txt

"""

import json
import time
import os.path
import urllib
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning



class ScrollPDFExport():
    # Constants
    DEBUG=False
    OPTIONS={'scope', 'locale', 'versionId', 'variantId', 'languageKey'}
    SCOPE={'current', 'descendants'}
    BASE_URI="plugins/servlet/scroll-pdf/api/public/1"

    # Variables
    server_url = None
    template_id = None
    page_id = None
    options = None
    url = None
    authentication = None
    check_certificate = None
    job_id = None
    job_status = None

    # Internal method for displaying debug messages
    def __debug(self, *message):
        if self.DEBUG:
            if type(message[0]) is int and len(message) > 1:
                print("DEBUG: " + ">" * message[0], '%s ' * (len(message)-1) % message[1::])
            else:
                print("DEBUG: " + ">", '%s ' * len(message) % message)


    # Initialize self. See example in the description.
    def __init__(self,
                 server_url,
                 template_id,
                 page_id,
                 options={'scope': 'descendants'},
                 authentication=None,
                 check_certificate=True):

        # Initialise class attributes
        self.server_url = server_url
        self.template_id = template_id
        self.page_id = page_id
        self.options = options

        # TODO Add synchronous export support
        # Synchronous URL
        #self.synchronous_url = "%s/%s/export-sync?templateId=%s&pageId=%s" % ( self.server_url, self.BASE_URI, self.template_id, self.page_id )
        #for option, value in options.items():
        #    if option in self.OPTIONS:
        #        if option != 'scope' or (option == 'scope' and value in self.SCOPE):
        #            self.synchronous_url += "&%s=%s" % (option,value)

        # Asyncronous URL
        self.url = "%s/%s/exports" % ( self.server_url, self.BASE_URI )
        self.authentication = authentication
        self.check_certificate = check_certificate
        self.job_status = dict()

        # Disable urlllib3 "Insecure Request Warnings"
        if not self.check_certificate:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Initiates an export job
    def start_export_job(self):
        body = dict()
        body['pageId'] = self.page_id
        body['scope'] = self.options['scope']
        body['templateId'] = self.template_id

        response = requests.post(self.url, data=json.dumps(body, indent=4), verify=self.check_certificate, auth=self.authentication, headers={'content-type': 'application/json'})
        if response.status_code == requests.codes.ok:

            # Get a job id from a server response
            content = response.json()
            if 'jobId' in content:
                self.job_id = content['jobId']
                return self.job_id
            else:
                raise ValueError('There is no job id in the server response!\n%s' % json.dumps(content, indent=4))
        else:
            raise ValueError('Got error code %s from %s.' % (response.status_code, self.server_url))

    # Returns the status of the export job
    def __get_job_status(self):
        # Start export job if job id isn't set
        if not self.job_id:
            self.start_export_job()

        # Prepare URL
        url = "%s/%s/exports/%s/status" % (self.server_url, self.BASE_URI, self.job_id)

        response = requests.get(url, verify=self.check_certificate, auth=self.authentication)

        if response.status_code == requests.codes.ok:
            # Get a job id from a server response
            self.job_status = response.json()
            if 'status' in self.job_status:
                return self.job_status['status']
            else:
                raise ValueError('There is no status field in the server response!\n%s') % json.dumps(content, indent=4)
                return False
        else:
            raise ValueError('Got error code %s from %s.' % (response.status_code, self.server_url))
            return False

    # Fetches the status of the export job at regular intervals (by default every two seconds) until the job is complete.
    def monitor_job_status(self):
        while self.__get_job_status() == 'incomplete':
            # TODO Add a progress bar
            # Two seconds delay before next cycle
            time.sleep(2)

        return self.job_status['status'] == 'complete'

    # Gets a download link
    def get_download_link(self):
        # Wait a job to be completed
        if self.monitor_job_status():
            # Return a link to the PDF file
            return self.job_status['downloadUrl']
        else:
            # Echo got some error
            raise ValueError('Job finished with a status code %s at step %s.' % (self.job_status['status'], self.job_status['step']))
            return False

    # Downloads the pdf file
    def download_pdf_file(self, filename=None):
        # Get a download link
        download_url = self.get_download_link()

        # Set a file name if not defined
        if not filename:
            filename = urllib.parse.unquote('%s/%s' % (os.getcwd(), download_url.split('/')[-1]))
        else:
            # Check if the file's upper level directory exists
            if path != '' and not os.path.isdir(path):
                raise ValueError('The file path does not exist! (%s)' % path)

        # Download the file only if it doesn't exist
        if not os.path.isfile(filename):
            # Download the file with chunks
            request = requests.get(download_url, stream=True, verify=self.check_certificate, auth=self.authentication)
            with open(filename, 'wb') as destination:
                for chunk in request.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        destination.write(chunk)

            # If the file still opened
            if not destination.closed:
                # Flush all unsaved data to disk
                destination.flush()
                # Close the file
                destination.close()

        # Return a full path to the filename
        return filename

    # Returns a string representation
    def __str__(self):
        return self.download_pdf_file()

    # Returns a class representation
    def __repr__(self):
        return self.__str__()

