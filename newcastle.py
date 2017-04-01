# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 16:48:59 2017

@author: zpeng
"""

import pandas as pd
import datetime
df = pd.read_csv( "castle-event-data-v4.csv",sep=',', header=0, parse_dates=True,quoting=1 )
