from clinv.sources import HetznerCloudVMsrc
from tests.sources import ClinvSourceBaseTestClass
import unittest

class TestHetznerCloudVMSource(ClinvSourceBaseTestClass, unittest.TestCase):
    '''
    Test the HetznerCloudVM implementation in the inventory.
    '''

    def setUp(self):
        super().setUp()
        self.source_obj = HetznerCloudVMsrc

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
        }
        self.desired_user_data = {
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data,
            self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data,
            self.desired_source_data,
        )

    @unittest.skip('Not yet')
    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data,
            self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data,
            self.desired_user_data,
        )

    @unittest.skip('Not yet')
    def test_generate_user_data_doesnt_loose_existing_data(self):
        user_key = [key for key in self.desired_user_data.keys()][0]
        desired_user_data = {user_key: {}}
        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data,
            desired_user_data,
        )

    @unittest.skip('Not yet')
    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @unittest.skip('Not yet')
    @patch('clinv.sources.hetnzer.HetznerCloudVM')
    def test_generate_inventory_creates_expected_dictionary(
        self,
        resource_mock
    ):
        resource_id = 's3_bucket_name'
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with(
                {
                    resource_id: desired_mock_input
                },
            ),
            None,
        )

        self.assertEqual(
            desired_inventory,
            {
                resource_id: resource_mock.return_value
            },
        )

class TestHetznerCloudVM(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = ''
        self.raw = {
        }
        self.resource = HetznerCloudVM(self.raw)

    def tearDown(self):
        super().tearDown()
