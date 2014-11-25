'''
Model Operations Processing System

Copyright Brian Fairbairn 2009

Licenced under the EUPL.  You may not use this work except in compliance with
the Licence.  You may obtain a copy of the Licence at
http://ec.europa.eu/idabc/eupl or as attached with this application
(see Licence file).  Unless required by applicable law or agreed to in writing,
software distributed under the Licence is distributed on an 'AS IS' basis
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied. See
the Licence governing permissions and limitations under the Licence.

'''
if __name__ == "__main__":
    import sys
    import time

    import MOPS_Control
    MOPS_Control.MOPS()
    print('MOPS terminated at ' + time.asctime()) 
    time.sleep(2)

