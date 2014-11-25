'''
Instructions Class
Contains Instructions to be used alongside Routes, Schedules and Stations

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.
'''
import MOPS_Element

class cInstructions(MOPS_Element.cElement):
    """instructions are additional, specific details for stations, routes and schedules.
    instructions are automatically deleted when a station, route or section is deleted, but
    can also be deleted independently
    """
    extract_code = 'select * from instructions'
    extract_header = 'id|route|schedule|station|instruction'



    def adinst(self, message):
        """add an instruction.  determine whether the instruction is for a station, route or
        schedule.
        """
        if self.show_access(message,
                            'ADINST element[ROUT/SCHD/STAX];route/schedule/station;instruction',
                            'N') != 0:
            return

        route = ''
        schedule = ''
        station = ''

        #type code----------------------------------------------------------------------------------
        xtype, rc = self.extract_field(message, 0, 'INSTRUCTION TYPE')
        if rc > 0:
            return

        if not (xtype == 'ROUT' or xtype == 'SCHD' or xtype == 'STAX'):
            print('* ITEM MUST BE <ROUT> <SCHD> OR <STAX>')
            return

        # where the instruction is for--------------------------------------------------------------
        entity, rc = self.extract_field(message, 1, 'WHERE INSTRUCTION IS FOR')
        if rc > 0:
            return

        if xtype == 'ROUT':
            sql = 'select id from route where route = ?'
            route = entity
        elif xtype == 'SCHD':
            sql = 'select id from schedule where schedule = ?'
            schedule = entity
        else:
            sql = 'select id from station where station = ?'
            station = entity
                
        data = (entity, )
        count, data = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* ROUTE, SCHEDULE OR STATION CODE DOES NOT EXIST (' + entity + ')')
            return

        #the instruction----------------------------------------------------------------------------
        instruction, rc = self.extract_field(message, 2, 'INSTRUCTION')
        if rc > 0:
            return         

        #carry out the update-----------------------------------------------------------------------
        data = (route, schedule, station, instruction)
        sql = 'insert into instructions values (null, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        print('NEW INSTRUCTION ADDED SUCCESSFULLY')
        print(xtype + entity + instruction)
        return
                

        
    def dxinst(self, message):
        """deletes a given instruction by id
        """
        if self.show_access(message, 'DXINST id', 'N') != 0:
            return

        #type code----------------------------------------------------------------------------------
        instruction, rc = self.extract_field(message, 0, 'INSTRUCTION TYPE')
        if rc > 0:
            return
        
        data = (instruction,)

        #validate the change------------------------------------------------------------------------
        sql = 'select id from instructions where id = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* INSTRUCTION CODE DOES NOT EXIST')
            return
        
        #process the change - delete the instructions-----------------------------------------------
        if self.db_update('delete from instructions where id = ?', data) == 0:
            print('INSTRUCTION' + instruction + 'SUCCESSFULLY DELETED')
        
        return
        
