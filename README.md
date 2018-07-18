# Automated Aruba AP Provisioning

Python script to interface with the Mobility Master/Controller to process an input CSV file containing APs to provision.

### Prerequisites

 * Python 3.x
 * `credentials.py` file formatted like below
 * `input.csv` file formatted like below

Tested on MacOS 10.13.5 with Python 3.7.0

Ensure `python3` is in your `$PATH`, and that `main.py` has execute permissions set.

## Usage


```
$ ./main.py -h
usage: main.py [-h] [-d] building floor

Provision APs (303H/334)

positional arguments:
  building    building name
  floor       floor number

optional arguments:
  -h, --help  show this help message and exit
  -d, --dry   dry-run (just print list of aps)
```

### `input.csv` format

`building-name,mesh-role,floor-number,mac-address,ap-name`

Ex:
```
Randolph,Portal,1,A8FFDEADBEEF,randolph-cafe-ap1
Randolph,Portal,1,A8FFDEADBEEF,randolph-f1-ap1
Randolph,Point,1,20FFDEADBEEF,randolph-f2-ap1
Randolph,Point,1,20FFDEADBEEF,randolph-f2-ap2
```

### `credentials.py`

The credentials used to connect to the Mobility Master/Controller API are contained in a file named `credentials.py`. This must be created in the same directory as the script, and formatted like the following (whitespace doesn't really matter just needs to be a proper pythonic `dict` object):

```
api = {
    'username' : 'changeme',
    'password' : 'changeme',
    'base_url' : 'https://<controller IP>:4343/v1',
    'ox60_config_path' : 'configpath=/md/wrls-cluster/<controller MAC>'
    'base_ap_group' : 'changeme'
}
```

## Authors

* **Connor Quick** - *Initial development* - connor_quick@harvard.edu
