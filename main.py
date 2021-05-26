import tkinter as tk
import logging

root = tk.Tk() #main window
root.mainloop() #infinite loop waits for user interaction

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter( '%(asctime)s %(levelname)s :: %(message)s' )
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logger.debug("This is debug")
logger.info("This is info")
logger.warning("This is info")
logger.error("This is info")
