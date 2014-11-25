'''
Param class: handles all the parameters for MOPS

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1   Removed unused variables
            Added new parameter DIRECTION that contains default direction for railroad
            Added new parameter PASSENGER to hold passenger car class code
            Added new parameter to control TRIMOPS output
'''

import time
import MOPS_Element

class cParams(MOPS_Element.cElement):
    """holds general parameter info for layout on a key/value table.  key is the parameter name,
    the value is held in the string.  
    """
    extract_code   = 'select * from parameter'
    extract_header = 'id|name|value\n'

    

    def __init__(self, uid, access, directory):
        """carry out some initiation; these values will be required all the time. loaded to override
        default init processing as a lot of the data isn't available and isnt required in any event
        """
        self.uid       = uid
        self.access    = access
        self.directory = directory
        self.rr        = 'PARAMETERS'
        return


    def update_param(self, param, value):
        """generic routine for setting a parameter value.  if the parameter value
        is not on the file then it will create it with the given value.
        """
        #get current value for the parameter; we need to know if we are overriding or creating
        data = (param,)
        sql = 'select value from parameter where name = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return 99

        #either insert a new record or update an existing one
        if count == 0:
            data = (param, value)
            sql = 'insert into parameter values (null, ?, ?)'
            if self.db_update(sql, data) != 0:
                return 99
        else:
            data = (value, param)
            sql = 'update parameter set value = ? where name = ?'
            if self.db_update(sql, data) != 0:
                return 99
        return 0



    def start_mops(self):
        """changes the status of mops to started.  mops is started from a stand-alone session
        but can be stopped by any supervisor.
        """
        rc = self.update_param('STATUS', 'STARTED')
        if rc == 0:
            print('>>> MOPS BACKGROUND PROCESSES STARTED <<<')
        else:
            print('*** ERROR STARTING MOPS BACKGROUND TASKS ***')
        return self.get_mops_status()

        
        
    def xxstop(self):
        """Changes the status of mops to stopped.  This will stop the background task if it is
        running.  can be set by any supervisor
        """
        if self.show_access('', 'XXSTOP', 'S') != 0:
            return

        rc = self.update_param('STATUS', 'STOPPED')
        if rc == 0:
            print('>>> MOPS BACKGROUND PROCESSES STOPPED <<<')
        else:
            print('*** ERROR STOPPING MOPS BACKGROUND TASKS ***')
        return

                
        
    def get_mops_status(self):
        """Gets the mops status from the Data Dictionary.  Status is either
        STOPPED or STARTED, defaults to STOPPED if no record
        """
        mops_status = self.get_param_value('STATUS', 'STOPPED')
        return mops_status
    

    
    def chparm(self, message):
        """Allows users access to change parameter values on the system by quoting the
        relevant parameter and the required value.
        """
        if self.show_access(message, 'CHPARM {PARAMETER};VALUE', 'S') != 0:
            return

        errors = 0
        
        #parameter name-----------------------------------------------------------------------------
        parameter, rc = self.extract_field(message, 0, 'NAME OF PARAMETER')
        if rc > 0:
            return

        #parameter value----------------------------------------------------------------------------
        param_value, rc = self.extract_field(message, 1, 'PARAMETER VALUE')
        if rc > 0:
            return

        if len(param_value) == 0:
            print('* NO PARAMETER VALUE PROVIDED FOR PARAMETER CHANGE')
            errors = errors + 1

        #validate-----------------------------------------------------------------------------------
        if errors > 0:
            return

        size_check   = True
        car_defaults = False
        param_name = parameter
        if parameter == 'RRNAME':
            param_name = 'RAILROAD NAME'
            size_check = False
        elif parameter == 'DIRECTION':                           #Rev 1
            param_name = 'PRIORITY DIRECTION'                    #Rev 1
            size_check = False                                   #Rev 1
        elif parameter == 'PASSENGER':                           #Rev 1
            param_name = 'PASSENGER CAR CLASS'                   #Rev 1
            size_check = False                                   #Rev 1
        elif parameter == 'TRIMOPS':                             #Rev 1
            param_name = 'TRIMOPS OUTPUT'                        #Rev 1
            size_check = False                                   #Rev 1
        elif parameter == 'STATSIZE':
            param_name = 'STATION TYPE CODE SIZE'
        elif parameter == 'RAILSIZE':
            param_name = 'RAILROAD CODE SIZE'
        elif parameter == 'STAXSIZE':
            param_name = 'STATION CODE SIZE'
        elif parameter == 'PLAXSIZE':
            param_name = 'PLACE CODE SIZE'
        elif parameter == 'AREASIZE':
            param_name = 'AREA CODE SIZE'
        elif parameter == 'LOADSIZE':
            param_name = 'LOADING CODE SIZE'
        elif parameter == 'COMMSIZE':
            param_name = 'COMMODITY CODE SIZE'
        elif parameter == 'LOCTSIZE':
            param_name = 'LOCOMOTIVE TYPE CODE SIZE'
        elif parameter == 'LOCOSIZE':
            param_name = 'LOCOMOTIVE CODE SIZE'
        elif parameter == 'CLASSIZE':
            param_name = 'CAR CLASS CODE SIZE'
        elif parameter == 'CARTSIZE':
            param_name = 'CAR TYPE TYPE CODE SIZE'
        elif parameter == 'CARXSIZE':
            param_name = 'CAR CODE SIZE'
        elif parameter == 'TRANSIZE':
            param_name = 'TRAIN CODE SIZE'
        elif parameter == 'CUROSIZE':
            param_name = 'CUSTOMER ROUTING CODE SIZE'
        elif parameter == 'ROUTSIZE':
            param_name = 'ROUTE CODE SIZE'
        elif parameter == 'SCHDSIZE':
            param_name = 'SCHEDULE CODE SIZE'
        elif parameter == 'CARMAINT':
            param_name = 'CAR MAINTENANCE INTERVAL'
            car_defaults = True
        elif parameter == 'CARWORKS':
            param_name = 'CAR MAINTENANCE TIME'
            car_defaults = True
        else:
            print('* PARAMETER ', parameter, ' NOT IDENTIFIED FOR UPDATE')
            return

        #carry out validation-----------------------------------------------------------------------
        if car_defaults:
            try:
                dummy = int(param_value)
            except:
                print('* PARAMETER MUST BE NUMERIC')
                return
            if int(param_value) < 1 or int(param_value) > 1000:
                print('*' + param_name + ' MUST HAVE A VALUE BETWEEN 1 AND 1000')
                return
        else:
            if size_check:
                try:
                    dummy = int(param_value)
                except:
                    print('* PARAMETER MUST BE NUMERIC')
                    return
                if int(param_value) < 1 or int(param_value) > 10:
                    print('*' + param_name + ' MUST HAVE A VALUE BETWEEN 1 AND 10')
                    return
        if parameter == 'DIRECTION':                                            #Rev 1
            if not (param_value == 'N' or param_value == 'S' or param_value == 'E' or param_value == 'W' or param_value == 'U' or param_value == 'D'):
                print('* DIRECTION PARAMETER MUST BE N, S, E, W, U OR D')
                return
            
        #carry out the parameter update-------------------------------------------------------------
        if self.update_param(parameter, param_value) > 0:
            return

        print(param_name + ' (' + parameter + ') CHANGED TO ' + param_value)
        return

        

    def get_field_size(self, param_name):
        """gets the value for the indicated parameter value field (for setting size of a code field)
        """
        size = 1
        data = (param_name,)
        sql = 'select value from parameter where name = ?'
        count, ds_param = self.db_read(sql, data)

        if count < 0:
            return -1

        for row in ds_param:
            size = int(row[0])
        return size



    def get_rr_name(self):
        """gets the value for the railroad name
        """
        name = self.get_param_value('RRNAME', 'NOT FOUND')
        return name



    def liparm(self, message):
        """Displays parameter values to the screen.  listed in parameter name order.
        """
        if self.show_access(message, 'LIPARM', 'R') != 0:
            return
        
        # build the column titles-------------------------------------------------------------------
        titles = ('PARAM=====   DATA=====================================================')

        # get the extract data----------------------------------------------------------------------
        sql='select name, value from parameter order by name'
        count, ds_params = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data-------------------------------------------------------------------
        line_count = 0
        for row in ds_params:
            if line_count == 0:
                print(titles)
            print(self.x_field(row[0], 12) + " " +
                   self.x_field(row[1], 30))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return
                   


    def prparm(self, message, Params):
        """Prints parameter values to a report.  Listed in parameter name order.
        """
        if self.show_access(message, 'PRPARM', 'R') != 0:
            return
        
        # build the column titles-------------------------------------------------------------------
        titles = ('PARAM=====   DATA=====================================================')

        # get the extract data----------------------------------------------------------------------
        sql = 'select name, value from parameter order by name'
        count, ds_params = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data------------------------------------------------------------------
        self.temp = {}
                   
        for row in ds_params:
            print_line = (self.x_field(row[0], 12) + ' ' +\
                          self.x_field(row[1], 30))
            self.temp[row[0]] = print_line

        #report the extracted data------------------------------------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRPARM',
                           report_name = 'LIST OF PARAMETERS',
                           Params = Params)
        return     



    def get_inc(self, counter):
        """increments a counter held against the <counter> reference on the Params file and returns
        the number.  If the <counter> does not exist it creates it and returns 1.
        """
        inc_s = self.get_param_value(counter, '0')
        inc = int(inc_s)
        inc = inc + 1
        inc_s = str(inc)
        self.update_param(counter, inc_s)
        return inc_s



    def settim(self, message):
        """stores the indicated time and date on the parameter file as
        DDmmmYYYY HH:MM:SS DOW.  The time is validated for value, and teh date and day
        of week is validated against the database file for accuracy.  this ensures that
        data is kept constant when being amended.
        """
        if self.show_access(message, 'SETTIM ddmmmyy hh:mm:ss dow', 'S') != 0:
            return

        dd = message[0:2]
        mm = message[2:5]
        yy = message[5:9]
        hh = message[10:12]
        ii = message[13:15]
        ss = message[16:18]
        dow = message[19:22]

        try:
            sss = int(ss)
        except:
            sss = -1            
        if sss < 0 or sss > 59:
            print('INVALID SECONDS VALUE ENTERED: MUST BE 00-59')
            return

        try:
            iii = int(ii)
        except:
            iii = -1            
        if iii < 0 or iii > 59:
            print('INVALID MINUTES VALUE ENTERED: MUST BE 00-59')
            return

        try:
            ihh = int(hh)
        except:
            ihh = -1
        if ihh < 0 or ihh > 23:
            print('INVALID HOURS VALUE ENTERED: MUST BE 00-23')
            return

        data = (dd, mm, yy)
        sql = 'select dow, id from calendar where day = ? and month = ? and year = ?'
        count, ds_dates = self.db_read(sql, data)

        if count == 0:
            print('* DATE DOES NOT EXIST ON DATABASE: CHECK DATA OR GENERATE NEW DATES')
            return

        for row in ds_dates:
            if dow != row[0]:
                print('* DAY OF WEEK IN ERROR: SHOWN AS ' + row[0] + ' IN DATABASE')
                return
            new_id = row[1]

        #reset the current date marker for the the current date
        data = ('X', 'C')
        sql = 'update calendar set current = ? where current = ?'
        if self.db_update(sql, data) != 0:
            return

        #mark the new day as current
        data = ('C', new_id)
        sql = 'update calendar set current = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        if self.update_param('DATETIME', message) == 0:
            print('SYSTEM DATE CHANGED TO: ' + message)
        else:
            print('FAILED TO CREATE DATE/TIME RECORD ON DATABASE * <===========')
        return



    def cspeed (self, message):
        """sets the clock speed for the application background task
        """
        if self.show_access(message, 'CSPEED speed', 'S') != 0:
            return

        try:
            cspeed = int(message)
        except:
            cspeed = -1
        if cspeed < 1 or cspeed > 12:
            print('Clock speed must be between 1 and 12')
            return

        if self.update_param('CSPEED', str(cspeed)) == 0:
            print('CLOCK SPEED CHANGED TO ' + str(cspeed) + ' TIMES NORMAL')
        else:
            print('FAILED TO CREATE TIME SPEED RECORD ON DATABASE * <===========')
        return



    def Z000_clock_advance (self):
        """moves the time on by 5 seconds, multiplied by the cspeed amount
        """
        datetime = self.get_param_value('DATETIME', '01JAN2009 12:00:00 THU')
        cspeed = int((self.get_param_value('CSPEED', 1)))

        dd = datetime[0:2]
        mm = datetime[2:5]
        yy = datetime[5:9]
        hh = datetime[10:12]
        ii = datetime[13:15]
        ss = datetime[16:18]
        day = datetime[19:22]
        eventflag = 'none'


        try:
            sss = int(ss)
            iii = int(ii)
            hhh = int(hh)
        except:
            print('* NO CURRENT DATE SET ON SYSTEM')
            return
        
        sss = sss + (cspeed * 5)
        if sss > 59:
            eventflag = 'minute'
            sss = sss - 60
            iii = iii + 1
            if iii > 59:
                eventflag = 'hour'
                iii = iii - 60
                hhh = hhh + 1
                if hhh > 23:
                    eventflag = 'day'
                    hhh = hhh - 24

                    #get the id for todays date
                    data = (dd, mm, yy)
                    sql = 'select id from calendar where day = ? and month = ? and year = ?'
                    count, ds_dates = self.db_read(sql, data)
                    if count < 0:
                        return
                    if count == 0:
                        print('* DATE DOES NOT EXIST ON DATABASE: CHECK DATA OR GENERATE NEW DATES')
                        return

                    for row in ds_dates:
                        db_id = row[0]

                    #mark today as completed
                    data = ('X', db_id)
                    sql = 'update calendar set current = ? where id = ?'
                    if self.db_update(sql, data) != 0:
                        return

                    #mark the next day as current
                    data = ('C', db_id + 1)
                    sql = 'update calendar set current = ? where id = ?'
                    if self.db_update(sql, data) != 0:
                        return
                    
                    #get data for the new day for storing on parameters
                    sql = 'select day, month, year, dow, holiday from calendar where id = ?'
                    data = (db_id +1,)
                    count, ds_dates = self.db_read(sql, data)
                    if count < 0:
                        return
                    for row in ds_dates:
                        dd  = row[0]
                        mm  = row[1]
                        yy  = row[2]
                        day = row[3]
                        hol = row[4]
                        if hol == 'Y':
                            day = 'HOL'

        ss = str(sss)
        ii = str(iii)
        hh = str(hhh)
        if len(ss) == 1:
            ss = '0' + ss
        if len(ii) == 1:
            ii = '0' + ii
        if len(hh) == 1:
            hh = '0' + hh
        new_datetime = dd + mm + yy + ' ' + hh + ':' + ii + ':' + ss + ' ' + day
        self.update_param('DATETIME', new_datetime)
        return eventflag



    def get_date(self):
        """returns the date from the parameter file
        """
        system_date = self.get_param_value('DATETIME', time.strftime('%d%b%Y'))
        system_date = system_date[0:9]
        return system_date



    def get_day_of_week(self):
        """get the current day of the week
        """
        system_date = self.get_param_value('DATETIME', 'XXX')
        system_dow = system_date[19:22]
        return system_dow



    def get_time(self):
        """returns the time from the parameter file
        """
        system_time = self.get_param_value('DATETIME', time.strftime('%H:%M:%S'))
        if system_time != None:
            system_time = system_time[10:15]
        return system_time



    def get_param_value(self, param, default):
        """generic routine to return a parameter.  a default value is also provided
        in the event of no record being found (which is a warning condition
        """
        data = (param,)
        sql = 'select value from parameter where name = ?'
        count, ds_params = self.db_read(sql, data)
        if count < 0:
            return

        for row in ds_params:
            count = count + 1
            value = row[0]

        if count == 0:
            value = default
            if param != 'STATUS':
                self.chparm(str(param) + ';' + str(value))
            if param == 'STATUS':
                self.xxstop()                
        return value
        
