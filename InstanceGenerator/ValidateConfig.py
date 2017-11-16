'''
AMMM Instance Generator v1.0
Config attributes validator.
Copyright 2016 Luis Velasco and Lluis Gifre.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# Validate config attributes read from a DAT file.


class ValidateConfig(object):
    @staticmethod
    def validate(data):
        # Validate that mandatory input parameters were found
        for paramName in ['instancesDirectory', 'fileNamePrefix',
                          'fileNameExtension', 'numInstances',
                          'nNurses', 'hours', 'minHours', 'maxHours',
                          'maxConsec', 'maxPresence']:
            if(paramName not in data.__dict__):
                print paramName, data.__dict__
                raise Exception(
                    'Parameter(%s) not contained in Configuration' % str(
                        paramName))

        instancesDirectory = data.instancesDirectory
        if(len(instancesDirectory) == 0):
            raise Exception('Value for instancesDirectory is empty')

        fileNamePrefix = data.fileNamePrefix
        if(len(fileNamePrefix) == 0):
            raise Exception('Value for fileNamePrefix is empty')

        fileNameExtension = data.fileNameExtension
        if(len(fileNameExtension) == 0):
            raise Exception('Value for fileNameExtension is empty')

        numInstances = data.numInstances
        if(not isinstance(numInstances, (int, long)) or (numInstances <= 0)):
            raise Exception(
                'numInstances(%s) has to be a positive integer value.' % str(numInstances))

        nNurses = data.nNurses
        if(not isinstance(nNurses, (int, long)) or (nNurses <= 0)):
            raise Exception(
                'nNurses(%s) has to be a positive integer value.' % str(nNurses))

        hours = data.hours
        if(not isinstance(hours, (int, long)) or (hours <= 0)):
            raise Exception(
                'hours(%s) has to be a positive integer value.' % str(hours))

        minHours = data.minHours
        if not isinstance(minHours, (int, long, float)):
            raise Exception(
                'minHours(%s) has to be a positive float value.' % str(minHours))

        maxHours = data.maxHours
        if(not isinstance(maxHours, (int, long, float)) or (maxHours <= 0) or (maxHours < minHours)):
            raise Exception(
                'maxHours(%s) has to be a positive float value.' % str(maxHours))

        maxConsec = data.maxConsec
        if(not isinstance(maxConsec, (int, long)) or (maxConsec <= 0)):
            raise Exception(
                'maxConsec(%s) has to be a positive integer value.' % str(maxConsec))

        maxPresence = data.maxPresence
        if(not isinstance(maxPresence, (int, long)) or (maxPresence <= 0)):
            raise Exception(
                'maxPresence(%s) has to be a positive integer value.' % str(maxPresence))
