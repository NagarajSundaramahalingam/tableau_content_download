# Download Tableau content

## Objective

Python script to download workbook, worksheet data, worksheet view, worksheet pdf.

### How to execute?

1. Edit the *configuration.py* file.

	```python
	# Configuration details
	SERVER_NAME = <SERVER_NAME>
	USER_NAME = <USER_NAME>
	PASSWORD = <PASSWORD>
	SITE_NAME = <SITE_NAME>
	VERSION = 3.7

	# File and folder details
	INPUT_FILE = 'input.csv'
	DOWNLOAD_FOLDER = 'downloaded'
	OUTPUT_FOLDER = 'output'
	ARCHIVE_FOLDER = 'archive'
	LOG_FOLDER = 'log'	
	```
2. Edit input.csv file
	- In download column, *Y* represents to download.

***Sample input file***

	|WORKBOOK_NAME|WORKSHEET_NAME|DOWNLOAD_DATA|DOWNLOAD_IMAGE|DOWNLOAD_PDF|DOWNLOAD_WORKBOOK|
	|-------------|--------------|-------------|--------------|------------|-----------------|
	|Work book 1  |Sheet 1       |Y            |Y             |Y           |Y                |
	|Work book 2  |Sheet 1       |Y            |Y             |Y           |N                |
	|Work book 3  |Sheet 1       |N            |Y             |Y           |Y                |
	
3. Execute *download\_tableau_content.py* script.

### Sample Output

On successful completion of script, it creates following folder/file structure

```cmd
C:.
│   configurations.py
│   download_tableau_content.py
│   input.csv
│   README.md
│
├───archive
│       tableau_content_download_04072020_180044.csv
│
├───downloaded
│       Workbook1_Sheet1_04072020_183142.csv
│       Workbook1_Sheet1_04072020_183144.png
│       Workbook1_Sheet1_04072020_183146.pdf
│       Work book 1.twb
│       .
│       .
│       .
│
├───log
│       tableau_content_download_2020-07-04_183124.log
│
├───output
        tableau_content_download_04072020_183154.csv
```

***Sample Output file:***

|WORKBOOK_NAME|WORKSHEET_NAME|DOWNLOAD_DATA|DOWNLOAD_IMAGE|DOWNLOAD_PDF|DOWNLOAD_WORKBOOK|WORKBOOK_ID                         |WORKBOOK_PATH             |VIEW_URL                     |VIEW_ID                             |DATA_PATH                                      |IMAGE_PATH                                     |PDF_PATH                                       |
|-------------|--------------|-------------|--------------|------------|-----------------|------------------------------------|--------------------------|-----------------------------|------------------------------------|-----------------------------------------------|-----------------------------------------------|-----------------------------------------------|
|Work book 1  |Sheet 1       |Y            |Y             |Y           |Y                |057c0818-1a67-452d-9e70-7fdb83b74aed|downloaded\Work book 1.twb|workbooksample1/sheets/Sheet1|20d485c6-2788-4821-8978-a3dba835137b|downloaded/Workbook1_Sheet1_04072020_183142.csv|downloaded/Workbook1_Sheet1_04072020_183144.png|downloaded/Workbook1_Sheet1_04072020_183146.pdf|
|Work book 2  |Sheet 1       |Y            |Y             |Y           |N                |-------                             |-------                   |-------                      |-------                             |-------                                        |-------                                        |-------                                        |
|Work book 3  |Sheet 1       |N            |Y             |Y           |Y                |-------                             |-------                   |-------                      |-------                             |-------                                        |-------                                        |-------                                        |


## Design


*[Refer complete architecture design here if the below image is broken](decks/tableau_content_download_design.html)*


![](decks/tableau_content_download_design.svg)


### Note:

Rest API methods used here are on version 3.7 or more. 

**[Refer Tableau server and Rest API versions here](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm)*