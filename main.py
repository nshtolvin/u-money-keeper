# -*- coding: utf-8 -*-
#

# Entry point to the application. Runs the main program.py program code.

# region Import
import os
import sys
import traceback
# endregion Import


# disable logging on a file file c:\Users\<user_name>\.kivy\logs\<filename> (only console logging is allowed)
os.environ["KIVY_NO_FILELOG"] = "1"
# connecting additional application libraries
cur_directory = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(cur_directory, 'libs/applibs'))

# region Context
CONFIGURATION_FILE = 'conf.json'
# endregion


def main():
    app = None

    try:
        from libs.sql_worker_lib import SQLWorker
        from libs.configuration_lib import read_settings
        from program import MainApp

        program_settings = read_settings(CONFIGURATION_FILE)
        SQLWorker.check_db_file_exist(cur_directory, program_settings["DB_FILENAME"])

        app = MainApp(program_settings)
        app.run()
    except Exception as err:
        import libs.logger_lib as logger
        logger.error("U-Money-Keeper", err)
        # text_error = traceback.format_exc()
        traceback.print_exc(file=open(os.path.join(cur_directory, 'error.log'), 'w'))

        if app:
            try:
                app.stop()
            except AttributeError:
                app = None


if __name__ in ('__main__', '__android__'):
    main()
