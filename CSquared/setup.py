from distutils.core import setup
from setuptools import find_packages


desc = "C Squared Systems Release Assistance Framework"

kwargs = {
    "name": "cssraf",
    "description": desc,
    "author": "James Patrick Fulford",
    "author_email": "james.fulford@csquaredsystems.com",
    "url": (
        "https://jamesfulford.com"
    ),
    "license": "Apache-2.0",

    "version": "1.0.0",
    "packages": find_packages(),

    "install_requires": [
        "openpyxl",
        "xlrd",
        "xlsxwriter",
        "pandas",
        "matplotlib",
        "mysql-connector==2.1.4",
        "sqlalchemy",
        "python-docx",
        "docx-mailmerge",
        "fulford.data",
        "beautifulsoup4"  # parsing
    ],

    "entry_points": {
        "console_scripts": [
            # Broad Statements
            "poll=css.release.ui.console.mainstream:poll",
            "cycle=css.release.ui.console.mainstream:cycle_rulings",
            (
                "render_decisions="
                "css.release.ui.console.mainstream:render_decisions"
            ),

            # Atomic Actions
            "summary=css.release.ui.console.atoms:summary",
            "query=css.release.ui.console.atoms:query",
            "process=css.release.ui.console.atoms:process",
            "draft=css.release.ui.console.atoms:draft_rulings",
            "stage=css.release.ui.console.atoms:stage_rulings",
            "render=css.release.ui.console.atoms:render",

            # Extra Tools
            "monitor=css.release.ui.console.special:after_hours",
            "rebuild=css.release.ui.console.special:add_rebuild_case",

            # Report
            "report=css.release.ui.console.report:report",

            # Prepare
            (
                "prepare="
                "css.release.ui.console.prepare:prepare_post_from_json"
            ),

            # Make Notification
            "emails=css.release.ui.console.special:get_emails",
            "notification=css.notifications.draft_notification:main",

            # Report Parsing
            "state=css.parsing.console:print_env_states",
            "parse=css.parsing.console:parse_reports",
        ]
    },

    "include_package_data": True,

    "data_files": {
        # include basic template structures
        ".": [".cssraf.json"]
    }.items()
}

setup(
    **kwargs
)
