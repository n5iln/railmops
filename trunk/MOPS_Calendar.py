'''
Calendar Class - accesses system calendar

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.
'''
import MOPS_Element

class cCalendars(MOPS_Element.cElement):
    """details about calendars.  calendars are held in five-year chunks on the database and can be
    created by the user.  also holds a current day marker (current date is reflected on the
    parameter file).  also holds a holiday marker.  day of week is required to match up with the
    weekly timetables.
    """
    extract_code = 'select * from calendar limit 100'
    extract_header = 'id|day|month|year|holiday|current date|day of week'



    def holidx(self, message):
        """sets the given day to be a holiday.  Command acts as a tag, setting and unsetting the
        holiday marker flag
        """
        if self.show_access(message, 'HOLIDX day;month;year', 'S') != 0:
            return

        #day----------------------------------------------------------------------------------------
        day, rc = self.extract_field(message, 0, 'DAY')
        if rc > 0:
            return
            
        #month---------------------------------------------------------------------------------------
        month, rc = self.extract_field(message, 1, 'MONTH')
        if rc > 0:
            return

        #year---------------------------------------------------------------------------------------
        year, rc = self.extract_field(message, 2, 'YEAR')
        if rc > 0:
            return

        #get the date on the database and see if it is a holiday------------------------------------
        data = (day, month, year)
        sql = 'select id, holiday from calendar where day = ? and month = ? and year = ?'
        count, ds_dates = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* DATE DOES NOT EXIST ON DATABASE')
            return

        #swap holiday/non-holiday status------------------------------------------------------------
        for row in ds_dates:
            if row[1] == 'YES':
                marker = ''
            else:
                marker = 'YES'
            date_id = row[0]

        #update the database with the new status-----------------------------------------------------
        data = (marker, date_id)
        sql = 'update calendar set holiday = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        if marker == 'YES':
            print('HOLIDAY SET FOR ' + day + month + year)
        else:
            print('HOLIDAY CANCELLED FOR ' + day + month + year)
        return



    def licalx(self, message):
        """this generates a list showing the next 10 days, starting from the current date
        """
        if self.show_access(message, 'LICALX', 'R') != 0:
            return

        #find todays date from the calendar----------------------------------------------------------
        data = ('C',)
        sql = 'select id from calendar where current = ?'
        count, ds_dates = self.db_read(sql, data)
        if count < 0:
            return

        for row in ds_dates:
            start_id = row[0]

        #read the next ten days and show to the screen----------------------------------------------
        start_id = start_id - 1
        data = (start_id,)
        sql = 'select day, month, year, holiday, dow from calendar ' +\
              'where id > ? order by id limit 10'
        count, ds_dates = self.db_read(sql, data)
        if count < 0:
            return

        print('DAY DATE======= HOL')
        for row in ds_dates:
            print(row[4] + ' ' +row[0] + row[1] + row[2] + ' ' + row[3])
        return        
