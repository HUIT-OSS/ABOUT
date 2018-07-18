#!/usr/bin/env python3
"""Module to provision APs."""

import argparse
import csv
import json
import warnings
import requests
import credentials

class AP:
    """Class to interact with API to provision APs."""
    def __init__(self):
        """Create API session and save login cookie."""
        self.base_url = credentials.api['base_url']
        self.config_path = credentials.api['config_path']
        self.session = requests.session()
        self.login(self.session)

    def rename(self, serial, name):
        """Renames an AP by serial number."""
        url = "{}/configuration/object/ap_rename?{}&UIDARUBA={}".format(
            self.base_url,
            self.config_path,
            self.uidaruba)

        obj_dict = {'serial-num': serial, 'new-name': name}
        obj_json = json.loads(json.dumps(obj_dict))

        resp = self.post(url, obj_json)

        print(resp.status_code)
        print(resp.text)

    def regroup(self, serial, group):
        """Moves an AP to a new ap-group by serial number."""
        url = "{}/configuration/object/ap_regroup?{}&UIDARUBA={}".format(
            self.base_url,
            self.config_path,
            self.uidaruba)

        obj_dict = {'serial-num': serial, 'new-group': group}
        obj_json = json.loads(json.dumps(obj_dict))

        resp = self.post(url, obj_json)

        print(resp.status_code)
        print(resp.text)

    def clear_list(self):
        """Runs the `clear_provisioning_ap_list` to prepare to provision a new AP."""
        clear_list_url = "{}/configuration/object/clear_provisioning_ap_list?{}&UIDARUBA={}".format(
            self.base_url,
            self.config_path,
            self.uidaruba)

        clear_list_dict = {"_action": "modify"}
        clear_list_json = json.loads(json.dumps(clear_list_dict))
        clear_list_resp = self.post(clear_list_url, clear_list_json)
        print("clear_list_resp: {}".format(clear_list_resp.status_code))
        # print(clear_list_resp.text)

    def read_bootinfo(self, orig_name):
        """Runs the 'read_bootinfo' API call to fetch existing paramaters from the AP."""
        read_bootinfo_url = "{}/configuration/object/read_bootinfo?{}&UIDARUBA={}".format(
            self.base_url,
            self.config_path,
            self.uidaruba)

        read_bootinfo_dict = {"_action": "modify",
                              "read_bootinfo_option": "ap-name",
                              "ap-name": orig_name
                              }

        read_bootinfo_json = json.loads(json.dumps(read_bootinfo_dict))
        read_bootinfo_resp = self.post(read_bootinfo_url, read_bootinfo_json)
        print("read_bootinfo_resp: {}".format(read_bootinfo_resp.status_code))
        # print(read_bootinfo_resp.text)

    def copy_prov(self, orig_name):
        """Runs the `copy_provisioning_params` API call to copy the parameters to modify."""
        copy_prov_url = "{}/configuration/object/copy_provisioning_params?{}&UIDARUBA={}".format(
            self.base_url,
            self.config_path,
            self.uidaruba)

        copy_prov_dict = {"_action": "modify",
                          "ap-name": orig_name,
                          "copy_provisioning_options": "ap-name"
                          }

        copy_prov_json = json.loads(json.dumps(copy_prov_dict))
        copy_prov_resp = self.post(copy_prov_url, copy_prov_json)
        print("copy_prov_resp: {}".format(copy_prov_resp.status_code))
        # print(copy_prov_resp.text)

    def ap_prov(self, new_name, mesh_role):
        """Runs the `ap_prov` API call to push the modified AP parameters."""
        ap_group = credentials.api['mesh_group_base'] + mesh_role
        ap_prov_url = "{}/configuration/object/ap_prov?{}&UIDARUBA={}".format(
            self.base_url,
            self.config_path,
            self.uidaruba)

        ap_prov_dict = {"_action": "modify",
                        "ap_name": {"_action": "modify", "ap-name": new_name},
                        "ap_group": {"_action": "modify", "ap-group": ap_group},
                        "mesh_role": {"_action": "modify", "mesh_role_sel": mesh_role}
                        }

        if mesh_role == "mesh-portal":
            ap_prov_dict["a_ant_gain"] = {"_action": "modify", "a-ant-gain": "5.5"}
            ap_prov_dict["g_ant_gain"] = {"_action": "modify", "g-ant-gain": "3.5"}

        ap_prov_json = json.loads(json.dumps(ap_prov_dict))
        ap_prov_resp = self.post(ap_prov_url, ap_prov_json)
        print("ap_prov_resp: {}".format(ap_prov_resp.status_code))
        # print(ap_prov_resp.text)


    def ap_reprovision(self, orig_name):
        """Runs the `ap_reprovision` API call to push the config to the AP and reboot."""
        ap_reprovision_url = "{}/configuration/object/ap_reprovision?{}&UIDARUBA={}".format(
            self.base_url,
            self.config_path,
            self.uidaruba)

        ap_reprovision_dict = {"_action": "modify",
                               "ap-name": orig_name,
                               "reprovision_option": "ap-name"
                               }

        ap_reprovision_json = json.loads(json.dumps(ap_reprovision_dict))
        ap_reprovision_resp = self.post(ap_reprovision_url, ap_reprovision_json)
        print("ap_reprovision_resp: {}".format(ap_reprovision_resp.status_code))
        # print(ap_reprovision_resp.text)

    def provision(self, orig_name, new_name, mesh_role):
        """Executes the various steps required to provision an AP."""
        self.clear_list()
        self.read_bootinfo(orig_name)
        self.copy_prov(orig_name)
        self.ap_prov(new_name, mesh_role)
        self.ap_reprovision(orig_name)

    def post(self, url, obj):
        """POSTs a JSON object to a URL."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return self.session.post(url, json=obj, verify=False)


    def login(self):
        """Returns the UIDARUBA session cookie."""
        url = self.base_url + "/api/login"
        creds = {'username' : credentials.api['username'],
                 'password' : credentials.api['password']}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            resp = session.post(url, creds, verify=False)

        self.uidaruba = json.loads(resp.text)['_global_result']['UIDARUBA']

def main():
    """Runs through a CSV to provision APs based on building name and floor number."""
    parser = argparse.ArgumentParser(description='Provision APs (303H/334)')
    parser.add_argument('-d', '--dry', help='dry-run (just print list of aps)', action='store_true')
    parser.add_argument('building', help="building name")
    parser.add_argument('floor', help="floor number")
    args = parser.parse_args()

    if not args.dry:
        print("ap provisioning!")
        # ap = AP()

    with open("input.csv", 'r') as file_in:
        csv_data = csv.reader(file_in, delimiter=',')

        for line in csv_data:
            building = line[0].lower()
            role = line[1].lower()
            floor = line[2]
            mac = ':'.join(a+b for a, b in zip(line[3][::2], line[3][1::2])).lower()
            name = line[4]

            if building == args.building and floor == args.floor:
                print("Role: {}, MAC: {}, Name: {}".format(role, mac, name))

                if not args.dry:
                    print("provisioning!")
                    # ap.provision(mac, name, "mesh-{}".format(role))


if __name__ == "__main__":
    main()
