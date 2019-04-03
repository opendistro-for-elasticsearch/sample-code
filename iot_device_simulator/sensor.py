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

Sensors! You want 'em, we got 'em
'''

from abc import ABCMeta, abstractmethod
from datetime import datetime
import math
import random
import time
import uuid
from pytz import timezone

class Sensor():
    '''Abstract class for all sensors'''

    __metaclass__ = ABCMeta

    def __init__(self, value_name, target_tz='US/Pacific'):
        self.sensor_id = "Sensor_%s" % str(uuid.uuid1())
        self.value_name = value_name
        self.timezone = timezone(target_tz)

    def now_local(self):
        '''Return the current time in PST timezone'''
        return datetime.now(timezone('UTC')).replace(microsecond=0).astimezone(self.timezone)

    def get_value_name(self):
        return self.value_name

    @abstractmethod
    def report(self):
        ''' Return a dict with timestamp and value'''


class SineSensor(Sensor):
    '''Reports a sin wave from min to max with sigfigs representing
       how quickly the value changes.
       TODO: timestamp belongs on the device'''
    def __init__(self, value_name, bottom=0, top=0, sigfigs=0, fuzz=0,
                 target_tz='US/Pacific'):
        super(SineSensor, self).__init__(value_name, target_tz)
        self.bottom = bottom
        self.top = top
        self.sigfigs = sigfigs
        self.fuzz = fuzz

    def value(self):
        '''Computes the value based on the current timestamp. Maybe better to compute
           off the last value'''
        divisor = 10.0**self.sigfigs
        one_to_n = int(time.time()) % divisor + 1
        mult_pct = one_to_n / divisor
        total_domain = 4 * math.pi
        sin = 1.0 + math.sin(total_domain * mult_pct)
        value_range = self.top - self.bottom
        return (self.bottom + (sin / 2.0) * value_range) + \
               (self.fuzz * random.random())

    def report(self):
        data_dict = {'@timestamp': self.now_local().isoformat(),
                     'sensor_id': self.sensor_id,
                     self.value_name: self.value()}
        return data_dict


class ConstSensor(Sensor):
    '''A sensor that reports a constant value. Add fuzz for variance
       TODO: timestamp belongs on the device'''
    def __init__(self, value_name, value=0, fuzz=0, target_tz='US/Pacific'):
        super(ConstSensor, self).__init__(value_name, target_tz)
        self.cur_value = value
        self.fuzz = fuzz
    def value(self):
        '''The value is a constant. Just add fuzz.'''
        return self.cur_value + random.random() * self.fuzz
    def report(self):
        return {
            '@timestamp': self.now_local().isoformat(),
            'sensor_id': self.sensor_id,
            self.value_name: self.value()
        }


class DriftingSensor(ConstSensor):
    '''A constant sensor that drifts randomly over time. Applies
       a random drift ranging from -drift_amt to +drift_amt when
       a random * the amount of seconds since the last drift is above
       threshold. '''
    def __init__(self, value_name, seed=0, threshold=0, drift_amt=0,
                 reset_threshold=0, fuzz=0, target_tz='US/Pacific'):
        super(DriftingSensor, self).__init__(value_name,
                                             value=seed,
                                             fuzz=fuzz,
                                             target_tz=target_tz)
        self.initial_value = seed
        self.threshold = threshold
        self.reset_threshold = reset_threshold
        self.drift_amt = drift_amt
        self.last_drift = time.time()

    def value(self):
        '''The value drifts by a random amount between -drift_amt and +drift_amt
           within a random amount of time. If reset_threshold is exceeded, then
           the value returns to its initial point. Fuzz also applies.'''
        time_elapsed = time.time() - self.last_drift
        if random.random() * time_elapsed > self.reset_threshold:
            self.cur_value = self.initial_value
        if random.random() * time_elapsed > self.threshold:
            self.cur_value += random.uniform(-self.drift_amt, self.drift_amt)
            self.last_drift = time.time()
        return super(DriftingSensor, self).value()
    def report(self):
        return {
            '@timestamp': self.now_local().isoformat(),
            'sensor_id': self.sensor_id,
            self.value_name: self.value()
        }


class MonotonicSensor(Sensor):
    '''A sensor that reports a constant value. Add fuzz for variance
       TODO: timestamp belongs on the device'''
    def __init__(self, value_name, value=0, delta=0, fuzz=0, 
                 ceiling=None, target_tz='US/Pacific'):
        super(MonotonicSensor, self).__init__(value_name, target_tz)
        self.cur_value = value
        self.delta = delta
        self.fuzz = fuzz
        self.ceiling = ceiling
    def value(self):
        '''The value is a constant. Just add fuzz.'''
        if self.ceiling and self.cur_value >= self.ceiling:
            return self.cur_value
        self.cur_value = self.cur_value + self.delta + random.random() * self.fuzz
        return self.cur_value
    def report(self):
        return {
            '@timestamp': self.now_local().isoformat(),
            'sensor_id': self.sensor_id,
            self.value_name: self.value()
        }
