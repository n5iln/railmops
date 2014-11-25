'''
Loco Type Class.
Models or Types of Locomotives, identifying their name and characteristics of
the model type

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Removed unused variables
'''

import MOPS_Element


class cLocoTypes(MOPS_Element.cElement):
    """details about locomotive types.  locomotives are linked to locomotive types.  locomotives
    will be either Electric, Diesel, Steam or Other.  Locomotives can operate Independently,
    as a dummy/slave (ie cannot operate on its own), as the power car in a Multiple Unit or Other.
    """
    extract_code = 'select * from locotype'
    extract_header = 'id|code|name|type|haulage|fuel capacity|fuel rate|maint interval|' +\
                     'maint outage|loco weight|loco length|oper mode\n'



    def adloct(self, message):
        """Add Locomotive Type.  Include a name for the power type, type (Diesel, Steam, Electric,
        or Other).  Add haulage capability, fuel capacity, fuel rate when running, maint interval,
        time in works, loco weight and length and operating mode (Independent, Slave, Multiple Unit
        or Other).
        """
        if self.show_access(message,
                            'ADLOCT loco type;name;power type[D/S/E/O];haulage;fuel capacity;fuel rate;' +\
                            'maint interval;works time;weight;length;oper mode[I/S/M/O]',
                            'S') != 0:
            return
        errors = 0

        #locomotive type code-----------------------------------------------------------------------
        loco_type, rc = self.extract_field(message, 0, 'LOCOMOTIVE TYPE CODE')
        if rc > 0:
            return

        if len(loco_type) > self.loctsize:
            print('* LOCOMOTIVE TYPE CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(loco_type) ==0:
            print('* NO LOCOMOTIVE TYPE CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return
        
        #check it does not already exist on the database
        data = (loco_type,)
        sql = 'select id from locotype where locotype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* LOCOMOTIVE TYPE CODE ALREADY EXISTS')
            return

        #loco type name-----------------------------------------------------------------------------
        loco_type_name, rc = self.extract_field(message, 1, 'LOCOMOTIVE TYPE NAME')
        if rc > 0:
            return

        #loco power type----------------------------------------------------------------------------
        power_type, rc = self.extract_field(message, 2, 'POWER TYPE')
        if rc > 0:
            return
            
        if not(power_type == 'D' or power_type == 'S' or power_type == 'E' or power_type == 'O'):
            errors = errors + 1
            print('* POWER MUST BE D-DIESEL E-ELECTRIC S-STEAM O-OTHER')

        #haulage------------------------------------------------------------------------------------
        haulage, rc = self.extract_field(message, 3, 'HAULAGE VALUE')
        if rc > 0:
            return

        try:
            if int(haulage) > 99999 or int(haulage) < 0:
                errors = errors + 1
                print('* HAULAGE VALUE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* HAULAGE VALUE MUST BE A WHOLE NUMBER')

        #fuel capacity------------------------------------------------------------------------------
        fuel_capacity, rc = self.extract_field(message, 4, 'FUEL CAPACITY VALUE')
        if rc > 1: 
            return

        if power_type == 'E':
            fuel_capacity = '99999'
            
        try:
            if int(fuel_capacity) > 99999 or int(fuel_capacity) < 0:
                errors = errors + 1
                print('* FUEL CAPACITY VALUE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* FUEL CAPACITY VALUE MUST BE A WHOLE NUMBER')

        #fuel rate----------------------------------------------------------------------------------
        fuel_rate, rc = self.extract_field(message, 5, 'FUEL RATE VALUE')
        if rc > 1:
            return

        if power_type == 'E':
            fuel_rate = '0'
            
        try:
            if int(fuel_rate) > 99999 or int(fuel_rate) < 0:
                errors = errors + 1
                print('* FUEL RATE VALUE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* FUEL RATE VALUE MUST BE A WHOLE NUMBER')

        #maint interval-----------------------------------------------------------------------------
        maint_outage, rc = self.extract_field(message, 6, 'MAINTENANCE INTERVAL')
        if rc > 0:
            return

        try:
            if int(maint_outage) > 99999 or int(maint_outage) < 0:
                errors = errors + 1
                print('* MAINTENANCE INTERVAL MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* MAINTENANCE INTERVAL MUST BE A WHOLE NUMBER')

        #maint outage-------------------------------------------------------------------------------
        works_time, rc = self.extract_field(message, 7, 'TIME IN WORKS')
        if rc > 0:
            return

        try:
            if int(works_time) > 99999 or int(works_time) < 0:
                errors = errors + 1
                print('* MAINTENANCE OUTAGE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* MAINTENANCE OUTAGE MUST BE A WHOLE NUMBER')

        #weight of loco-----------------------------------------------------------------------------
        weight, rc = self.extract_field(message, 8, 'WEIGHT OF LOCO')
        if rc > 0:
            return

        try:
            if int(weight) > 99999 or int(weight) < 0:
                errors = errors + 1
                print('* WEIGHT OF LOCO MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* WEIGHT OF LOCO MUST BE A WHOLE NUMBER')

        #length-------------------------------------------------------------------------------------
        length, rc = self.extract_field(message, 9, 'LOCOMOTIVE LENGTH')
        if rc > 0:
            return

        try:
            if int(length) > 99999 or int(length) < 0:
                errors = errors + 1
                print('* LOCOMOTIVE LENGTH MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* LOCOMOTIVE LENGTH MUST BE A WHOLE NUMBER')

        #loco power type----------------------------------------------------------------------------
        loco_oper_mode, rc = self.extract_field(message, 10, 'LOCOMOTIVE OPERATING MODE')
        if rc > 0:
            return
        
        if not(loco_oper_mode == 'I' or loco_oper_mode == 'S' or loco_oper_mode == 'M' or loco_oper_mode == 'O'):
            errors = errors + 1
            print('* OPERATING MODE MUST BE I-INDEPENDENT S-SLAVE M-MULTIPLE UNIT O-OTHER')

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (loco_type, loco_type_name, power_type, haulage, fuel_capacity, fuel_rate,
             maint_outage, works_time, weight, length, loco_oper_mode)
        sql = 'insert into locotype values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        power_desc, oper_desc = self.get_power_desc(power_type, loco_oper_mode)
        print('NEW LOCOMOTIVE TYPE ADDED SUCCESSFULLY')
        print('LOCOMOTIVE TYPE:' + loco_type + loco_type_name + power_desc)
        print('HAUL:' + str(haulage) + ' WT:' + str(weight) + 'LGTH:' + str(length) +
               'FUEL CAP:' + str(fuel_capacity) + 'RATE:' + str(fuel_rate))	   
        print('MAINT INTERVAL:' + str(maint_outage) + 'WORKS TIME:' + str(works_time) +
               '(' + oper_desc + ')')  
        return



    def chloct(self, message):
        """Change Locomotive Type, including type name, type (Diesel, Steam, Electric,
        or Other), haulage capability, fuel capacity, fuel rate when running, maint interval,
        time in works, loco weight and length and operating mode (Independent, Slave, Multiple Unit
        or Other).
        """
        if self.show_access(message,
                            'CHLOCT loco type;(name);(power type[D/S/E/O]);(haulage);(fuel capacity);(fuel rate);' +\
                            '(maint interval);(works time);(weight);(length);(oper mode[I/S/M/O])',
                            'S') != 0:
            return
        errors = 0

        #locomotive type code-----------------------------------------------------------------------
        loco_type, rc = self.extract_field(message, 0, 'LOCOMOTIVE TYPE CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (loco_type,)
        sql = 'select name, power_type, haulage, fuel_capacity, fuel_rate, ' +\
              'maint_interval, works_time, weight, length, oper_mode ' +\
              'from locotype where locotype = ?'
        count, ds_loco_types = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOCOMOTIVE TYPE CODE DOES NOT EXIST')
            return

        for row in ds_loco_types:
            loco_type_name  = row[0] 
            power_type      = row[1]
            haulage         = row[2]
            fuel_capacity   = row[3]
            fuel_rate       = row[4]
            maint_outage    = row[5]
            works_time      = row[6]
            weight          = row[7]
            length          = row[8]
            loco_oper_mode  = row[9]

        #loco type name-----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            loco_type_name = value

        #loco power type----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            power_type = value
        
        if not(power_type == 'D' or power_type == 'S' or power_type == 'E' or power_type == 'O'):
            errors = errors + 1
            print('* POWER MUST BE D-DIESEL E-ELECTRIC S-STEAM O-OTHER')

        #haulage------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            haulage = value

        try:
            if int(haulage) > 99999 or int(haulage) < 0:
                errors = errors + 1
                print('* HAULAGE VALUE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* HAULAGE VALUE MUST BE A WHOLE NUMBER')

        #fuel capacity------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 4, '')
        if rc == 0:
            fuel_capacity = value

        if power_type == 'E':
            fuel_capacity = '99999'

        try:
            if int(fuel_capacity) > 99999 or int(fuel_capacity) < 0:
                errors = errors + 1
                print('* FUEL CAPACITY VALUE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* FUEL CAPACITY VALUE MUST BE A WHOLE NUMBER')

        #fuel rate----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 5, '')
        if rc == 0:
            fuel_rate = value

        if power_type == 'E':
            fuel_rate = '0'

        try:
            if int(fuel_rate) > 99999 or int(fuel_rate) < 0:
                errors = errors + 1
                print('* FUEL RATE VALUE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* FUEL RATE VALUE MUST BE A WHOLE NUMBER')

        #maint interval-----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 6, '')
        if rc == 0:
            maint_outage = value

        try:
            if int(maint_outage) > 99999 or int(maint_outage) < 0:
                errors = errors + 1
                print('* MAINTENANCE INTERVAL MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* MAINTENANCE INTERVAL MUST BE A WHOLE NUMBER')

        #maint outage-------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 7, '')
        if rc == 0:
            works_time = value

        try:
            if int(works_time) > 99999 or int(works_time) < 0:
                errors = errors + 1
                print('* TIME IN WORKS MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* TIME IN WORKS MUST BE A WHOLE NUMBER')

        #weight of loco-----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 8, '')
        if rc == 0:
            maint_outage = value

        try:
            if int(maint_outage) > 99999 or int(maint_outage) < 0:
                errors = errors + 1
                print('* DETERMINE WEIGHT OF LOCO MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* DETERMINE WEIGHT OF LOCO MUST BE A WHOLE NUMBER')

        #length-------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 9, '')
        if rc == 0:
            length = value

        try:
            if int(length) > 99999 or int(length) < 0:
                errors = errors + 1
                print('* LOCOMOTIVE LENGTH MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* LOCOMOTIVE LENGTH MUST BE A WHOLE NUMBER')

        #loco power type----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 10, '')
        if rc == 0:
            loco_oper_mode = value
        
        if not(loco_oper_mode == 'I' or loco_oper_mode == 'S' or loco_oper_mode == 'M' or loco_oper_mode == 'O'):
            errors = errors + 1
            print('* OPERATING MODE MUST BE I-INDEPENDENT S-SLAVE M-MULTIPLE UNIT O-OTHER')

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (loco_type_name, power_type, haulage, fuel_capacity,fuel_rate, maint_outage,
                works_time, weight, length, loco_oper_mode, loco_type)
        sql = 'update locotype set name = ?, power_type = ?, haulage = ?, ' + \
              'fuel_capacity = ?, fuel_rate = ?, maint_interval = ?, works_time = ?, ' +\
              'weight = ?, length = ?, oper_mode = ? where locotype = ?'

        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        power_desc, oper_desc = self.get_power_desc(power_type, loco_oper_mode)
        print('LOCOMOTIVE TYPE CHANGED SUCCESSFULLY')
        print('LOCOMOTIVE TYPE:' + loco_type, loco_type_name, power_desc)
        print('HAUL:' + str(haulage) + ' WT:' + str(weight) + 'LGTH:' + str(length) + 'FUEL CAP:' + str(fuel_capacity) + 'RATE:' + str(fuel_rate))	   
        print('MAINT INTERVAL:' + str(maint_outage) + 'WORKS TIME:' + str(works_time) + '(' + oper_desc + ')')  
        return 


    
    def dxloct(self, message):
        """deletes a locomotive type from the list.  checks that no
        locos are using it first
        """
        if self.show_access(message, 'DXLOCT loco type', 'S') != 0:
            return

        #locomotive type code
        loco_type, rc = self.extract_field(message, 0, 'LOCOMOTIVE TYPE CODE')
        if rc > 0:
            return
        data = (loco_type,)

        #validate the change - check there is a record to delete
        sql = 'select id from locotype where locotype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOCOMOTIVE TYPE CODE DOES NOT EXIST')
            return

        #make sure that there is not a loco linked to the type
        sql = 'select id from locomotive where locotype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* LOCOMOTIVES ARE ATTACHED TO THIS TYPE - CANNOT DELETE')
            return
            
        #process the change
        if self.db_update('delete from locotype where locotype = ?', data) == 0:
            print('LOCOMOTIVE TYPE' + loco_type + 'SUCCESSFULLY DELETED')
        return



    def liloct(self, message):
        """list locomotive types showing full details.  Sortable by name or code
        """
        if self.show_access(message, 'LILOCT (sort[0/1])', 'R') != 0:
            return        

        #sort requirement
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        # build the column titles
        name_size = 78 - self.loctsize - 51
        titles = self.x_field('TYPE======', self.loctsize)   + ' ' +\
                 self.x_field('LOCOMOTIVE TYPE===============', name_size) + ' ' +\
                 self.x_field('PWR==', 3) + ' ' +\
                 self.x_field('HAULS', 5) + ' ' +\
                 self.x_field('F.CAP', 5) + ' ' +\
                 self.x_field('FRATE', 5) + ' ' +\
                 self.x_field('MAINT', 5) + ' ' +\
                 self.x_field('WORKS', 5) + ' ' +\
                 self.x_field('WEGHT', 5) + ' ' +\
                 self.x_field('LNGTH', 5) + ' ' +\
                 self.x_field('MOD', 3)

        # get the extract data
        if sort_order == '1':
            sql = 'select id, locotype, name, power_type, haulage, fuel_capacity, fuel_rate, ' +\
                  'maint_interval, works_time, weight, length, oper_mode from locotype ' +\
                  'order by name'
        else:
            sql = 'select id, locotype, name, power_type, haulage, fuel_capacity, fuel_rate, ' +\
                  'maint_interval, works_time, weight, length, oper_mode from locotype ' +\
                  'order by locotype'
               
        count, ds_locotypes = self.db_read(sql, '')
        if count < 0:
            return

        #display the data to the screen
        line_count = 0
        for row in ds_locotypes:
            if line_count == 0:
                print(titles)
            power, oper_mode = self.get_short_desc(row[3], row[11])
            print(self.x_field(row[1], self.loctsize) + " " +
                   self.x_field(row[2], name_size) + " " +
                   self.x_field(power, 3) + " " +
                   self.x_field(row[4], 5, 'R') + " " +
                   self.x_field(row[5], 5, 'R') + " " +
                   self.x_field(row[6], 5, 'R') + " " +
                   self.x_field(row[7], 5, 'R') + " " +
                   self.x_field(row[8], 5, 'R') + " " +
                   self.x_field(row[9], 5, 'R') + " " +
                   self.x_field(row[10], 5, 'R') + " " +
                   self.x_field(oper_mode, 3))

            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return


    def prloct(self, message, Params):
        """print locomotive types showing full details.  Sortable by name or code
        """
        if self.show_access(message, 'PRLOCT (sort[0/1])', 'R') != 0:
            return           

        #sort requirement
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        # build the column titles
        name_size = 79 - self.loctsize - 51
        titles = self.x_field('TYPE======', self.loctsize)   + ' ' +\
                 self.x_field('LOCOMOTIVE TYPE===============', name_size) + ' ' +\
                 self.x_field('PWR==', 3) + ' ' +\
                 self.x_field('HAULS', 5) + ' ' +\
                 self.x_field('F.CAP', 5) + ' ' +\
                 self.x_field('FRATE', 5) + ' ' +\
                 self.x_field('MAINT', 5) + ' ' +\
                 self.x_field('WORKS', 5) + ' ' +\
                 self.x_field('WEGHT', 5) + ' ' +\
                 self.x_field('LNGTH', 5) + ' ' +\
                 self.x_field('MOD', 3)

        # get the extract data
        if sort_order == '1':
            sql = 'select id, locotype, name, power_type, haulage, fuel_capacity, fuel_rate, ' +\
                  'maint_interval, works_time, weight, length, oper_mode from locotype ' +\
                  'order by name'
        else:
            sql = 'select id, locotype, name, power_type, haulage, fuel_capacity, fuel_rate, ' +\
                  'maint_interval, works_time, weight, length, oper_mode from locotype ' +\
                  'order by locotype'
               
        count, ds_locotypes = self.db_read(sql, '')
        if count < 0:
            return

        #build the extracted data
        self.temp = {}
        for row in ds_locotypes:
            power, oper_mode = self.get_short_desc(row[3], row[11])
            print_line = self.x_field(row[1], self.loctsize) + ' ' +\
                   self.x_field(row[2], name_size) + ' ' +\
                   self.x_field(power, 3) + ' ' +\
                   self.x_field(row[4], 5, 'R') + ' ' +\
                   self.x_field(row[5], 5, 'R') + ' ' +\
                   self.x_field(row[6], 5, 'R') + ' ' +\
                   self.x_field(row[7], 5, 'R') + ' ' +\
                   self.x_field(row[8], 5, 'R') + ' ' +\
                   self.x_field(row[9], 5, 'R') + ' ' +\
                   self.x_field(row[10], 5, 'R') + ' ' +\
                   self.x_field(oper_mode, 3)
            if message == '1':
                self.temp[row[2]] = print_line
            else:
                self.temp[row[1]] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRLOCT',
                           report_name = 'LIST OF LOCOMOTIVE TYPES',
                           Params = Params)
        return



    def get_power_desc(self, power_type, loco_oper_mode):
        """gets descriptions for power type and oper mode
        """
        if power_type == 'D':
            power_desc = 'DIESEL LOCOMOTIVE'
        elif power_type == 'E':
            power_desc ='ELECTRIC LOCOMOTIVE'
        elif power_type == 'S':
            power_desc = 'STEAM LOCOMOTIVE'
        elif power_type == 'O':
            power_desc = 'OTHER LOCOMOTIVE TYPE'
        else:
            power_desc = 'NOT KNOWN'
        if loco_oper_mode == 'I':
            oper_desc = 'LOCOMOTIVE CAN OPERATE INDEPENDENTLY'
        elif loco_oper_mode == 'S':
            oper_desc = 'SLAVE LOCOMOTIVE, CANNOT OPERATE INDEPENDENTLY'
        elif loco_oper_mode == 'M':
            oper_desc = 'MULTIPLE UNIT LOCOMOTIVE'
        elif loco_oper_mode == 'O':
            oper_desc = 'OTHER LOCOMOTIVE OPERATING TYPE'
        else:
            oper_desc = 'NOT KNOWN'
        return power_desc, oper_desc



    def get_short_desc(self, power_type, loco_oper_mode):
        """gets short descriptions for power type and oper mode
        """
        if power_type == 'D':
            power_desc = 'DSL'
        elif power_type == 'S':
            power_desc = 'STM'
        elif power_type == 'E':
            power_desc = 'ELC'
        else:
            power_desc = 'OTHR'  
        if loco_oper_mode == 'I':
            oper_mode_desc = 'IND'
        elif loco_oper_mode == 'S':
            oper_mode_desc = 'DUM'
        elif loco_oper_mode == 'M':
            oper_mode_desc = 'M/U'
        else: 
            oper_mode_desc = 'IND'
        return power_desc, oper_mode_desc
