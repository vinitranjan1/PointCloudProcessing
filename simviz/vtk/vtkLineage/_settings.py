import pandas as pd, datetime

"""
Many classes to be used as constants throughout the visualization

Eventually, many of these constants should be stored in the .ini files
"""

class AISLE:
    length = 60    # inches
    x = length

class PALLET:
    length = 48     # inches
    width = 40      # inches
    height = 92     # inches
    x = length
    y = width
    z = height

class PALLET_SLOT:
    length = 57     # inches
    width = 49      # inches
    height = 119    # inches
    x = length
    y = width
    z = height

# From swisslog sketchup file
class PALLET_SLOT__SWISSLOG:
    length = 57     # inches
    width = 49      # inches
    height = 119    # inches
    x = length
    y = width
    z = height

# helper lookup table for interpretting system acronyms from system identifiers
SYSTEMS_LOOKUP = {
    'levels': {'loc': 'storage_location'},
    'buffers':   {},
    'elevators': {},
    'cranes': {}
    }

ACTION_LOOKUP = {
    'EIDL': 1.0,
    'EPCK': 2.0,
    'EMNP': 3.0,
    'EPPU': 4.0,
    'EMWP': 5.0,
    'EPDU': 6.0,
    'EPDU': 7.0,
    'CIDL': 8.0,
    'CRRT': 9.0,
    'CRRT': 10.0,
    'CPCK': 11.0,
    'CMNP': 12.0,
    'CPPU': 13.0,
    'CMWP': 14.0,
    'CPDO': 15.0,
    'CPDO': 16.0
}

STATE_LOOKUP = {
    'EIDL': 1.0,
    'CIDL': 2.0,
    'EPCK': 3.0,
    'CPCK': 4.0,
    'EPLC': 5.0,
    'CPLC': 6.0,
}
