#!/usr/bin/env python3
"""Module to provision APs."""

import argparse
import csv
import json
import warnings
import requests
import credentials


class Controller:
    """Class to interact with API to provision APs."""

    def __init__(self):
        """Create API session and save login cookie."""
        self.base_url = credentials.api['base_url']
        self.config_path = credentials.api['config_path']
        self.group_base = credentials.api['group_base']
        self.session = requests.session()
        self.login()

    def rename(self, serial, name):
        """Renames an AP by serial number."""
        api_page = "/configuration/object/ap_rename"
        url = "{}{}?{}&UIDARUBA={}".format(
            self.base_url,
            api_page,
            self.config_path,
            self.uidaruba)

        obj_dict = {'serial-num': serial, 'new-name': name}
        obj_json = json.loads(json.dumps(obj_dict))

        resp = self.post(url, obj_json)

        print(resp.status_code)
        print(resp.text)

    def regroup(self, serial, group):
        """Moves an AP to a new ap-group by serial number."""
        api_page = "/configuration/object/ap_regroup"
        url = "{}{}?{}&UIDARUBA={}".format(
            self.base_url,
            api_page,
            self.config_path,
            self.uidaruba)

        obj_dict = {'serial-num': serial, 'new-group': group}
        obj_json = json.loads(json.dumps(obj_dict))

        resp = self.post(url, obj_json)

        print(resp.status_code)
        print(resp.text)

    def clear_list(self):
        """Prepares the controller to provision a new AP"""
        api_page = "/configuration/object/clear_provisioning_ap_list"
        url = "{}{}?{}&UIDARUBA={}".format(
            self.base_url,
            api_page,
            self.config_path,
            self.uidaruba)

        obj = {"_action": "modify"}
        json_obj = json.loads(json.dumps(obj))
        resp = self.post(url, json_obj)
        print("clear_list_resp: {}".format(resp.status_code))
        # print(resp.text)

    def read_bootinfo(self, orig_name):
        """Fetch existing paramaters from the AP."""
        api_page = "/configuration/object/read_bootinfo"
        url = "{}{}?{}&UIDARUBA={}".format(
            self.base_url,
            api_page,
            self.config_path,
            self.uidaruba)

        obj = {"_action": "modify",
               "read_bootinfo_option": "ap-name",
               "ap-name": orig_name
               }

        json_obj = json.loads(json.dumps(obj))
        resp = self.post(url, json_obj)
        print("read_bootinfo_resp: {}".format(resp.status_code))
        # print(resp.text)

    def copy_prov(self, orig_name):
        """Copy the existing parameters to modify."""
        api_page = "/configuration/object/copy_provisioning_params"
        url = "{}{}?{}&UIDARUBA={}".format(
            self.base_url,
            api_page,
            self.config_path,
            self.uidaruba)

        obj = {"_action": "modify",
               "ap-name": orig_name,
               "copy_provisioning_options": "ap-name"
               }

        json_obj = json.loads(json.dumps(obj))
        resp = self.post(url, json_obj)
        print("copy_prov_resp: {}".format(resp.status_code))
        # print(resp.text)

    def ap_prov(self, new_name, mesh_role):
        """Runs the `ap_prov` API call to push the modified AP parameters."""
        api_page = "/configuration/object/ap_prov"
        ap_group = self.group_base + mesh_role
        url = "{}{}?{}&UIDARUBA={}".format(
            self.base_url,
            api_page,
            self.config_path,
            self.uidaruba)

        obj = {"_action": "modify",
               "ap_name": {"_action": "modify",
                           "ap-name": new_name},
               "ap_group": {"_action": "modify",
                            "ap-group": ap_group},
               "mesh_role": {"_action": "modify",
                             "mesh_role_sel": mesh_role}
               }

        if mesh_role == "mesh-portal":
            obj["a_ant_gain"] = {"_action": "modify",
                                 "a-ant-gain": "5.5"}
            obj["g_ant_gain"] = {"_action": "modify",
                                 "g-ant-gain": "3.5"}

        json_obj = json.loads(json.dumps(obj))
        resp = self.post(url, json_obj)
        print("ap_prov_resp: {}".format(resp.status_code))
        # print(resp.text)

    def ap_reprovision(self, orig_name):
        """Push the config to the AP and reboot."""
        api_page = "/configuration/object/ap_reprovision"
        url = "{}{}?{}&UIDARUBA={}".format(
            self.base_url,
            api_page,
            self.config_path,
            self.uidaruba)

        obj = {"_action": "modify",
               "ap-name": orig_name,
               "reprovision_option": "ap-name"
               }

        json_obj = json.loads(json.dumps(obj))
        resp = self.post(url, json_obj)
        print("ap_reprovision_resp: {}".format(resp.status_code))
        # print(resp.text)

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
        """Sets the UIDARUBA session cookie."""
        url = self.base_url + "/api/login"
        creds = {'username': credentials.api['username'],
                 'password': credentials.api['password']}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            resp = self.session.post(url, creds, verify=False)

        self.uidaruba = json.loads(resp.text)['_global_result']['UIDARUBA']

    def logout(self):
        """Logs out from the controller."""
        url = self.base_url + "/api/logout"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            resp = self.session.post(url, verify=False)

        print(json.loads(resp.text)['_global_result']['status_str'])


def args_handler():
    """Handles the argparse stuff."""
    parser = argparse.ArgumentParser(description='Provision APs (303H/334)')
    parser.add_argument('-d', '--dry',
                        help='dry-run (just print list of aps)',
                        action='store_true')
    parser.add_argument('building', help="building name")
    parser.add_argument('floor', help="floor number")
    return parser.parse_args()


def main():
    """Provision APs based on building name and floor number."""
    args = args_handler()

    if not args.dry:
        controller = Controller()

    with open("input.csv", 'r') as file_in:
        csv_data = csv.reader(file_in, delimiter=',')

        for line in csv_data:
            building = line[0].lower()
            role = line[1].lower()
            floor = line[2]
            mac = ':'.join(a+b for a, b in zip(line[3][::2],
                                               line[3][1::2])).lower()
            name = line[4]

            if building == args.building and floor == args.floor:
                print("Role: {}, MAC: {}, Name: {}".format(role, mac, name))

                if not args.dry:
                    controller.provision(mac, name, "mesh-{}".format(role))

    if not args.dry:
        controller.logout()


if __name__ == "__main__":
    main()
