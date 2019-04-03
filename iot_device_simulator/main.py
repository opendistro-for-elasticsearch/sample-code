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

Generate load against an Amazon ES endpoint. Needs lots of work to add
parameterizations around endpoint, request signing, number of devices,
kinds of sensors, etc. etc.

Improvements:
 - Don't hardcode the device construction
 - Don't hardcode the sensors per device
'''

import argparse
import time

from device import Device
from flushing_es_buffer import FlushingESBuffer, ESDescriptor
from sensor import SineSensor, ConstSensor, DriftingSensor, MonotonicSensor
from transport import Transport

def get_args():
    description = 'Simulate devices with sensors and send data to Elasticsearch'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-d', '--devices', type=int, default=10,
        help='the number of devices', action='store')
    parser.add_argument('-s', '--samples', type=int, default=1000,
        help='the number of samples to Elasticsearch', action='store')
    parser.add_argument('-b', '--batch-size', type=int, default=1000,
        help='Number of log lines in each _bulk request', action='store')
    args = parser.parse_args()
    if args.devices < 0:
        raise ValueError('Number of devices must be positive')
    if args.samples < 0:
        raise ValueError('Number of samples must be positive')
    if args.batch_size < 0:
        raise ValueError('Batch size must be positive')
    descriptive_text = ('Building {} devices with 5 sensors each and sending {} '
                        'samples to Elasticsearch. Total of {} log lines')
    descriptive_text = descriptive_text.format(args.devices, args.samples, 
                                               5 * args.devices * args.samples)
    print(descriptive_text)
    return args

def make_device():
    d = Device()
    d.add_sensor(ConstSensor('humidity', value=50, fuzz=20.0))
    d.add_sensor(DriftingSensor('drift', seed=50, threshold=10,
                                reset_threshold=100, drift_amt=0.5))
    d.add_sensor(SineSensor('temperature', 43, 78, 4, fuzz=1.0))
    d.add_sensor(DriftingSensor('CPU', seed=50, threshold=10,
                                reset_threshold=100, drift_amt=0.1))
    return d


if __name__ == '__main__':
    args = get_args()
    buffer = FlushingESBuffer(
        ESDescriptor(endpoint='https://127.0.0.1:9200', 
                     es_index='logs',
                     es_type='log'),
        signed=False,
        flush_trigger=args.batch_size)
    devices = list() # pylint: disable=invalid-name
    for i in range(args.devices - 1):
        d = make_device()
        devices.append(d)

    # Add a special device that has a "malfunctioning" CPU that ramps to 100.
    d = make_device()
    d.remove_sensor('CPU')
    d.add_sensor(MonotonicSensor('CPU', value=50, delta=0.1, ceiling=100, 
                                 fuzz=0.01))
    devices.append(d)

    for i in range(args.samples):
        for device in devices:
            dev_report = device.report()
            for sens_report in dev_report:
                buffer.add_log_line(sens_report)
        time.sleep(1)
