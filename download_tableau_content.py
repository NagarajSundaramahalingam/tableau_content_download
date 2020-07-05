# Import libraries
import os
import sys
import logging
from datetime import datetime
import requests
from glob import glob
import shutil
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import configurations as c

# Disable warnings (Making without verification connection)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Create directory
if not os.path.exists(c.LOG_FOLDER):
    os.makedirs(c.LOG_FOLDER)

if not os.path.exists(c.DOWNLOAD_FOLDER):
    os.makedirs(c.DOWNLOAD_FOLDER)

if not os.path.exists(c.OUTPUT_FOLDER):
    os.makedirs(c.OUTPUT_FOLDER)

if not os.path.exists(c.ARCHIVE_FOLDER):
    os.makedirs(c.ARCHIVE_FOLDER)

# Move file to archive
prev_files = glob(f'{c.LOG_FOLDER}/*.log')
prev_files.extend(glob(f'{c.DOWNLOAD_FOLDER}/*.*'))
prev_files.extend(glob(f'{c.OUTPUT_FOLDER}/*.*'))

for f in prev_files:
    if not os.path.isfile(f'{c.ARCHIVE_FOLDER}/{os.path.basename(f)}'):
        shutil.move(f, c.ARCHIVE_FOLDER)
    else:
        os.remove(f)

# Log details
log_file = f'{c.LOG_FOLDER}/tableau_content_download_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

main_url = f'https://{c.SERVER_NAME}/api/{c.VERSION}'
auth_url = f'{main_url}/auth/signin'

auth_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
auth_body = {'credentials': {
                'name': c.USER_NAME, 'password': c.PASSWORD,
                'site': {'contentUrl': c.SITE_NAME}}}

conn_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Tableau-Auth': ''}


def tab_sign_in(url, body, headers):
    '''Sign in tableau server and returns the site id, user id, token
        Input arguments:
            url = sign in url(type:str). (Ex.https://<TABLEAU_SERVER>/api/3.7/auth/signin)
            body = credentials and site(type:json)
            headers = header - content type(type:json)
        Output arguments:
            site_id = id of site(type:str)
            user_id = id of user(type:str)
            token_id = auth token(type:str)
        Error:
            Returns status_code and exit
    '''
    # Verify is set to False
    server_login = requests.post(url, json=body, headers=headers, verify=False)

    if server_login.status_code == 200:
        logging.info(f'Server - {c.SERVER_NAME} is signed in successfully with the user {c.USER_NAME}.')
        return server_login.json()['credentials']['site']['id'],\
                server_login.json()['credentials']['user']['id'],\
                server_login.json()['credentials']['token']
    else:
        logging.error(f'{c.SERVER_NAME} is failed to sign-in. {server_login.status_code}')
        logging.error(f'Response body - {server_login.json()}')
        sys.exit(1)


def tab_sign_out(url, headers):
    '''Sign out tableau server
        Input arguments:
            url = sign out url(type:str)
            headers = header - content type(type:json)
        Output arguments:
            status_code
        Error:
            Returns status_code and exit
    '''
    # Verify is set to False
    server_logout = requests.post(url, headers=headers, verify=False)
    return server_logout.status_code


def get_workbook_id(name, site_id, headers):
    '''Returns workbook id for the given workbook name
        Input arguments:
            site_id = id of site(type:str)
            headers = headers with token(type:json)
            name = workbook name
        Output argument:
            workbook_id = id of workbook(type:str)
        Error:
            Returns None or ERROR
    '''
    url = f'{main_url}/sites/{site_id}/workbooks?filter=name:eq:{name}'
    logging.info(f'Get workbook id api {url}')
    get_wb = requests.get(url, headers=headers, verify=False)
    logging.info(f'Get workbook id response {get_wb.json()}')
    if get_wb.status_code == 200:
        wbs = get_wb.json().get('workbooks').get('workbook')
        logging.info(f'Workbook id for {name} - {wbs[0]["id"] if wbs is not None else None}')
        return wbs[0]['id'] if wbs is not None else None
    else:
        logging.error(f'Get workbook id is failed Due to {get_wb.json()}')
        return 'ERROR'


