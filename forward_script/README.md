# Wikipedia to Commons Uploader Forward script
This script forwards from the German Wikipedia to the Upload Wizard on Wikimedia Commons.

It reads the text of the Wikipedia page and uses a Python script to generate information from templates in the text.
The information from the Python script is used to generate URL parameters needed for the Upload Wizard.

## Installation
Clone the repository and run

    composer install

## Local testing

Go to the `forward_script` directory and run the command

    php -S localhost:8080 -t web web/index.php

You can then test it with URLs like

`http://localhost:8080/redirect/Liste_der_Baudenkmäler_in_Abtswind/wlm-de-by?id=D-6-75-111-5&lat=49.77168&lon=10.37051`

The general structure of the URL is

`http://localhost:8080/redirect/WIKIPEDIA_PAGENAME/COMMONS_CAMPAIGN_NAME?id=MONUMENT_ID&lat=LATITUDE&lon=LONGITUDE`

Only `WIKIPEDIA_PAGENAME` and `COMMONS_CAMPAIGN_NAME` are required parameters.
