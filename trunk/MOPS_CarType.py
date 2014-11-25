'''
CarType Class This sub-divides Car Classes into cars with the same characteristics for
loading and other purposes

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1  Unused variables removed
    17/08/2010 Ver 1  Added processing for P-Passenger type cars
'''

import MOPS_Element

class cCarTypes(MOPS_Element.cElement):
    """details about car types.  car types contain information about cars, and are linked to car
    classes.  car types have loading codes which determine loading and unloading availability.
    """
    extract_header = 'id|code|name|length|oper mode|capacity|' +\
                     'unladen weight|loading|unloading|class\n'
    extract_code = 'select * from cartype'



    def adcart(self, message):
        """adds details of a type of car - length, weight, capacity, unladen weight,
        and how it loads/unloads (linked to a loading code).  must belong to a car class.
        operating mode also required - I-Independent (ie normal car) or part of a
        multiple unit (mainly for passenger car sets that operate in multiple units with
        a mixture of powered and unpowered cars).
        """
        if self.show_access(message,
                            'ADCART car type;type name;length;capacity;unladen weight;oper mode[I/M];' +\
                            '^load^;^(un)load^;^car class^', 'S') != 0:
            return
        errors = 0
        
        #code---------------------------------------------------------------------------------------
        cartype, rc = self.extract_field(message, 0, 'CAR TYPE CODE')
        if rc > 0:
            return

        if len(cartype) > self.cartsize:
            print('* CAR TYPE  CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(cartype) ==0:
            print('* NO CAR TYPE  CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #check it does not already exist on the database--------------------------------------------
        data = (cartype,)
        sql = 'select id from cartype where cartype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* CAR TYPE CODE ALREADY EXISTS')
            return

        #name---------------------------------------------------------------------------------------
        car_type_name, rc = self.extract_field(message, 1, 'CAR TYPE NAME')
        if rc > 0:
            return

        #length-------------------------------------------------------------------------------------
        length, rc = self.extract_field(message, 2, 'CAR TYPE LENGTH')
        if rc > 0:
            return

        try:
            if int(length) > 99999 or int(length) < 0:
                errors = errors + 1
                print('* CAR TYPE LENGTH MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* CAR TYPE LENGTH MUST BE A WHOLE NUMBER')

        #capacity-----------------------------------------------------------------------------------
        capacity, rc = self.extract_field(message, 3, 'CAR TYPE CAPACITY')
        if rc > 0:
            return
        
        try:
            if int(capacity) > 99999 or int(capacity) < 0:
                errors = errors + 1
                print('* CAR TYPE CAPACITY MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* CAR TYPE CAPACITY MUST BE A WHOLE NUMBER')

        #unladen weight-----------------------------------------------------------------------------
        unladen_weight, rc = self.extract_field(message, 4, 'UNLADEN WEIGHT')
        if rc > 0:
            return
        
        try:
            if int(unladen_weight) > 99999 or int(unladen_weight) < 0:
                errors = errors + 1
                print('* CAR TYPE UNLADEN WEIGHT MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* CAR TYPE UNLADEN WEIGHT MUST BE A WHOLE NUMBER')

        #car oper type------------------------------------------------------------------------------
        car_oper_mode, rc = self.extract_field(message, 5, 'OPERATING MODE')
        if rc > 0:
            return
        
        if not(car_oper_mode == 'I' or car_oper_mode == 'M' or car_oper_mode == 'P'): #Ver 1
            errors = errors + 1
            print('* OPERATING MODE MUST BE I-INDEPENDENT M-MULTIPLE UNIT P-PASSENGER')

        #loading------------------------------------------------------------------------------------
        loading, rc = self.extract_field(message, 6, 'LOADING CODE')
        if rc > 0:
            return

        data = (loading, 'Y')
        sql = 'select desc from loading where loading = ? and can_load = ?'
        count, ds_loadings = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* LOADING CODE ' + loading + ' DOES NOT EXIST OR NOT SET FOR LOADING')
        else:
            for row in ds_loadings:
                loading_desc = row[0]
                                 
        #unloading----------------------------------------------------------------------------------
        unloading, rc = self.extract_field(message, 7, 'UNLOADING CODE')
        if rc > 0:
            return

        data = (unloading, 'Y')
        sql = 'select desc from loading where loading = ? and can_unload = ?'
        count, ds_loadings = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* LOADING CODE ' + unloading + ' DOES NOT EXIST OR NOT SET FOR UNLOADING')
        else:
            for row in ds_loadings:
                unloading_desc = row[0]

        #car class----------------------------------------------------------------------------------
        carclass, rc = self.extract_field(message, 8, 'CAR CLASS CODE')
        if rc > 0:
            return

        data = (carclass,)
        sql = 'select name from carclass where carclass = ?'
        count, ds_classes = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* CAR CLASS CODE DOES NOT EXIST')
        else:
            for row in ds_classes:
                class_name = row[0]

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (cartype, car_type_name, length, car_oper_mode, capacity, unladen_weight,
             loading, unloading, carclass)
        sql = 'insert into cartype values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        oper_desc = ''
        if car_oper_mode == 'I':
            oper_desc = 'INDEPENDENT'
        if car_oper_mode == 'M':
            oper_desc = 'MULTIPLE UNIT'
        if car_oper_mode == 'P':                                            #Ver 1
            oper_desc = 'PASSENGER'                                         #Ver 1

        print('NEW CAR TYPE ADDED SUCCESSFULLY')
        print(cartype + car_type_name + carclass + class_name + oper_desc)
        print('LENGTH: ' + str(length) + ' CAPACITY: ' + str(capacity) + ' UNLADEN WT: ' +\
               str(unladen_weight))
        print('LOADING: ' + loading + ' (' + loading_desc.strip() + ') ' + 'UNLOADING:' +\
               unloading + ' (' + unloading_desc.strip() + ')')
        return


    
    def chcart(self, message):
        """amend details of a type of car - length, weight, capacity, unladen weight,
        and how it loads/unloads (linked to a loading code).  Must belong to a car class.
        Operating mode also required - I-Independent (ie normal car) or part of a
        Multiple Unit (mainly for passenger car sets that operate in Multiple Units with
        a mixture of powered and unpowered cars).
        """
        if self.show_access(message,
                            'CHCART car type;(type name);(length);(capacity);(unladen weight);' +\
                            '([I/M]);(^load^);(^(un)load^);(^car class^)', 'S') != 0:
            return
        errors = 0

        #code---------------------------------------------------------------------------------------
        cartype, rc = self.extract_field(message, 0, 'CAR TYPE CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (cartype,)
        sql = 'select name, length, oper_mode, capacity, unladen_weight, loading, unloading, ' +\
              'carclass from cartype where cartype = ?'
        count, ds_cartypes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* CAR TYPE CODE DOES NOT EXIST')
            return
        
        for row in ds_cartypes:
            car_type_name = row[0]
            length = row[1]
            car_oper_mode = row[2]
            capacity = row[3]
            unladen_weight = row[4]
            loading = row[5]
            unloading = row[6]
            carclass = row[7]
            old_carclass = row[7]

        #name---------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
                car_type_name = value
            
        #length-------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
                length = value
        
        try:
            if int(length) > 99999 or int(length) < 0:
                errors = errors + 1
                print('* CAR TYPE LENGTH MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* CAR TYPE LENGTH MUST BE A WHOLE NUMBER')

        #capacity-----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            capacity = value

        try:
            if int(capacity) > 99999 or int(capacity) < 0:
                errors = errors + 1
                print('* CAR TYPE CAPACITY MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* CAR TYPE CAPACITY MUST BE A WHOLE NUMBER')

        #unladen weight-----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 4, '')
        if rc == 0:
            unladen_weight = value

        try:
            if int(unladen_weight) > 99999 or int(unladen_weight) < 0:
                errors = errors + 1
                print('* CAR TYPE UNLADEN WEIGHT MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* CAR TYPE UNLADEN WEIGHT MUST BE A WHOLE NUMBER')

        #car oper type------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 5, '')
        if rc == 0:
            car_oper_mode = value

        if not(car_oper_mode == 'I' or car_oper_mode == 'M' or car_oper_mode == 'P'):    #Ver 1
            errors = errors + 1
            print('* OPERATING MODE MUST BE I-INDEPENDENT M-MULTIPLE UNIT P-PASSENGER')

        #loading------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 6, '')
        if rc == 0:
            loading = value

        data = (loading, 'Y')
        sql = 'select desc from loading where loading = ? and can_load = ?'
        count, ds_loadings = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* LOADING CODE ' + loading + ' DOES NOT EXIST OR NOT SET FOR LOADING')
        else:
            for row in ds_loadings:
                loading_desc = row[0]
                                 
        #unloading----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 7, '')
        if rc == 0:
            unloading = value

        data = (unloading, 'Y')
        sql = 'select desc from loading where loading = ? and can_unload = ?'
        count, ds_loadings = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* LOADING CODE ' + unloading + ' DOES NOT EXIST OR NOT SET FOR UNLOADING')
        else:
            for row in ds_loadings:
                unloading_desc = row[0]
                                 
        #car class----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 8, '')
        if rc == 0:
            carclass = value

        data = (carclass,)
        sql = 'select name from carclass where carclass = ?'
        count, ds_classes = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* CAR CLASS CODE DOES NOT EXIST')
        else:
            for row in ds_classes:
                class_name = row[0]

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (car_type_name, length, car_oper_mode, capacity, unladen_weight, loading,
             unloading, carclass, cartype)
        sql = 'update cartype set name = ?, length = ?, oper_mode = ?, capacity = ?, ' +\
              'unladen_weight = ?, loading = ?, unloading = ?, carclass = ? where cartype = ?'
        if self.db_update(sql, data) != 0:
            return

        if carclass != old_carclass:
            data = (carclass, old_carclass)
            sql = 'update car set carclass = ? where carclass = ?'
            if self.db_update(sql, data) != 0:
                return

        if car_oper_mode == 'I':
            oper_desc = 'INDEPENDENT'
        elif car_oper_mode == 'M':
            oper_desc = 'MULTIPLE UNIT'
        elif car_oper_mode == 'P':                                        #Ver 1
            oper_desc = 'PASSENGER'                                       #Ver 1
        else:
            oper_desc = ''

        print('CAR TYPE DETAILS CHANGED SUCCESSFULLY')
        print(cartype + car_type_name + carclass + class_name + oper_desc)
        print('LENGTH: ' + str(length) + ' CAPACITY: ' + str(capacity) + ' UNLADEN WT: ' +\
               str(unladen_weight))
        print('LOADING:' + loading + ' (' + loading_desc.strip() + ') ' + 'UNLOADING:' +\
               unloading + ' (' + unloading_desc.strip() + ')')
        return



    def dxcart(self, message):
        """deletes a car type from the list.  checks that a car does not refer to it
        """
        if self.show_access(message, 'DXCART car type', 'S') != 0:
            return
    
        #code---------------------------------------------------------------------------------------
        cartype, rc = self.extract_field(message, 0, 'CAR TYPE CODE')
        if rc > 0:
            return

        data = (cartype,)

        #validate the change------------------------------------------------------------------------
        sql = 'select id from cartype where cartype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* CAR TYPE CODE DOES NOT EXIST')
            return

        #make sure that there is not a car linked to the cartype------------------------------------
        sql = 'select id from car where cartype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* CARS BELONG TO THIS CAR TYPE - CANNOT DELETE')
            return

        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from cartype where cartype = ?', data) == 0:
            print('CAR TYPE ' + cartype + ' SUCCESSFULLY DELETED')
        return
    

        
    def licart(self, message):
        """returns a list of cars.  Sortable by code or name
        """
        if self.show_access(message, 'LICART (sort[0/1])', 'R') != 0:
            return        

        #status
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = ''

        #class
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            class_filter = value
        else:
            class_filter = ''
            
        # build the column titles
        class_name = 80 - self.cartsize - 2 * self.loadsize - self.classize - 16 - 8
        if class_name > 30:
            class_name = 30
        titles = self.x_field('TYPE======', self.cartsize) + ' ' +\
                 self.x_field('NAME==========================', class_name) + ' ' +\
                 self.x_field('LNGTH', 5) + ' ' +\
                 self.x_field('CAPTY', 5) + ' ' +\
                 self.x_field('U/WT=', 5) + ' ' +\
                 self.x_field('O', 1) + ' ' +\
                 self.x_field('LOADING===', self.loadsize) + ' ' +\
                 self.x_field('UNLOADING=', self.loadsize) + ' ' +\
                 self.x_field('CLASS=====', self.classize)

        # get the extract data
        if sort_order == '1':
            sql = 'select cartype, name, length, oper_mode, capacity, unladen_weight, loading, ' +\
                  'unloading, carclass from cartype order by name'
        else:        
            sql = 'select cartype, name, length, oper_mode, capacity, unladen_weight, loading, ' +\
                  'unloading, carclass from cartype order by carclass'

        count, ds_cartype = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data
        line_count = 0
        records = 0
        for row in ds_cartype:
            car_class = row[8]
            if line_count == 0:
                print(titles)
            if class_filter == '' or class_filter == car_class:
                print(self.x_field(row[0], self.cartsize) + " " +
                       self.x_field(row[1], class_name) + " " +
                       self.x_field(row[2], 5, 'R') + " " +
                       self.x_field(row[4], 5, 'R') + " " +
                       self.x_field(row[5], 5, 'R') + " " +
                       self.x_field(row[3], 1) + " " +
                       self.x_field(row[6], self.loadsize) + " " +
                       self.x_field(row[7], self.loadsize) + " " +
                       self.x_field(row[8], self.classize))
                records = records + 1
                line_count = line_count + 1
                if line_count > 20:
                    line_count = 0
                    reply = raw_input('+')
                    if reply == 'x':
                        break
        print(' ** END OF DATA:' + str(records) + ' RECORDS DISPLAYED **')         
        return



    def prcart(self, message, Params):
        """prints a list of cars.  Sortable by code or name
        """
        if self.show_access(message, 'PRCART (sort[0/1])', 'R') != 0:
            return        

        #status
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = ''

        #class
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            class_filter = value
        else:
            class_filter = ''
            
        # build the column titles
        class_name = 80 - self.cartsize - 2 * self.loadsize - self.classize - 16 - 8
        if class_name > 30:
            class_name = 30
        titles = self.x_field('TYPE======', self.cartsize) + ' ' +\
                 self.x_field('NAME==========================', class_name) + ' ' +\
                 self.x_field('LNGTH', 5) + ' ' +\
                 self.x_field('CAPTY', 5) + ' ' +\
                 self.x_field('U/WT=', 5) + ' ' +\
                 self.x_field('O', 1) + ' ' +\
                 self.x_field('LOADING===', self.loadsize) + ' ' +\
                 self.x_field('UNLOADING=', self.loadsize) + ' ' +\
                 self.x_field('CLASS=====', self.classize)

        # get the extract data
        if sort_order == '1':
            sql = 'select cartype, name, length, oper_mode, capacity, unladen_weight, loading, ' +\
                  'unloading, carclass from cartype order by name'
        else:        
            sql = 'select cartype, name, length, oper_mode, capacity, unladen_weight, loading, ' +\
                  'unloading, carclass from cartype order by carclass'

        count, ds_cartype = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data
        self.temp = {}
        for row in ds_cartype:
            car_class = row[8]
            if class_filter == '' or class_filter == car_class:
                print_line = self.x_field(row[0], self.cartsize) + ' ' +\
                       self.x_field(row[1], class_name) + ' ' +\
                       self.x_field(row[2], 5, 'R') + ' ' +\
                       self.x_field(row[4], 5, 'R') + ' ' +\
                       self.x_field(row[5], 5, 'R') + ' ' +\
                       self.x_field(row[3], 1) + ' ' +\
                       self.x_field(row[6], self.loadsize) + ' ' +\
                       self.x_field(row[7], self.loadsize) + ' ' +\
                       self.x_field(row[8], self.classize)
                if sort_order == '1':
                    self.temp[row[1]] = print_line
                else:
                    self.temp[row[0]] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRCART',
                           report_name = 'LIST OF CAR TYPES',
                           Params = Params)
        return
        