def download_workbook(wb_id, site_id, headers):
    '''Downloads the workbook and returns the file name
        Input arguments:
            wb_id = id of workbook(type:str)
            site_id = id of site(type:str)
            headers = headers with token(type:str)
        Output argument:
            file_name = file name of downloaded workbook(type:str)
        Error:
            Returns ERROR
        '''
    url = f'{main_url}/sites/{site_id}/workbooks/{wb_id}/content'
    logging.info(f'Get workbook content api {url}')
    get_wb = requests.get(url, headers=headers, verify=False)
    if get_wb.status_code == 200:
        file_header = get_wb.headers.get('Content-Disposition')
        file_name = os.path.join(c.DOWNLOAD_FOLDER, re.findall('filename="(.+)"', file_header)[0])
        with open(file_name, 'wb') as f:
            f.write(get_wb.content)
        logging.info(f'Downloaded workbook - {file_name}')
        return file_name
    else:
        logging.error(f'Download workbook is failed Due to {get_wb.json()}')
        return 'ERROR'


def get_view_id(name, site_id, headers):
    '''Returns view id for the given workbook name/sheet name
        Input arguments:
            name = workbook and view name
            site_id = id of site(type:str)
            headers = headers with token(type:json)
        Output argument:
            view_id = id of view(type:str)
        Error:
            Returns None or ERROR
    '''
    url = f'{main_url}/sites/{site_id}/views?filter=contentUrl:eq:{name}'
    logging.info(f'Get view id api {url}')
    get_view = requests.get(url, headers=headers, verify=False)
    logging.info(f'Get workbook id response {get_view.json()}')
    if get_view.status_code == 200:
        views = get_view.json().get('views').get('view')
        logging.info(f'View id for url {name} - {views[0]["id"] if views is not None else None}')
        return views[0]['id'] if views is not None else None
    else:
        logging.error(f'Get view id is failed Due to {get_view.json()}')
        return 'ERROR'


def download_view_data(view_id, site_id, headers, name):
    '''Downloads the view data and returns the file name
        Input arguments:
            view_id = id of view(type:str)
            site_id = id of site(type:str)
            headers = headers with token(type:str)
            name = concatenation of workbook and sheet with timestamp
        Output argument:
            file_name = file name of downloaded view(type:str)
        Error:
            Returns ERROR
        '''
    url = f'{main_url}/sites/{site_id}/views/{view_id}/data?maxAge=1'
    logging.info(f'Get view data api {url}')
    get_view_data = requests.get(url, headers=headers, verify=False)
    if get_view_data.status_code == 200:
        data_file_name = f'{c.DOWNLOAD_FOLDER}/{name}_{datetime.now().strftime("%d%m%Y_%H%M%S")}.csv'
        with open(data_file_name, 'wb') as f:
            f.write(get_view_data.content)
        logging.info(f'Downloaded view data - {data_file_name}')
        return data_file_name
    else:
        logging.error(f'Download view data is failed Due to {get_view_data.json()}')
        return 'ERROR'


def download_view_image(view_id, site_id, headers, name):
    '''Downloads the view image and returns the file name
        Input arguments:
            view_id = id of view(type:str)
            site_id = id of site(type:str)
            headers = headers with token(type:str)
            name = concatenation of workbook and sheet with timestamp
        Output argument:
            file_name = file name of downloaded view image(type:str)
        Error:
            Returns ERROR
        '''
    url = f'{main_url}/sites/{site_id}/views/{view_id}/image?maxAge=1'
    logging.info(f'Get view image api {url}')
    get_view_image = requests.get(url, headers=headers, verify=False)
    if get_view_image.status_code == 200:
        image_file_name = f'{c.DOWNLOAD_FOLDER}/{name}_{datetime.now().strftime("%d%m%Y_%H%M%S")}.png'
        with open(image_file_name, 'wb') as f:
            f.write(get_view_image.content)
        logging.info(f'Downloaded view image - {image_file_name}')
        return image_file_name
    else:
        logging.error(f'Download view image is failed Due to {get_view_image.json()}')
        return 'ERROR'


