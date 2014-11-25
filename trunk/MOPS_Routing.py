'''
Routing Class
This contains information about requests for cars -
 empty car orders and for waybills

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Unused variables removed
'''

import MOPS_Element

class cRoutings(MOPS_Element.cElement):
    """information about required customer routing for traffic.  this information is advisory only
    and is printed on waybills, etc: it is not enforced.
    """
    extract_code = 'select * from routing'
    extract_header = 'id|code|description\n'



    def adcuro(self, message):
        """adds a new routing code and description
        """
        if self.show_access(message, 'ADCURO customer routing;description', 'S') != 0:
            return
        
        #routing code-------------------------------------------------------------------------------
        curo, rc = self.extract_field(message, 0, 'CUSTOMER ROUTING CODE')
        if rc > 0:
            return

        if len(curo) > self.curosize:
            print('* CUSTOMER ROUTING CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(curo) == 0:
            print('* NO CUSTOMER ROUTING CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #check it does not already exist on the database
        data = (curo,)
        sql = 'select id from routing where routing = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* CUSTOMER ROUTING CODE ALREADY EXISTS')
            return

        #customer routing---------------------------------------------------------------------------
        routing, rc = self.extract_field(message, 1, 'CUSTOMER ROUTING DETAILS')
        if rc > 0:
            return

        #carry out the update-----------------------------------------------------------------------
        data = (curo, routing)
        sql = 'insert into routing values (null, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        print('NEW CUSTOMER ROUTING ADDED SUCCESSFULLY')
        print(curo + routing)
        return
    


    def chcuro(self, message):
        """allows amendment of an existing routing code
        """
        if self.show_access(message, 'CHCURO customer routing;description', 'S') != 0:
            return
        
        #routing code-------------------------------------------------------------------------------
        curo, rc = self.extract_field(message, 0, 'CUSTOMER ROUTING CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (curo,)
        sql = 'select desc from routing where routing = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* CUSTOMER ROUTING CODE DOES NOT EXIST')
            return

        for row in ds_routes:
            routing = row[0]

        #customer routing--------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            routing = value

        #carry out the update----------------------------------------------------------------------
        data = (routing, curo)
        sql = 'update routing set desc = ? where routing = ?'
        if self.db_update(sql, data) != 0:
            return

        print('CUSTOMER ROUTING CHANGED SUCCESSFULLY')
        print(curo + routing)
        return



    def dxcuro(self, message):
        """deletes a customer routing from the database.  cannot eb deleted if attached to a
        warehouse
        """
        if self.show_access(message, 'DXCURO customer routing', 'S') != 0:
            return

        #routing code-------------------------------------------------------------------------------
        curo, rc = self.extract_field(message, 0, 'CUSTOMER ROUTING CODE')
        if rc > 0:
            return
        data = (curo,)

        #validate the change-----------------------------------------------------------------------
        sql = 'select id from routing where routing = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* CUSTOMER ROUTING CODE DOES NOT EXIST')
            return

        #validate that the customer routing is not in use------------------------------------------
        sql = 'select id from warehouse where routing = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* CUSTOMER ROUTING IN USE FOR A WAREHOUSE, CANNOT DELETE')
            return

        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from routing where routing = ?', data) == 0:
            print('CUSTOMER ROUTING' + curo + 'SUCCESSFULLY DELETED')
        return



    def licuro(self, message):
        """lists customer routing codes on the database.  available in code or name order.
        """
        if self.show_access(message, 'LICURO (sort[0/1])', 'R') != 0:
            return        

        #work out the various parameters
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = ''

        # build the column titles
        titles = self.x_field('CODE======', self.curosize) + ' ' +\
                 self.x_field('ROUTING=============================================', 50)

        # get the extract data
        if sort_order == '1':
            sql = 'select routing, desc from routing order by desc'
        else:
            sql = 'select routing, desc from routing order by routing'

        count, ds_routes = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data
        line_count = 0
        for row in ds_routes:
            if line_count == 0:
                print(titles)               
            print(self.x_field(row[0], self.curosize) + " " +
                    self.x_field(row[1], 50))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def prcuro(self, message, Params):
        """prints customer routing to a report.  available sorted by code or name
        """
        if self.show_access(message, 'PRCURO (sort[0/1])', 'R') != 0:
            return        

        #work out the various parameters
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = ''

        # build the column titles ------------------------------------------
        titles = self.x_field('CODE======', self.curosize) + ' ' +\
                 self.x_field('ROUTING=============================================', 50)

        # get the extract data
        if sort_order == '1':
            sql = 'select routing, desc from routing order by desc'
        else:
            sql = 'select routing, desc from routing order by routing'

        count, ds_routes = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data
        self.temp = {}
        
        for row in ds_routes:
            print_line = self.x_field(row[0], self.curosize) + ' ' +\
                         self.x_field(row[1], 50)
            if sort_order == '1':
                self.temp[row[1]] = print_line
            else:
                self.temp[row[0]] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRCURO',
                           report_name = 'LIST OF CUSTOMER ROUTINGS',
                           Params = Params)
        return
