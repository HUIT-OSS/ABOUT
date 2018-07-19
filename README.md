# Automated Aruba AP Provisioning

Python script to interface with the Mobility Master/Controller to process an input CSV file containing APs to provision. We are currently provisioning Aruba 334 APs as mesh-portals, and Aruba 303H APs as mesh-points.

Once we plug the APs for a floor into a PoE switch (with layer 2 access to the Mobility Controller), with factory-default settings they should show up in the controller's web GUI with their ap-names set to their MAC address. Once we see all the APs up in the controller, the script is run by specifying the building and floor corresponding to the connected APs. This will push the new ap-name, ap-group, and mesh-role configuration changes to the APs, then they will reboot. The 334s seem to come back up in ~3-5 mins, while the 303Hs have been taking more like ~10-30 mins.

If an AP is already provisioned, its name will most likely no longer be its MAC address, thus the script will do nothing to it. If an AP fails to show up on the controller, a power-cycle usually will make it appear.

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

The building name argument is not case-sensitive. ie: "perkins" will work for "Perkins" in the CSV.

### `input.csv` format

The `input.csv` file needs to be named `input.csv` in the same directory as `main.py`. A future revision will allow specifying the filename as a command line argument.

`building-name,mesh-role,floor-number,mac-address,ap-name`

Example CSV:
```
Randolph,Portal,1,A8FFDEADBEEF,randolph-cafe-ap1
Randolph,Portal,1,A8FFDEADBEEF,randolph-f1-ap1
Randolph,Point,1,20FFDEADBEEF,randolph-f2-ap1
Randolph,Point,1,20FFDEADBEEF,randolph-f2-ap2
```

The `building-name` and `mesh-role` columns are _not_ case-sensitive. They will be run through the `lower()` function to compare lower-case strings. The `floor-number` column must be an integer. The `mac-address` column will be converted to lower-case and ':' will be inserted every two chars..

### `credentials.py`

The credentials used to connect to the Mobility Master/Controller API are contained in a file named `credentials.py`. This must be created in the same directory as the script, and formatted like the following (whitespace doesn't really matter just needs to be a proper pythonic `dict` object):

```
api = {
    'username' : 'changeme',
    'password' : 'changeme',
    'base_url' : 'https://<mobility-master IP>:4343/v1',
    'config_path' : 'configpath=/md/<cluster-group>/<controller MAC>'
    'ap_group' : 'changeme'
}
```

Configure a username/password for a valid user with API access to provision APs. Specify the Mobility Master IP address, the wireless cluster group name, and the controller's MAC address that the APs are connected to.

The `ap_group` variable will be suffixed by "portal" or "point" for mesh-portals or mesh-points, respectively.

The `config_path` should be shown in the URL bar in the Mobility Master, once the controller is selected. Script might need to be tweaked if pushing right to controller instead of master -- no promises.

## Authors

* **Connor Quick** - *Initial development* - connor_quick@harvard.edu
