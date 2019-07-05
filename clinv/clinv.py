#!/usr/bin/python3

# Copyright (C) 2019 lyz <lyz@riseup.net>
# This file is part of clinv.
#
# clinv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# clinv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with clinv.  If not, see <http://www.gnu.org/licenses/>.

# Program to maintain an inventory of assets.

from clinv.aws import EC2Instance
from collections import OrderedDict
from operator import itemgetter
from yaml import YAMLError
import boto3
import logging
import os
import pyexcel
import re
import yaml


class Clinv():
    def __init__(self, inventory_dir):
        self.log = logging.getLogger('main')
        self.ec2 = boto3.client('ec2')
        self.inventory_dir = inventory_dir
        self.raw_inv_path = os.path.join(
            self.inventory_dir,
            'raw_inventory.yaml',
        )
        self.raw_data_path = os.path.join(
            self.inventory_dir,
            'raw_data.yaml',
        )
        self.raw_data = {
            'ec2': {},
        }

    def _update_raw_ec2(self):
        self.raw_inv = {
            'ec2': [],
        }
        self.raw_inv['ec2'] = \
            self.ec2.describe_instances()['Reservations']

        prune_keys = [
            'AmiLaunchIndex',
            'Architecture',
            'BlockDeviceMappings',
            'CapacityReservationSpecification',
            'ClientToken',
            'CpuOptions',
            'EbsOptimized',
            'HibernationOptions',
            'Hypervisor',
            'ImageId',
            'KeyName',
            'LaunchTime',
            'Monitoring',
            'Placement',
            'PrivateDnsName',
            'PrivateIpAddress',
            'ProductCodes',
            'PublicDnsName',
            'PublicIpAddress',
            'RootDeviceName',
            'RootDeviceType',
            'SourceDestCheck',
            'SubnetId',
            'VirtualizationType',
        ]
        network_prune_keys = [
            'Association',
            'Attachment',
            'Description',
            'Groups',
            'InterfaceType',
            'Ipv6Addresses',
            'MacAddress',
            'NetworkInterfaceId',
            'OwnerId',
            'PrivateDnsName',
            'PrivateIpAddress',
            'SourceDestCheck',
            'Status',
            'SubnetId',
            'VpcId',
        ]

        for resource in self.raw_inv['ec2']:
            for instance in resource['Instances']:
                for prune_key in prune_keys:
                    try:
                        instance.pop(prune_key)
                    except KeyError:
                        pass
                for interface in instance['NetworkInterfaces']:
                    for prune_key in network_prune_keys:
                        try:
                            interface.pop(prune_key)
                        except KeyError:
                            pass

    def _update_raw_inventory(self):
        self._update_raw_ec2()

    def _update_inventory(self):
        self.inv = {
            'ec2': {},
        }
        for resource in self.raw_inv['ec2']:
            for instance in resource['Instances']:
                instance_id = instance['InstanceId']
                try:
                    self.raw_data['ec2'][instance_id]
                except KeyError:
                    self.raw_data['ec2'][instance_id] = {
                        'description': '',
                        'to_destroy': False,
                        'environment': 'production',
                    }
                for key, value in \
                        self.raw_data['ec2'][instance_id].items():
                    instance[key] = value

                self.inv['ec2'][instance_id] = EC2Instance(instance)

    def _save_yaml(self, yaml_path, dictionary):
        'Save variable to yaml'

        with open(os.path.expanduser(yaml_path), 'w+') as f:
            yaml.dump(dictionary, f, default_flow_style=False)

    def save_inventory(self):
        self._save_yaml(self.raw_inv_path, self.raw_inv)
        self._save_yaml(self.raw_data_path, self.raw_data)

    def _load_yaml(self, yaml_path):
        'Load YAML to variable'
        try:
            with open(os.path.expanduser(yaml_path), 'r') as f:
                try:
                    return yaml.safe_load(f)
                except YAMLError as e:
                    self.log.error(e)
                    raise
        except FileNotFoundError as e:
            self.log.error('Error opening yaml file {}'.format(yaml_path))
            raise(e)

    def load_inventory(self):
        self.raw_inv = self._load_yaml(self.raw_inv_path)

    def load_data(self):
        self.raw_data = self._load_yaml(self.raw_data_path)
        if self.raw_data is None:
            self.raw_data = {
                'ec2': {},
            }
        self._update_inventory()

    def _search_ec2(self, search_string):
        result = []
        for instance_id, instance in self.inv['ec2'].items():
            if instance.search(search_string) is True:
                result.append(instance)
        return result

    def _match_dictionary_field(self, resource, search_string, field):
        try:
            if re.match(search_string, str(resource[field]), re.IGNORECASE):
                return True
        except KeyError:
            pass
        return False

    def _search_raw_data_resource(self, resource_type, search_string):
        result = []
        try:
            self.raw_data[resource_type]
        except KeyError:
            return result

        for resource_id, resource in self.raw_data[resource_type].items():
            # Search by name
            if self._match_dictionary_field(
                resource,
                search_string,
                'name',
            ):
                result.append(resource_id)
                continue

            # Search by aliases
            if self._match_dictionary_field(
                resource,
                search_string,
                'aliases',
            ):
                result.append(resource_id)
                continue

            # Search by description
            if self._match_dictionary_field(
                resource,
                search_string,
                'description',
            ):
                result.append(resource_id)
                continue
        return result

    def _search_projects(self, search_string):
        return self._search_raw_data_resource('projects', search_string)

    def _search_services(self, search_string):
        return self._search_raw_data_resource('services', search_string)

    def _search_informations(self, search_string):
        return self._search_raw_data_resource('informations', search_string)

    def _print_raw_data_resources(self, resource_type, resource_ids):
        for resource_id in sorted(resource_ids):
            print('{}: {}'.format(
                resource_id,
                self.raw_data[resource_type][resource_id]['name'],
            ))

    def print_search(self, search_string):
        pro_ids = self._search_projects(search_string)

        if pro_ids != []:
            print('Type: Projects')
            self._print_raw_data_resources('projects', pro_ids)

        ser_ids = self._search_services(search_string)

        if ser_ids != []:
            print('\nType: Services')
            self._print_raw_data_resources('services', ser_ids)

        inf_ids = self._search_informations(search_string)

        if inf_ids != []:
            print('\nType: Informations')
            self._print_raw_data_resources('informations', inf_ids)

        ec2_instances = self._search_ec2(search_string)

        if ec2_instances != []:
            print('\nType: EC2 instances')
            for instance in ec2_instances:
                instance.print()

        if ec2_instances == [] and \
                pro_ids == [] and \
                ser_ids == [] and \
                inf_ids == []:
            print('I found nothing with that search_string')
            return

    def _unassigned_ec2(self):
        all_assigned_instances = []
        for service_id, service in sorted(self.raw_data['services'].items()):
            try:
                for instance in service['aws']['ec2']:
                    all_assigned_instances.append(instance)
            except TypeError:
                pass

        for instance_id, instance in sorted(self.inv['ec2'].items()):
            if instance_id not in all_assigned_instances:
                if instance.state != 'terminated':
                    print('{}: {}'.format(instance.id, instance.name))

    def _unassigned_services(self):
        all_assigned_services = []
        for project_id, project in sorted(self.raw_data['projects'].items()):
            try:
                for service in project['services']:
                    all_assigned_services.append(service)
            except TypeError:
                pass

        for service_id, service in sorted(self.raw_data['services'].items()):
            if service_id not in all_assigned_services:
                print('{}: {}'.format(service_id, service['name']))

    def _unassigned_informations(self):
        all_assigned_informations = []
        for project_id, project in self.raw_data['projects'].items():
            try:
                for information in project['informations']:
                    all_assigned_informations.append(information)
            except TypeError:
                pass

        for information_id, information in \
                sorted(self.raw_data['informations'].items()):
            if information_id not in all_assigned_informations:
                print('{}: {}'.format(information_id, information['name']))

    def unassigned(self, resource_type):
        if resource_type == 'ec2':
            self._unassigned_ec2()
        elif resource_type == 'services':
            self._unassigned_services()
        elif resource_type == 'informations':
            self._unassigned_informations()

    def _list_raw_data_resource(self, resource_type):
        self._print_raw_data_resources(
            resource_type,
            self.raw_data[resource_type].keys()
        )

    def _list_informations(self):
        self._list_raw_data_resource('informations')

    def _list_projects(self):
        self._list_raw_data_resource('projects')

    def _list_services(self):
        not_terminated_service_ids = []
        for service_id, service in self.raw_data['services'].items():
            try:
                if service['state'] != 'terminated':
                    not_terminated_service_ids.append(service_id)
            except KeyError:
                raise KeyError(
                    "{} doesn't have the state defined".format(service_id)
                )
        self._print_raw_data_resources('services', not_terminated_service_ids)

    def _list_ec2(self):
        for instance_id, instance in self.inv['ec2'].items():
            print('{}: {}'.format(instance.id, instance.name))

    def list(self, resource_type):
        if resource_type == 'ec2':
            self._list_ec2()
        elif resource_type == 'services':
            self._list_services()
        elif resource_type == 'informations':
            self._list_informations()
        elif resource_type == 'projects':
            self._list_projects()

    def export(self, export_path):
        # Create ec2 sheet
        exported_ec2_headers = [
            'ID',
            'Name',
            'Services',
            'To destroy',
            'Responsible',
            'Comments'
        ]

        # Fill up content
        exported_ec2_data = []
        for instance_id, instance in self.inv['ec2'].items():
            related_services = {
                service_id: service
                for service_id, service in self.raw_data['services'].items()
                for ec2_instance in service['aws']['ec2']
                if ec2_instance == instance_id
            }

            exported_ec2_data.append(
                [
                    instance_id,
                    instance.name,
                    ', '.join(
                        [
                            service['name']
                            for service_id, service in related_services.items()
                        ]
                    ),
                    instance._get_field('to_destroy'),
                    ', '.join(set(
                        [
                            service['responsible']
                            for service_id, service in related_services.items()
                        ]
                    )),
                    instance.description,
                ]
            )
        # Sort by name
        exported_ec2_data = sorted(exported_ec2_data, key=itemgetter(1))
        exported_ec2_data.insert(0, exported_ec2_headers)

        # Create ods book

        book = OrderedDict()
        book.update({'EC2 Instances': exported_ec2_data})

        pyexcel.save_book_as(
            bookdict=book,
            dest_file_name=os.path.expanduser(export_path),
        )

    @property
    def regions(self):
        ec2 = boto3.client('ec2')
        return [
            region['RegionName']
            for region in ec2.describe_regions()['Regions']
        ]
