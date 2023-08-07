###########################################################################
# Asterisk automatic config file generator
# John Lucas - john@laserbeam31.tk
#
# Automatically generates SIP and dialplan configuration files for an 
# Asterisk server, based on input CSV data.
###########################################################################

#!/usr/bin/env python3

import csv

# Input data:
# -----------

print("**Inputting user-defined parameters**")

# Gather filenames from user:
extensionsFilename = str(input("Enter name of input CSV file containing extension details (leave blank for default): "))
sipFilename = str(input("Enter name of SIP extension config file to be generated (leave blank for default): "))
dialplanFilename = str(input("Enter name of dialplan config file to be generated (leave blank for default): "))

# Set defaults if filenames left blank:
if len(extensionsFilename) == 0:
    extensionsFilename = "sip_autoconfig_csv_template.ods.csv"
if len(sipFilename) == 0:
    sipFilename = "pjsip.conf"
if len(dialplanFilename) == 0:
    dialplanFilename = "extensions.conf"

# Open output config files:
#sipFilename = 'pjsip.conf'
#dialplanFilename = 'extensions.conf'
sipOutFile = open(sipFilename, 'wt')
dialplanOutFile = open(dialplanFilename,'wt')

# Load CSV file containing entry for each extension:
extensionsDataFile = open(extensionsFilename,'rt')
extensionData = csv.reader(extensionsDataFile)

# Gather NAT parameters from user:
localSubnet = input("Enter local subnet in CIDR notation (xxx.xxx.xxx.xxx/xx): ")
wanAddress = input("Enter public IP address of server (xxx.xxx.xxx.xxx): ")
print("---------")

# Initialise and populate storage lists/objects:
# ----------------------------------------------

# Dial group lists:
dialGroup1Number = 0
dialGroup1NumberSet = False
dialGroup1 = []
dialGroup2Number = 0
dialGroup2NumberSet = False
dialGroup2 = []
dialGroup3Number = 0
dialGroup3NumberSet = False
dialGroup3 = []

# List to contain extension objects:
extensions = []

# Create object template for extension
class telephone:
    def __init__(self, tel_extensionNumber, tel_callerID, tel_username, tel_authenticationMethod, tel_passwd, tel_ipAddr, tel_dialGroup1, tel_dialGroup2, tel_dialGroup3):
        self.extensionNumber = tel_extensionNumber.lower().strip()
        self.callerID = tel_callerID.lower().strip()
        self.username = tel_username.lower().strip()
        self.authenticationMethod = tel_authenticationMethod.lower().strip()
        self.passwd = tel_passwd.lower().strip()
        self.ipAddr = tel_ipAddr.lower().strip()
        self.dialGroup1 = tel_dialGroup1.lower().strip()
        self.dialGroup2 = tel_dialGroup2.lower().strip()
        self.dialGroup3 = tel_dialGroup3.lower().strip()

# Loop through extracted CSV values and create telephone objects / populate dial groups
print("**Processing CSV records**")
rowCount = 0
for row in extensionData:
    if rowCount!=0:
        # Skip empty/unidentified CSV rows
        if len(row[0])==0:
            pass
        else:
            extension = telephone(str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]),str(row[6]),str(row[7]),str(row[8]))
            extensions.append(extension)
    rowCount += 1

print("%s records processed from input CSV file." % str(rowCount-1))
print("---------")

