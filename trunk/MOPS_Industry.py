'''
Industry Class

Model Operations Processing System

Copyright Brian Fairbairn 2009  Licenced under the EUPL.  You may not use this
work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application
(see Licence file).  Unless required by applicable law or agreed to in writing,
software distributed under the Licence is distributed on an 'AS IS' basis
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied. See
the Licence governing permissions and limitations under the Licence.
'''

import re
import MOPS_Misc
import MOPS_Element



class cIndustries(MOPS_Element.cElement):
    """Details about Industries. 
    indy	     10 Reference for Industry
    industry_name    30 Name of Company
    place	     10 Place at which industry is located
    """

    info_dx = 'DXINDY code'
    info_li = 'LIINDY (sort)'
    info_pr = 'PRINDY (sort)'
    report_id = 'PRINDY'
    report_name = 'LIST OF INDUSTRIES'
    extract_code = 'select * from industry'
    extract_header = 'code|industry|station|place\n'
    


    def dxindy(self, message):
        """deletes an industry from the list.  checks that it is not on a train
        """
        if self.show_access(message, self.info_dx, 'S') != 0:
            return

        indy = message.strip()
        t = (indy,)

        #validate the change
        sql = 'select id from industry where indy = ?'
        count, data = self.db_read(sql, t, __name__)
        if count < 0:
            return
        if count == 0:
            print('* INDUSTRY CODE DOES NOT EXIST')
            return

        #process the change
        if self.update('delete from industry where indy = ?', t) == 0:
            print('INDUSTRY' + indy + 'SUCCESSFULLY DELETED')
        return



    def get_print_titles(self):
        """returns the appropriate titles for the default print
        """
        indy_title = 'INDUSTRY=='
        name_title = 'NAME=========================='
        place_title = 'PLACE====================================='
        indy_title = indy_title.ljust(self.indysize)[:self.indysize]
        name_title = name_title.ljust(30)[:30]
        place_title = place_title.ljust(38)[:38]

        titles =    indy_title    + ' ' +         \
                    name_title    + ' ' +         \
                    place_title 
        return titles



    def build_list(self, message, offset, style):
        """xtracts and sorts a list of industries
        """
        self.temp.clear()
        sort_order = message.strip()
        sql = 'select place.stax, place.plax, place.place_name, industry.indy, industry.industry_name, industry.place_id '  +\
              'from place, industry where place.id = industry.place_id' 
        t = ()
        data = ()
        count, data = self.db_read(sql, t, __name__)
        if count < 0:
            return

        for row in data:
            stax = row[0].ljust(self.staxsize)[:self.staxsize]
            plax = row[1].ljust(self.plaxsize)[:self.plaxsize]
            placename = row[2]
            indy = row[3].ljust(self.indysize)[:self.indysize]
            industry_name = row[4].ljust(30)[:30]
            place_id = row[5]
            the_place = stax + ' ' + plax + ' (' + str(place_id) + ') ' + placename
            the_place = the_place.ljust(38)[:38]
            print_string = offset +                 \
                           indy           + ' ' +   \
                           industry_name  + ' ' +   \
                           the_place   
            if sort_order == '1':
                self.temp[industry_name + indy] = print_string
            else:
                self.temp[indy] = print_string
        return self.temp      


        
    def break_message(self, message, change_mode):
        """breaks the input message into the constituent parts and validates.  Used
        for both the new and changed process as the validation is common. The data
        is loaded into object variables.  If this is a change message and the data
        is not supplied for a field then it will be replaced by the current value
        """
        errors = 0

        #industry  ------------------------------------------------------------
        rc, value = MOPS_Misc.format_data(raw_data = message,
                                      position = 0,
                                      size = self.indysize,
                                      mode = change_mode,
                                      original_value = '')
        if rc != 0:
            errors = errors + 1
            print('* CANNOT DETERMINE INDUSTRY CODE - CHECK DATA AND DELIMITERS')
        if value.strip() == '':
            errors = errors + 1
            print('* CANNOT DETERMINE INDUSTRY CODE - CODE CANNOT BE BLANK')

        #read the database and populate the fields
        indy = ''
        industry_name = ''
        place_name = ''
        place_id = 0
        plax = ''
        stax = ''

        t = (value,)
        sql = 'select * from industry where indy = ?'
        count, data = self.db_read(sql, t, __name__)
        if count < 0:
            return
        for row in data:
            industry_name = row[2]
            place_id = row[3]

        if change_mode == 'change' and count ==0:
            print('* INDUSTRY CODE DOES NOT EXIST FOR CHANGE')
            errors = errors + 1
        if change_mode == 'new' and count != 0:
            print('* INDUSTRY CODE ALREADY EXISTS')
            errors = errors + 1

        if errors == 0:
            indy = value

        #name -------------------------------------------------------------
        rc, value = MOPS_Misc.format_data(raw_data = message,
                                      position = 1,
                                      size = 30,
                                      mode = change_mode,
                                      original_value = industry_name)
        if rc != 0:
            errors = errors + 1
            print('* CANNOT DETERMINE INDUSTRY NAME - CHECK DATA AND DELIMITERS')
        if errors == 0:
            industry_name = value

        #place -------------------------------------------------------------
        rc, value = MOPS_Misc.format_data(raw_data = message,
                                      position = 2,
                                      size = self.plaxsize,
                                      mode = change_mode,
                                      original_value = place_id)
        if rc != 0:
            errors = errors + 1
            print('* CANNOT DETERMINE PLACE CODE - CHECK DATA AND DELIMITERS')

        t = (value,)
        data = ()
        sql = 'select id, place_name, stax, plax from place where id = ?'
        count, data = self.db_read(sql, t, __name__)
        if count < 0:
            return

        if count == 0:
            print('* PLACE DOES NOT EXIST')
            errors = errors + 1
        else:    
            for row in data:
                place_name = row[1]
                stax = row[2]
                plax = row[3]
            
        if errors == 0:
            place_id = value

        #carry out the update --------------------------------------------------
        if errors != 0:
            return

        if change_mode == 'new':
            title = 'NEW INDUSTRY ADDED SUCCESSFULLY'
            t = (indy, industry_name, place_id)
            sql = 'insert into industry values (null, ?, ?, ?)'
        if change_mode == 'change':
            title = 'INDUSTRY CHANGED SUCCESSFULLY'
            t = (industry_name, place_id, indy)
            sql = 'update industry set industry_name = ?, place_id = ? where indy = ?'

        if self.update(sql, t) != 0:
            return

        #report the change to the screen =========================================
        print(title)
        print(indy + industry_name)
        print('AT:' + stax + plax + place_name + '(PLACE ID: ' + place_id + ')')
        return
            
        return errors
