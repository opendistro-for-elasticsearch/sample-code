'''
Copyright 2019, Amazon Web Services Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Python 3
'''

import json
import time
import uuid

import boto3
from pytz import timezone
from sensor import SineSensor, ConstSensor, DriftingSensor

class Device():
    '''A device has a list of sensors and generates report()s'''
    def __init__(self, device_id=None, target_tz='US/Pacific'):
        if device_id:
            self.device_id = device_id
        else:
            self.device_id = "device_%s" % str(uuid.uuid1())
        self.timezone = timezone(target_tz)
        self.sensors = list()

    def add_sensor(self, sensor_to_add):
        '''Add a sensor to the list'''
        self.sensors.append(sensor_to_add)

    def remove_sensor(self, sensor_name):

        self.sensors = \
            [sensor for sensor in self.sensors \
                if sensor.get_value_name != sensor_name]

    def report(self):
        '''Generate a list of records for this device. Each element is a
           dict with a single sensor report.
           TODO The return should be hierarchical rather than flat.'''
        ret = list()
        for sensor in self.sensors:
            rep = sensor.report()
            rep['device_id'] = self.device_id
            rep['unique_id'] = "%s:%s" % (rep['device_id'], \
                                          rep['sensor_id'])
            ret.append(rep)
        return ret
