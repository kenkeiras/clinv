from clinv.sources import ClinvSourcesrc, ClinvGenericResource

import os
import json
from hcloud import Client
from hcloud.server_types.domain import ServerType
from hcloud.images.domain import Image


class HetznerCloudVMsrc(ClinvSourcesrc):
    """
    Class to gather and manipulate the HetznerCloudVM resources.

    Parameters:
        source_data (dict): HetznerCloudVMsrc compatible source_data
        dictionary.
        user_data (dict): HetznerCloudVMsrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = 'hetzner-cloud-vm'

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
            }

        Returns:
            dict: content of self.source_data.
        """


        """
        Server model
        ====== =====

        id: int
          ID of the server

        name: str
          Name of the server (must be unique per project and a valid hostname as per RFC 1123)

        status: str
          Status of the server Choices: `running`, `initializing`, `starting`, `stopping`, `off`, `deleting`, `migrating`, `rebuilding`, `unknown`

        created: datetime
          Point in time when the server was created

        public_net: :class:`PublicNetwork <hcloud.servers.domain.PublicNetwork>`
          Public network information.

        server_type: :class:`BoundServerType <hcloud.server_types.client.BoundServerType>`
        datacenter: :class:`BoundDatacenter <hcloud.datacenters.client.BoundDatacenter>`

        image: :class:`BoundImage <hcloud.images.client.BoundImage>`, None
          iso: :class:`BoundIso <hcloud.isos.client.BoundIso>`, None

        rescue_enabled: bool
          True if rescue mode is enabled: Server will then boot into rescue system on next reboot.

        locked: bool
          True if server has been locked and is not available to user.

        backup_window: str, None
          Time window (UTC) in which the backup will run, or None if the backups are not enabled

        outgoing_traffic: int, None
          Outbound Traffic for the current billing period in bytes

        ingoing_traffic: int, None
          Inbound Traffic for the current billing period in bytes

        included_traffic: int
          Free Traffic for the current billing period in bytes

        protection: dict
          Protection configuration for the server

        labels: dict
          User-defined labels (key-value pairs)

        volumes: List[:class:`BoundVolume <hcloud.volumes.client.BoundVolume>`]
          Volumes assigned to this server.

        private_net: List[:class:`PrivateNet <hcloud.servers.domain.PrivateNet`]
          Private networks information.

        """

        self.log.info('Fetching HetznerCloudVM inventory')

        config = json.load(open(os.path.expanduser("~/.hetzner/config.json")))
        client = Client(token=config['token'])
        servers = client.servers.get_all()
        self.source_data = {}

        for server in servers:
            self.source_data[server.name] = {
                "id": server.id,
                "status": server.status,
                "name": server.name,
                "labels": server.labels,
                "created": server.created,
                "datacenter": server.datacenter.id,
                "datacenter_name": server.datacenter.name,
            }

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for id, value in self.source_data.items():
            if id not in self.user_data:
                self.user_data[id] = {
                    'id': value['id'],
                    'description': '',
                    'to_destroy': 'tbd',
                    'environment': 'tbd',
                    'datacenter': value['datacenter'],
                    'datacenter_name': value['datacenter_name'],
                }


        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with HetznerCloudVM resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: HetznerCloudVM inventory with user and source data
        """

        inventory = {}

        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = HetznerCloudVM({resource_id: resource})

        return inventory


class HetznerCloudVM(ClinvGenericResource):
    """
    Abstract class to extend ClinvGenericResource, it gathers method and
    attributes for the HetznerCloudVM resources.

    Public methods:
        print: Prints the name of the resource
        short_print: Prints information of the resource

    Public properties:
        name: Returns the name of the record.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)
