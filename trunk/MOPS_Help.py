'''
Help: provides some basic help facilities

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.
'''
import sys
import platform
import MOPS_Misc

def help():
    """Provides basic help facilities online - get more help using different commands
    """
    print(' ')
    print('To logoff and exit MOPS, type QUIT or EXIT')
    print(' ')
    print('There are a large number of commands in MOPS.  See the User Guide for')
    print('full details on these commands.  Commands have to be entered in the ')
    print('following manner:')
    print('  COMMAND data-1;data-2;data-3...')
    print('where COMMAND is the 6-digit MOPS command and the data is entered as')
    print('parameters, delimited by a semi-colon.  For a list of available commands')
    print('type ASSIST.  To see what data is required for a particular command')
    print('type the command name followed by a question mark.')
    print(' ')
    print('In addition:')
    print('  for details about MOPS, type ABOUT')
    print('  to see the license, type LICENS')
    
def about():
    """Provides summary details about MOPS - version, shoer history etc
    """
    print(' ')
    print('MODEL OPERATIONAL PROCESSING SYSTEM (MOPS)')
    print('==========================================')
    print('')
    print('Python version details: ' + str(sys.version_info[0]) + '.' +  str(sys.version_info[1]) + ' on ' + platform.system())
    mops_directory = MOPS_Misc.directory_location()
    print('Location of data files: ' + mops_directory)
    print(' ')
    print('MOPS was originally written to provide support for Model Railroad')
    print('Operations, and is based on mainframe systems used in the 20th Century.')
    print('')
    print('MOPS is Copyright Brian Fairbairn 2009/2010.')
    print('Licenced under the EUPL.  You may not use this work except in compliance with')
    print('the Licence.  You may obtain a copy of the Licence at')
    print('http://ec.europa.eu/idabc/eupl or as attached with this application')
    print('(see License.txt)).  Unless required by applicable law or agreed to in writing,')
    print('software distributed under the Licence is distributed on an AS IS basis')
    print('WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied. See')
    print('the Licence governing permissions and limitations under the Licence.')
    return
