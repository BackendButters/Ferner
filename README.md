# Ferner
A Simple AWS Glacier upload slave.

## What's that?
Project Ferner is meant to be a user-friendly [AWS Glacier](http://aws.amazon.com/de/glacier/) client. Right now, Ferner consists of the *Snowman*-Module, which is currently able to upload files to Glacier.

## Prerequisites
Python 3.4 with modules: watchdog, logbook, boto

## Configuration
Use the provided configuration file *dconf.yaml* and adapt it to your settings. Enter your AWS credentials and region and vault to use. Also, make sure your AWS user is equipped with the correct Glacier permissions. If you wish, you can also specify the time range in which uploads will be started.

## Usage
`Snowman.py -c *yourconfig*.yaml`

After starting the program, all newly created files in the working directory will be automatically uploaded to the vault provided in the config file.

## What's to come?
A lot. I plan to transform it into a full Django Web-App that keeps track of your Glacier inventory, accepts and automatically handles up- and download jobs. Version 0.1 can be regarded as a kick-off.

## What does *Ferner* mean?
It's the bavarian word for glacier.

## Why did you create that?
For my own purposes to easily upload files to glacier with my not-so-fast internet connection and without needing to run my 400W computer all night. Instead, I run it on a Raspberry Pi.

## Issues
If you are having boto-issues, especially `boto.glacier.exceptions.UnexpectedHTTPResponseError: Expected (204,), got (400, b'{"code":"InvalidParameterValueException","message":"Invalid Content-Range: bytes%200-4194303/*","type":"Client"}')`, have a look at [this issue](https://github.com/boto/boto/issues/2524).

## License
Ferner is published under the MIT License.