# Error checking:
rowCount = 0
for extension in extensions:
    rowCount += 1
    # Basic checks
    if extension.extensionNumber[0] == "0":
        raise ValueError("The phone number of an extension cannot begin with a [0]")
    if len(extension.extensionNumber) == 0:
        raise ValueError("Missing extension number in row %s of CSV data" % str(rowCount))
    if len(extension.callerID) == 0:
        raise ValueError("Missing caller ID in row %s of CSV data" % str(rowCount))
    if len(extension.username) == 0:
        raise ValueError("Missing username in row %s of CSV data" % str(rowCount))
    if len(extension.authenticationMethod) == 0:
        raise ValueError("Missing authentication method in row %s of CSV data" % str(rowCount))
    # Check if authentication parameters correctly set
    if extension.authenticationMethod=="IP" and len(extension.ipAddr)==0:
        raise ValueError("IP address for row %s of CSV data cannot be left blank if authentication method for this entry is set to [IP]" % str(rowCount))
    if extension.authenticationMethod=="PWD" and len(extension.passwd)==0:
        raise ValueError("Password for row %s of CSV data cannot be left blank if authentication method for this entry is set to [PWD]" % str(rowCount))
    # Check for overlapping extension numbers
    for extensionSubCount in range(rowCount,len(extensions)):
        if extension.extensionNumber == extensions[extensionSubCount].extensionNumber:
            raise ValueError("Two extensions cannot have same number")
    # Check if dial group numbers overlap with any extension numbers
    for extensionSubCount in range(0,len(extensions)):
        if (extension.extensionNumber==extensions[extensionSubCount].dialGroup1) or (extension.extensionNumber==extensions[extensionSubCount].dialGroup2) or (extension.extensionNumber==extensions[extensionSubCount].dialGroup3):
            raise ValueError("An extension and a dial group cannot have the same number")

# Generate dial groups:
print("**Amalgamating dial groups**")
for extension in extensions:
    extDialGroupData = [extension.dialGroup1,extension.dialGroup2,extension.dialGroup3]
    # Check for duplicate dial group entries in same row
    for groupCount in range(0,2):
        for groupSubCount in range((groupCount+1),3):
            if extDialGroupData[groupCount] == extDialGroupData[groupSubCount]:
                extDialGroupData[groupSubCount] = ""
                #raise RuntimeError("Cannot assign a single extension to same dial group more than once")

    # Allocate each extension to correct dial group(s)
    for extDialGroupNumber in extDialGroupData:
        if len(extDialGroupNumber) > 0:
            if extDialGroupNumber==dialGroup1Number and dialGroup1NumberSet==True:
                dialGroup1.append(extension.username)
            elif extDialGroupNumber==dialGroup2Number and dialGroup2NumberSet==True:
                dialGroup2.append(extension.username)
            elif extDialGroupNumber==dialGroup3Number and dialGroup3NumberSet==True:
                dialGroup3.append(extension.username)
            else:
                if dialGroup1NumberSet == False:
                    dialGroup1.append(extension.username)
                    dialGroup1Number = extDialGroupNumber
                    dialGroup1NumberSet = True
                elif dialGroup2NumberSet == False:
                    dialGroup2.append(extension.username)
                    dialGroup2Number = extDialGroupNumber
                    dialGroup2NumberSet = True
                elif dialGroup3NumberSet == False:
                    dialGroup3.append(extension.username)
                    dialGroup3Number = extDialGroupNumber
                    dialGroup3NumberSet = True
                else:
                    raise ValueError("More than three dial groups cannot be defined")

print("Dial group %s members: %s" % (dialGroup1Number, str(dialGroup1)))
print("Dial group %s members: %s" % (dialGroup2Number, str(dialGroup2)))
print("Dial group %s members: %s" % (dialGroup3Number, str(dialGroup3)))
print("---------")

# Write config files:
# -------------------

# Generate standard required pjsip.conf lines:
udpTransportBasic = [
    "[transport-udp]",
    "type=transport",
    "protocol=udp",
    "bind=0.0.0.0"
]
udpTransportNat = [
    "[transport-udp-nat]",
    "type=transport",
    "protocol=udp",
    "bind=0.0.0.0",
    "local_net=%s" % localSubnet,
    "external_media_address=%s" % wanAddress,
    "external_signalling_address=%s\n" % wanAddress
]
# Write standard pjsip.conf lines:
sipOutFile.write("; Basic transport parameters\n")
for line in udpTransportBasic:
    sipOutFile.write(line+"\n")