def download_view_pdf(view_id, site_id, headers, name):
    '''Downloads the view pdf and returns the file name
        Input arguments:
            view_id = id of view(type:str)
            site_id = id of site(type:str)
            headers = headers with token(type:str)
            name = concatenation of workbook and sheet with timestamp
        Output argument:
            file_name = file name of downloaded view pdf(type:str)
        Error:
            Returns ERROR
        '''
    url = f'{main_url}/sites/{site_id}/views/{view_id}/pdf?maxAge=1'
    logging.info(f'Get view pdf api {url}')
    get_view_pdf = requests.get(url, headers=headers, verify=False)
    if get_view_pdf.status_code == 200:
        pdf_file_name = f'{c.DOWNLOAD_FOLDER}/{name}_{datetime.now().strftime("%d%m%Y_%H%M%S")}.pdf'
        with open(pdf_file_name, 'wb') as f:
            f.write(get_view_pdf.content)
        logging.info(f'Downloaded view pdf - {pdf_file_name}')
        return pdf_file_name
    else:
        logging.error(f'Download view pdf is failed Due to {get_view_pdf.json()}')
        return 'ERROR'


try:
    # Read input file
    input_df = pd.read_csv(c.INPUT_FILE)
    logging.info(f'{c.INPUT_FILE} is read successfully.')

    site_id, user_id, token = tab_sign_in(auth_url, auth_body, auth_headers)
    conn_headers['X-Tableau-Auth'] = token

    output_dict = {}

    for i, r in input_df.iterrows():
        try:

            workbook_id = get_workbook_id(
                            r['WORKBOOK_NAME'], site_id, conn_headers) if r['DOWNLOAD_WORKBOOK'] == 'Y' else None
            workbook_path = download_workbook(
                                workbook_id, site_id, conn_headers) if workbook_id is not None else None
            view_url = r['WORKBOOK_NAME'].replace(' ', '') + '/sheets/' + r['WORKSHEET_NAME'].replace(' ', '')
            view_id = get_view_id(view_url, site_id, conn_headers)
            data_path = download_view_data(
                            view_id, site_id, conn_headers,
                            view_url.replace('/sheets/', '_')) if r['DOWNLOAD_DATA'] == 'Y' else None
            image_path = download_view_image(
                            view_id, site_id, conn_headers,
                            view_url.replace('/sheets/', '_')) if r['DOWNLOAD_IMAGE'] == 'Y' else None
            pdf_path = download_view_pdf(
                            view_id, site_id, conn_headers,
                            view_url.replace('/sheets/', '_')) if r['DOWNLOAD_PDF'] == 'Y' else None

            output_dict[i] = {
                                'WORKBOOK_ID': workbook_id, 'WORKBOOK_PATH': workbook_path,
                                'VIEW_URL': view_url, 'VIEW_ID': view_id,
                                'DATA_PATH': data_path, 'IMAGE_PATH': image_path, 'PDF_PATH': pdf_path}
            print(f'Out of {input_df.shape[0]}, {i+1} - processed')
            logging.info(f'Out of {input_df.shape[0]}, {i+1} - processed')
            logging.info(f'Record {i+1} - details {output_dict}')
        
        except Exception as e:
            logging.error(f'Record - {i+1} processing is failed. Due to {e}')

    output_df = pd.DataFrame.from_dict(output_dict, orient='index')
    result_df = pd.concat([input_df, output_df], axis=1)
    output_file_name = f'{c.OUTPUT_FOLDER}/tableau_content_download_{datetime.now().strftime("%d%m%Y_%H%M%S")}.csv'
    result_df.to_csv(output_file_name, index=False)

    logging.info(f'Tableau content download is completed, Refer output file here - {output_file_name}')

    sign_out = tab_sign_out(f'{main_url}/auth/signout', conn_headers)
    if sign_out == 204:
        logging.info(f'Server - {c.SERVER_NAME} is successfully signed out')
    else:
        logging.error(f'Server - {c.SERVER_NAME} is failed to sign out {sign_out}')

except Exception as e:
    print('Script is failed.')
    logging.error(f'Script is failed. Due to - {e}')

print('Script is completed')
