'''
Flash Class An alert going to users

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.
'''

import MOPS_Element


class cFlashes(MOPS_Element.cElement):
    """flashes are messages that are either generated manually or created automatically by the
    system.  when a message is generated, a copy is created for each user, and displayed to
    each user at the first available opportunity.  flashes not read within a given (system)
    timescale are automatically deleted
    """



    def flashx(self, message, Params):
        """create manual flash messages.  uses the generic flash generation process
        """
        if self.show_access(message, 'FLASHX message', 'R') != 0:
            return

        message = message + '  ' + Params.get_date() + ' AT ' + Params.get_time() + ' BY ' +\
                  self.uid.strip()
        self.Z003_generate_flash_message(message, Params)

        print('FLASH MESSAGE SENT TO ALL USERS:')
        print(message.strip()) 
        return

    
    def Z003_generate_flash_message(self, message, Params):
        """creates a new flash status message and stores a new message for each user on the
        database.  Each record is stored with a 24-hour countdown timer.
        """
        flashid = Params.get_inc('FLASHID')
        message = message.ljust(250)[:250]
        message = message.strip()

        sql = 'select user from user'
        count, ds_users = self.db_read(sql, '')
        if count < 0:
            return
        
        for row in ds_users:
            user_code = row[0]
            data = (flashid, message, user_code, 24)
            sql = 'insert into flash values (null, ?, ?, ?, ?)'
            if self.db_update(sql, data) != 0:
                return
        return



    def Z004_check_flash_required(self):
        """check whether a flash is required to be displayed to a user.  This is called from the
        control routine on a message-by -message basis
        """
        #--------------------------------------------------------------------------------------------
        #get the message for the given user and load into an array
        t = (self.uid,)
        sql = 'select message, id from flash where user = ? and timer > 0'
        count, ds_flashes = self.db_read(sql, t)
        if count < 0:
            return

        #--------------------------------------------------------------------------------------------
        #display the message and delete when shown (just delete all for the user)
        for row in ds_flashes:
            print(row[0])

        sql = 'delete from flash where user = ? and timer > 0'
        t = (self.uid,)
        self.db_update(sql, t)
        return 



    def Z006_expire_flash_messages(self):
        """run down the timer on the messages.  if they reach zero, remove them
        """
        sql = 'update flash set timer = timer - 1'
        if self.db_update(sql, '') != 0:
            return
        
        sql = 'delete from flash where timer < 0'
        if self.db_update(sql, '') != 0:
            return
        return