sipOutFile.write("\n; NAT transport parameters\n")
for line in udpTransportNat:
    sipOutFile.write(line+"\n")

# Write first extensions.conf line:
dialplanOutFile.write("[users]\n")

# Generate required lines for pjsip.conf and extensions.conf for each extension:
print("**Configuring individual extensions**")
for extension in extensions:
    print("Configuring extension: %s" % extension.username)
    # Pjsip.conf lines (authentication-dependent)
    if extension.authenticationMethod.lower() == "pwd":
        mainPjsipEntry = [
            "\n;%s" % extension.username,
            "[%s]" % extension.username,
            "type=endpoint",
            "transport=transport-udp",
            "context=users",
            "disallow=all",
            "allow=alaw",
            "allow=ulaw",
            "auth=%s" % extension.username,
            "aors=%s" % extension.username,
            'callerid="%s <%s>"' % (extension.callerID,extension.username)
        ]
        authPjsipEntry = [
            "[%s]" % extension.username,
            "type=auth",
            "auth_type=userpass",
            "password=%s" % extension.passwd,
            "username=%s" % extension.username
        ]
        aorPjsipEntry = [
            "[%s]" % extension.username,
            "type=aor",
            "max_contacts=5"
        ]
    elif extension.authenticationMethod.lower() == "ip":
        mainPjsipEntry = [
            "\n;%s" % extension.username,
            "[%s]" % extension.username,
            "type=endpoint",
            "transport=transport-udp",
            "context=users",
            "disallow=all",
            "allow=alaw",
            "allow=ulaw",
            "aors=%s" % extension.username,
            'callerid="%s <%s>"' % (extension.callerID,extension.username)
        ]
        authPjsipEntry = [
            "[%s]" % extension.username,
            "type=identify",
            "endpoint=%s" % extension.username,
            "match=%s" % extension.ipAddr
        ]
        aorPjsipEntry = [
            "[%s]" % extension.username,
            "type=aor",
            "max_contacts=5"
        ]
    # Extensions.conf lines
    mainExtensionsEntry = "exten => %s,1,Dial(PJSIP/%s)" % (extension.extensionNumber,extension.username)
    # Write all lines out to files
    for line in mainPjsipEntry:
        sipOutFile.write(line+"\n")
    for line in authPjsipEntry:
        sipOutFile.write(line+"\n")
    for line in aorPjsipEntry:
        sipOutFile.write(line+"\n")
    dialplanOutFile.write(mainExtensionsEntry+"\n")

# Write dial groups to extensions.conf:
if len(dialGroup1)>0:
    dialGroup1Line = "exten => %s,1,Dial(PJSIP/%s" % (dialGroup1Number,dialGroup1[0])
    for username in dialGroup1[1:]:
        dialGroup1Line = dialGroup1Line + ("&PJSIP/%s" % username)
    dialplanOutFile.write(dialGroup1Line+")\n")
if len(dialGroup2)>0:
    dialGroup2Line = "exten => %s,1,Dial(PJSIP/%s" % (dialGroup2Number,dialGroup2[0])
    for username in dialGroup2[1:]:
        dialGroup2Line = dialGroup2Line + ("&PJSIP/%s" % username)
    dialplanOutFile.write(dialGroup2Line+")\n")
if len(dialGroup3)>0:
    dialGroup3Line = "exten => %s,1,Dial(PJSIP/%s" % (dialGroup3Number,dialGroup3[0])
    for username in dialGroup3[1:]:
        dialGroup3Line = dialGroup3Line + ("&PJSIP/%s" % username)
    dialplanOutFile.write(dialGroup3Line+")\n")

# Clean up / close files
# ----------------------

sipOutFile.close()
dialplanOutFile.close()
extensionsDataFile.close()

# TODO:
# - Add NAT traversal per-extension setting, to apply [transport-udp-nat] to specific extension(s)