__version__ = "0.7.0"
__author__ = "Oliver Lindemann"

"""
to use the GUI recorder:
``
    from forceDAQ import gui

    gui.start(remote_control=False,
              ask_filename=True,
               calibration_file="FT_demo.cal")
``

import relevant stuff to program your own recorder:
``
    from forceDAQ import recorder_classes
``

import relevant stuff for remote control of the GUI recorder:
``
    from forceDAQ import remote_control
``

For function to support data handling see the folder pyForceDAQ/analysis

"""

