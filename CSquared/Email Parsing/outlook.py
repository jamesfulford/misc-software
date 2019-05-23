import os
try:
    import win32com.client
except ImportError:
    print open(
        os.path.join(os.path.dirname(__file__), "parsing", "README.txt")
    ).read()
    raise


OUTLOOK = win32com.client.Dispatch("Outlook.Application")
MAPI = OUTLOOK.GetNamespace("MAPI")
