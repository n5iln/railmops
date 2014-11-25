'''
User Class. Identifies an individual using the system, and is used to control
access to functions and identify owners of printed output

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    13/08/2010 Rev 1 Removed reference to re module.  Unused variable removed.
'''

import sqlite3
import MOPS_Element


class cUsers(MOPS_Element.cElement):
    """Details about Users.  As this is about users, the values of user ids can be confused
    between the user doing the update and the user being updated.  To clarify in this code:
        code - the id of the user being updated
        userid - the id of the user carrying out the update
    Note that adding or changing a user automatically defaults the password to a value of
    'PASSWORD'  Some fields are generated automatically.  A new user is forced to change password
    first time it is used.  Note the term password is the term for the entered value; passcode
    is the term for the encoded value held on the database. There is a startup userid
    ('xuserx', pwd=''xpassx').

    users have certain attributes: access level (supervisor can do anything; normal access has
    update access to railroad running functions only; and read access.  system also controls
    sign-on and sign-off.  there is a disabled indicator which alllows a person to be stopped
    from entering the system, but still retians their details
    """
    extract_code = 'select * from user'
    extract_header = 'id|code|name|passcode|user_type|is_signed_on|has_access_disabled|' +\
                     'get_new_password\n'



    def __init__(self, directory):
        """initiliase the objects with defaults.  this overrides the normal element __init__
        as we are loading the user object before we are loading the params, so we are missing
        chunks of data.  also, some of these variables will be defined as we sign a user on.
        """
        self.directory = directory
        self.uid       = ''
        self.access    = ''
        self.rr        = 'MOPS'
        self.temp      = {}
        return


    
    def aduser(self, message):
        """"A new user will have a user code, name, a default password and an access indicator
        (Supervisor, Normal or Readonly).  The password is encrypted. user signed on should be
        set to N and new user set to Y.  Has access disabled should be set to N.
        """
        if self.show_access(message, 'ADUSER user;user name;(user type[S/N/R])', 'S') != 0:
            return
        
        #user code----------------------------------------------------------------------------------
        user_code, rc = self.extract_field(message, 0, 'USER CODE')
        if rc > 0:
            return

        if len(user_code) > 8:
            print('* USER CODE LIMITED TO 8 CHARACTERS')
            return
                
        #check it does not already exist on the database
        data = (user_code,)
        sql = 'select id from user where user = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* USER CODE ' + user_code + ' ALREADY EXISTS')
            return        

        #user name----------------------------------------------------------------------------------
        user_name, rc = self.extract_field(message, 1, 'USER NAME')
        if rc > 1:
            return

        #user type----------------------------------------------------------------------------------
        user_type, rc = self.extract_field(message, 2, 'USER TYPE')
        if rc > 1:
            return

        if user_type == '':
            user_type = 'R'

        if not(user_type == 'S' or user_type == 'N' or user_type == 'R'):
            print('* USER ACCESS MUST BE S-SUPERVISOR N-NORMAL R-READ ONLY')
            return

        if user_type == 'S':
            type_desc = 'STATUS: SUPERVISOR ACCESS'
        elif user_type == 'N':
            type_desc = 'STATUS: NORMAL ACCESS'
        elif user_type == 'R':
            type_desc = 'STATUS: READ-ONLY ACCESS'
        else:
            type_desc = '* ERROR: UNKNOWN STATUS'

        #carry out the update-----------------------------------------------------------------------
        passcode = self.encrypt('PASSWORD')
        data = (user_code, user_name, passcode, user_type, 'N', 'N', 'Y')
        sql = 'insert into user values (null, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        print('NEW USER DETAILS ADDED')
        print('USERID: ' + user_code + ' NAME: ' + user_name + ' ACCESS: ' + type_desc)
        return
                    

        
    def chuser(self, message):
        """Change name, or access indicator (read-only, normal or supervisor).  other details
        remain unchanged.
        """
        if self.show_access(message, 'CHUSER user;(user name);(user type[S/N/R])', 'S') != 0:
            return

        #user code----------------------------------------------------------------------------------
        user_code, rc = self.extract_field(message, 0, 'USER CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (user_code,)
        sql = 'select name, user_type, id from user where user = ?'
        count, ds_users = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* USER CODE ' + user_code + ' DOES NOT EXIST')
            return

        for row in ds_users:
            user_name = row[0]
            user_type = row[1]
            user_id   = row[2]
            
        #user name ---------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            user_name = value

        #user access--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            user_type = value

        if not(user_type == 'S' or user_type == 'N' or user_type == 'R'):
            print('* USER ACCESS MUST BE S-SUPERVISOR N-NORMAL R-READ ONLY')
            return        

        if user_type == 'S':
            type_desc = 'STATUS: SUPERVISOR ACCESS'
        elif user_type == 'N':
            type_desc = 'STATUS: NORMAL ACCESS'
        elif user_type == 'R':
            type_desc = 'STATUS: READ-ONLY ACCESS'
        else:
            type_desc = '* ERROR: UNKNOWN STATUS'

        #carry out the update-----------------------------------------------------------------------
        data = (user_name, user_type, user_id)
        sql = 'update user set name = ?, user_type = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        print('USER DETAILS CHANGED')
        print('USERID: ' + user_code, ' NAME: ' + user_name, ' ACCESS: ' + type_desc)
        return



    def eduser(self, message):
        """enables or disables a user based on user code.  works as a toggle ie just flips the
        enable/disable flag the other way.
        """
        if self.show_access(message, 'EDUSER user', 'S') != 0:
            return

        #user code----------------------------------------------------------------------------------
        user_code, rc = self.extract_field(message, 0, 'USER CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (user_code,)
        sql = 'select has_access_disabled, id from user where user = ?'
        count, ds_users = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* USER CODE ', user_code, ' DOES NOT EXIST')
            return

        for row in ds_users:
            user_disabled = row[0]
            user_id = row[1]
 
        #make the change----------------------------------------------------------------------------
        if user_disabled == 'N':
            user_disabled = 'Y'
            status_desc = 'DISABLED IN MOPS'
        else:
            user_disabled = 'N'
            status_desc = 'ENABLED IN MOPS'

        #update the database------------------------------------------------------------------------
        data = (user_disabled, user_id)
        sql = 'update user set has_access_disabled = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        print('USER ', user_code, ' HAS BEEN ', status_desc)
        return



    def resetp(self, message):
        """"resets a password to the default value.  the password is encrypted.
        """
        if self.show_access(message, 'RESETP user', 'S') != 0:
            return

        #user code----------------------------------------------------------------------------------
        user_code, rc = self.extract_field(message, 0, 'USER CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (user_code,)
        count, ds_users = self.db_read('select id from user where user = ?', data)
        if count < 0:
            return
        if count == 0:
            print('* USER CODE ', user_code, ' DOES NOT EXIST')
            return
        else:
            for row in ds_users:
                user_id = row[0]

        #update the database------------------------------------------------------------------------
        passcode = self.encrypt('PASSWORD')
        data = (passcode, user_id)
        sql = 'update user set passcode = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        print('USER ', user_code, ' PASSWORD HAS BEEN RESET')
        return

    
        
    def chpass (self, user):
        """allows a user to change a password.  prompted if password is set to the default value.
        the password is encrypted.  This is a prompt-driven verb
        """
        #get the new pasword------------------------------------------------------------------------
        password  = raw_input('ENTER NEW PASSWORD: ')
        password = password.ljust(8)
        password = str.upper(password)
        password = password.strip()

        #process the change-------------------------------------------------------------------------
        passcode = self.encrypt(password)
        data = (passcode, user)
        sql = 'update user set passcode = ? where user = ?'
        if self.db_update(sql, data) != 0:
            return

        print('PASSWORD HAS BEEN CHANGED')
        return


        
    def dxuser(self, message):
        """"Deletes a user from the system using the user code
        """
        if self.show_access(message, 'DXUSER user', 'S') != 0:
            return

        #user code----------------------------------------------------------------------------------
        user_code, rc = self.extract_field(message, 0, 'USER CODE')
        if rc > 0:
            return

        #validate the change - check there is a record to delete
        data = (user_code,)
        sql = 'select id from user where user = ?'
        count, ds_users = self.db_read(sql, data)
        if count == -1:
            return
        if count == 0:
            print('* NO RECORD TO DELETE', user_code, 'DOES NOT EXIST')
            return
        else:
            for row in ds_users:
                user_id = row[0]

        #process the change-------------------------------------------------------------------------
        data = (user_id,)
        sql = 'delete from user where id = ?'
        if self.db_update(sql, data) == 0:
            print('USER ' + user_code + ' SUCCESSFULLY DELETED')
        return

    

    def Z028_sign_on(self):
        """asks for the sign-on details for a user.  allows for three attempts before abandoning.
        note that the three attempts are not shared across user or time sessions so multiple
        attempts are supported.  as this doesn't have to be a secure system that's good enough.
        there is a readily available userid and password - XUSERX and XPASSX
        """
        tries = 0

        #allows three attempts
        while tries < 4:
            tries = tries + 1
            user = raw_input('ENTER USER ID: ') #deprecated in Python 3, change to input()
            user = str.upper(user)
            password  = raw_input('ENTER PASSWORD: ') #deprecated
            if password == '':
                password = 'XWRONGX'
            password = str.upper(password)
            password = password.strip()
            encrypted = self.encrypt(password)

            #check whether default ids being used
            if (user == 'XUSERX') and (password == 'XPASSX'):
                print('* WARNING - DEFAULT USER ID BEING USED')
                return 'DEFAULT', 'S'
            else:
                #normal user id and password
                t = (user,)
                count = 0
                try:
                    cxn1 = sqlite3.connect(self.directory + 'mops.db')
                    c1 = cxn1.cursor()
                    c1.execute('select * from user where user = ?', t)
                except:
                    print('* FAILED TO OBTAIN DATA FOR VALIDATION * <=========== 001')
                    return '********', 'R'
                for row in c1:
                    count = count + 1
                    user_code     = row[1]
                    user_passcode = row[3]
                    user_type     = row[4]
                    user_disabled = row[6]
                    user_new_user = row[7]
                c1.close()
                cxn1.close()
                if count == 1 and user_passcode == encrypted:

                    if user_disabled == 'Y':
                        print('* YOUR USER ID IS DISABLED - CONTACT YOUR SYSTEM ADMINISTRATOR')
                        return '********', '*'

                    if user_new_user == 'Y':
                        self.chpass(user)

                    values = ('Y', 'N', user_code)

                    if self.db_update('update user set is_signed_on = ?, ' +\
                                      'get_new_password = ? where user = ?', values) != 0:
                        return '********', '*'
                    return user_code, user_type
                else:
                    print('ID OR PASSWORD NOT RECOGNISED')
        print('* INVALID USER ID OR PASSWORD')
        return '********', 'R'
        

        
    def Z029_sign_off (self):
        """signs off from the system - resets the signed-on flag on exit
        """
        if self.uid == 'DEFAULT':
            return
        data = ('N', self.uid)
        sql = 'update user set is_signed_on = ? where user = ?'
        self.db_update(sql, data)
        return
    


    def liuser(self, message):
        """displays user data to the screen.  passcodes are not shown (as they are encrypted
        anyway its not an issue).  prints in name order.
        """
        if self.show_access(message, 'LIUSER', 'S') != 0:
            return

        # build the column titles-------------------------------------------------------------------
        titles = 'USERID== NAME========================= TYP ACT DIS'

        # get the extract data----------------------------------------------------------------------
        sql = 'select user, name, user_type, is_signed_on, has_access_disabled ' +\
              'from user order by name'
        count, ds_users = self.db_read(sql, '')
        if count < 0:


            return

        #report the extracted data-------------------------------------------------------------------
        line_count = 0
        for row in ds_users:
            if line_count == 0:
                print(titles)
            print(self.x_field(row[0], 8) + " " +
                   self.x_field(row[1], 30) + " " +
                   self.x_field(row[2], 1, 'R') + " " +
                   self.x_field(row[3], 3, 'R') + " " +
                   self.x_field(row[4], 3, 'R'))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def pruser(self, message, Params):
        """prints an extracted output to a report.  Passcodes are not shown.  Prints in name order.
        """
        if self.show_access(message, 'PRUSER', 'S') != 0:
            return

        # build the column titles-------------------------------------------------------------------
        titles = 'USERID== NAME========================= TYP ACT DIS'

        # get the extract data----------------------------------------------------------------------
        sql = 'select user, name, user_type, is_signed_on, has_access_disabled ' +\
              'from user order by name'
        count, ds_users = self.db_read(sql, '')
        if count < 0:
            return

        #build the extracted data-------------------------------------------------------------------
        self.temp = {}
        for row in ds_users:
            print_line = (self.x_field(row[0], 8) + ' ' +\
                   self.x_field(row[1], 30) + ' ' +\
                   self.x_field(row[2], 1, 'R') + ' ' +\
                   self.x_field(row[3], 3, 'R') + ' ' +\
                   self.x_field(row[4], 3, 'R'))
            self.temp[row[0]] = print_line

        #report the extracted data------------------------------------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRUSER',
                           report_name = 'LIST OF USERS IN NAME ORDER',
                           Params = Params)
        return     


        
    def encrypt(self, password):
        """one-way encryption of a password.  The encryption is made by accumulating the
        ordinance values of the individual characters in the password.
        """
        i = 0
        j = 0
        while i < len(password):
            j = j + ord(password[i]) * i
            i = i + 1
        s_j = str(j)
        return s_j
