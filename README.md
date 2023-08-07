# asterisk-auto-config
Python program to automatically generate SIP and dialplan config files for a basic Asterisk SIP server.

Files
-----

- ```sip_autoconfig_csv_template.ods``` - Spreadsheet with preformatted columns to be populated with details for each telephone extension to be served by the Asterisk server. When populated, export this spreadsheet as a CSV file; this is loaded by the main program, to instruct generation of correct configuration file entries for each extension.

- ```asterisk_auto_config.py```  - Main Python script to read CSV file containing extension data and generate pjsip.conf/extensions.conf asterisk configuration files.

Operation steps
---------------

This guide assumes use of a Linux PC with Python3 installed. The Python3 /csv/ module is also required.

1. Download all files from this repository and place them in the same local directory (from now on referred to as the "project directory").
2. Open ```sip_autoconfig_csv_template.ods``` in a spreadsheet program of your choice and populate the rows with data for each extension, according to the prepopulated headings.
3. Once ```sip_autoconfig_csv_template.ods``` has been populated, export this spreadsheet as a CSV file.
4. Open a terminal in the project directory and use the command ```python3 asterisk_auto_config.py``` to execute the program.
5. The program will first ask for the filename of the input CSV file. Enter here the full name of the above exported CSV file. The default option of ```extensions.csv``` is set if this prompt is left blank.
6. The program next asks for the output filenames to be used for the generated SIP extension and dialplan configuration files. If left blank, the defaults of ```pjsip.conf``` and ```extensions.conf``` are used, respectively.
7. Finally,the program requests details about the local and public IP addresses/subnets of the Asterisk server to which the generated configuration files will be applied. These are necessary in order to correctly set the NAT traversal parameters in the SIP config file.
8. The program reads the contents of the generated CSV file and converts this into syntactically correct SIP endpoint and dialplan files (```pjsip.conf``` and ```extensions.conf```, if default values are set above) which can be loaded into the configuration file directory of an Asterisk server.
