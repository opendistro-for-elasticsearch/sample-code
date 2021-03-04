# IoT Device and Sensor Simulator

This library provides a set of Python classes that simulates sensors and
devices. Devices are collections of sensors. The library also includes classes
for buffering log lines and sending to Elasticsearch. 


## Requirements

The code requires Python 3

This example uses the es_sink library, provided in this repo. To install,

```
> pip install <path_to_community_repo>/es_sink
```


## Basic Usage

main.py illustrates the basic usage of the library. Construct and use a
FlushingESBuffer, pointing at the Elasticsearch endpoint. Construct devices with
Sensors. Call each Device's report() method in a loop, and send the result
to the FlushingESBuffer.

There are 4 Sensor types:

1. SineSensor - Produces a sin wave, based on the system clock between a bottom
and a top value. You can add random fuzz. 
2. ConstSensor - Produces a constant value. Can be modified with Random fuzz. 
3. DriftingConstSensor - A ConstSensor that drifts randomly from its starting 
value. 
4. MonotonicSensor - Produces a monotonically changing value, based on a start 
point, delta amount, and fuzz.


## Code of Conduct

This project has adopted an [Open Source Code of
Conduct](https://opendistro.github.io/for-elasticsearch/codeofconduct.html).


## Security issue notifications

If you discover a potential security issue in this project we ask that you
notify AWS/Amazon Security via our [vulnerability reporting
page](http://aws.amazon.com/security/vulnerability-reporting/). Please do
**not** create a public GitHub issue.


## Licensing

See the [LICENSE](./LICENSE) file for our project's licensing. We will ask you
to confirm the licensing of your contribution.


## Copyright

Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
