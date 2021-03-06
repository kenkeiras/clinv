import logging
import unittest
from unittest.mock import call, patch
from clinv.cli import load_parser, load_logger


class TestArgparse(unittest.TestCase):
    def setUp(self):
        self.parser = load_parser()

    def test_can_specify_data_path(self):
        parsed = self.parser.parse_args(['-d', '/tmp/inventory.yaml'])
        self.assertEqual(parsed.data_path, '/tmp/inventory.yaml')

    def test_default_data_path(self):
        parsed = self.parser.parse_args([])
        self.assertEqual(
            parsed.data_path,
            '~/.local/share/clinv',
        )

    def test_can_specify_search_subcommand(self):
        parsed = self.parser.parse_args(['search', 'instance_name'])
        self.assertEqual(parsed.subcommand, 'search')
        self.assertEqual(parsed.search_string, 'instance_name')

    def test_can_specify_generate_subcommand(self):
        parsed = self.parser.parse_args(['generate'])
        self.assertEqual(parsed.subcommand, 'generate')

    def test_unassigned_subcommand_defaults_to_all(self):
        parsed = self.parser.parse_args(['unassigned'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'all')

    def test_can_specify_unassigned_ec2_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'ec2'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'ec2')

    def test_can_specify_unassigned_rds_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'rds'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'rds')

    def test_can_specify_unassigned_services_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'services'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'services')

    def test_can_specify_unassigned_people_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'people'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'people')

    def test_can_specify_unassigned_iam_users_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'iam_users'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'iam_users')

    def test_can_specify_unassigned_iam_groups_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'iam_groups'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'iam_groups')

    def test_can_specify_unassigned_informations_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'informations'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'informations')

    def test_can_specify_unassigned_route53_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'route53'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'route53')

    def test_can_specify_list_rds_subcommand(self):
        parsed = self.parser.parse_args(['list', 'rds'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'rds')

    def test_can_specify_list_ec2_subcommand(self):
        parsed = self.parser.parse_args(['list', 'ec2'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'ec2')

    def test_can_specify_list_services_subcommand(self):
        parsed = self.parser.parse_args(['list', 'services'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'services')

    def test_can_specify_list_informations_subcommand(self):
        parsed = self.parser.parse_args(['list', 'informations'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'informations')

    def test_can_specify_list_people_subcommand(self):
        parsed = self.parser.parse_args(['list', 'people'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'people')

    def test_can_specify_list_iam_users_subcommand(self):
        parsed = self.parser.parse_args(['list', 'iam_users'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'iam_users')

    def test_can_specify_export_subcommand(self):
        parsed = self.parser.parse_args(['export'])
        self.assertEqual(parsed.subcommand, 'export')

    def test_export_has_default_file(self):
        parsed = self.parser.parse_args(['export'])
        self.assertEqual(
            parsed.export_path,
            '~/.local/share/clinv/inventory.ods'
        )

    def test_export_can_specify_file_path(self):
        parsed = self.parser.parse_args(['export', 'file.ods'])
        self.assertEqual(parsed.export_path, 'file.ods')

    def test_can_specify_print_subcommand(self):
        parsed = self.parser.parse_args(['print', 'resource_id'])
        self.assertEqual(parsed.subcommand, 'print')
        self.assertEqual(parsed.search_string, 'resource_id')


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.logging_patch = patch('clinv.cli.logging', autospect=True)
        self.logging = self.logging_patch.start()

        self.logging.DEBUG = 10
        self.logging.INFO = 20
        self.logging.WARNING = 30
        self.logging.ERROR = 40

    def tearDown(self):
        self.logging_patch.stop()

    def test_logger_is_configured_by_default(self):
        load_logger()
        self.assertEqual(
            self.logging.addLevelName.assert_has_calls(
                [
                    call(logging.INFO, '[\033[36mINFO\033[0m]'),
                    call(logging.ERROR, '[\033[31mERROR\033[0m]'),
                    call(logging.DEBUG, '[\033[32mDEBUG\033[0m]'),
                    call(logging.WARNING, '[\033[33mWARNING\033[0m]'),
                ]
            ),
            None
        )
        self.assertEqual(
            self.logging.basicConfig.assert_called_with(
                level=logging.INFO,
                format="  %(levelname)s %(message)s",
            ),
            None
        )
