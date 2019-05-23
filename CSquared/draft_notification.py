# draft_notification upgrade 7.22.x env1 [env2 [...]]

import sys
import datetime
from dateutil.relativedelta import relativedelta
import os

from css import config
from css.outlook import OUTLOOK


DTFMT = "%B %d, %Y"

SUBJECT = "System Upgrade Notice {version} - {environment}"


def main():
    # 1: message_type
    # 2: version (7.23.x)
    # 3+: environment(s)

    # Retrive contents of message
    message_type = sys.argv[1]
    assert message_type in os.listdir(
        config.NOTIFICATION_FORMATS_DIRECTORY
    )
    filename = os.path.join(
        os.path.expanduser(config.NOTIFICATION_FORMATS_DIRECTORY),
        message_type
    )

    with open(filename, "r") as phile:
        HTMLBODY = phile.read()

    version = sys.argv[2].lower()

    RELEASE_NOTES_DIRECTORY = os.path.join(
        os.path.expanduser(config.RELEASE_NOTES_DIRECTORIES),
        version
    )
    try:
        RELEASE_NOTES_FILES = map(
            lambda x: os.path.join(RELEASE_NOTES_DIRECTORY, x),
            os.listdir(RELEASE_NOTES_DIRECTORY)
        )
    except OSError:
        RELEASE_NOTES_FILES = []

    for environment in sys.argv[3:]:
        config.MASTER_LOGGER.info("Drafting ")
        context = {
            "environment": environment.upper(),
            "version": version,
            "date": (
                datetime.datetime.today() + relativedelta(weekday=2)
            ).strftime(DTFMT)
        }

        # Create mail and configure recipients
        mail = OUTLOOK.CreateItem(0)
        mail.To = "system.upgrades@jamesfulford.com"
        mail.BCC = environment.upper()

        # Set email contents
        mail.Subject = SUBJECT.format(**context)
        mail.HTMLBody = HTMLBODY.format(**context).replace("\n", "<br />")

        # If upgrade, attach release notes if available.
        if message_type == "upgrade":
            for att in RELEASE_NOTES_FILES:
                mail.Attachments.Add(Source=att)

        mail.Save()  # saves to drafts folder

    print """
        1. Change "FROM" field to "siteportal.upgrades"
        2. Change "BCC" field to correct group
            update the group members if not already done
        3. Set the date to be the date in Smartsheet + 1 day
        4. Set the correct maintenance window corresponding to this environment
    """
