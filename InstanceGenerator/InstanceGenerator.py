'''
AMMM Instance Generator v1.0
Instance Generator class.
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

import os
import random


class InstanceGenerator(object):
    def __init__(self, config):
        self.config = config

    def generate(self):
        instancesDirectory = self.config.instancesDirectory
        fileNamePrefix = self.config.fileNamePrefix
        fileNameExtension = self.config.fileNameExtension
        numInstances = self.config.numInstances

        nNurses = self.config.nNurses
        hours = self.config.hours
        minHours = self.config.minHours
        maxHours = self.config.maxHours

        maxConsec = self.config.maxConsec
        maxPresence = self.config.maxPresence

        if(not os.path.isdir(instancesDirectory)):
            raise Exception(
                'Directory(%s) does not exist' % instancesDirectory)

        for i in xrange(0, numInstances):
            instancePath = os.path.join(instancesDirectory,
                '%s_%d.%s' % (fileNamePrefix, i, fileNameExtension))
            fInstance = open(instancePath, 'w')

            num_hours = random.randint(hours >> 2, hours)
            total_demand = []
            # Should probably check if dividing by 4 is enough
            total_nurses = random.randint(nNurses >> 4, nNurses)

            for h in xrange(0, num_hours):
                current_hours_demand = random.randint(1, total_nurses)
                total_demand.append(current_hours_demand)

            fInstance.write('nNurses=%d;\n' % total_nurses)
            fInstance.write('hours=%d;\n' % num_hours)
            fInstance.write('demand=[%s];\n' % (
                ' '.join(map(str, total_demand))))
            fInstance.write('minHours=%d;\n' % minHours)
            fInstance.write('maxHours=%d;\n' % maxHours)
            fInstance.write('maxConsec=%d;\n' % maxConsec)
            fInstance.write('maxPresence=%d;\n' % maxPresence)
            fInstance.close()
