In order for email parsing to work, configure Outlook to have a folder (just under your "Inbox").
In config.json, be sure to set parsing.outlook_reports_folder to match the name of this folder.

The parsing code relies on the following rule:


Apply this rule after the message arrives
from <Release Engineer 1> or <Release Engineer 2> or James Fulford
    and with 'Mirror post report' or 'Live post report' or 'Mirror Post report' or 'Live Post report'
move it to the <parsing.outlook_reports_folder> folder
    and stop processing more rules


