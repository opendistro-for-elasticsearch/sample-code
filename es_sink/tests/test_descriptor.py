import sys
sys.path.append("../es_sink")


import unittest


import es_sink.es_auth as es_auth
import es_sink.descriptor
import es_sink.transport_utils

class TestDescriptor(unittest.TestCase):

    TS_ID6 = es_sink.descriptor.IndexDescriptor(es_index='logs',
                                                es_type='log',
                                                es_v7=False,
                                                timestamped=True)
    TS_ID7 = es_sink.descriptor.IndexDescriptor(es_index='logs',
                                                es_v7=True,
                                                timestamped=True)

    NO_TS_ID6 = es_sink.descriptor.IndexDescriptor(es_index='logs',
                                                   es_type='log',
                                                   es_v7=False,
                                                   timestamped=False)
    NO_TS_ID7 = es_sink.descriptor.IndexDescriptor(es_index='logs',
                                                   es_v7=True,
                                                   timestamped=False)

    ACTION_LINE_6 = '{{"index" : {{ "_index" : "logs{}", "_type": "log" }} }}'
    ACTION_LINE_7 = '{{"index" : {{ "_index" : "logs{}" }} }}'

    def test_index_descriptor_defaults(self):
        idx = es_sink.descriptor.IndexDescriptor()
        self.assertIsNone(idx.es_index)
        self.assertIsNone(idx.es_type)
        self.assertTrue(idx.es_v7)
        self.assertTrue(idx.timestamped)

    def test_es_auth(self):
        auth = es_auth.ESHttpAuth('admin', 'admin')
        auth = es_auth.ESNoAuth()
        auth = es_auth.ESSigV4Auth()

    def test_create(self):
        auth = es_auth.ESHttpAuth('admin', 'admin')
        index_descriptor = self.TS_ID6
        desc = es_sink.descriptor.ESDescriptor("https://localhost:9200/",
                                               index_descriptor,
                                               auth=auth)

    def test_missing_user_pass_region(self):
        auth = es_auth.ESNoAuth()
        index_descriptor = self.TS_ID7
        desc = es_sink.descriptor.ESDescriptor("https://localhost:9200/",
                                               index_descriptor,
                                               auth=auth)
        self.assertRaises(ValueError, desc.user_password)
        self.assertIsNone(desc.region)

    def test_auth(self):
        auth = es_auth.ESNoAuth()
        index_descriptor = es_sink.descriptor.IndexDescriptor()
        desc = es_sink.descriptor.ESDescriptor("https://localhost:9200/",
                                               index_descriptor,
                                               auth=auth)
        self.assertFalse(desc.is_signed())
        self.assertFalse(desc.is_http_auth())

        auth = es_auth.ESSigV4Auth()
        desc = es_sink.descriptor.ESDescriptor("https://localhost:9200/",
                                               index_descriptor,
                                               region='us-west-2',
                                               auth=auth)
        self.assertTrue(desc.is_signed())
        self.assertFalse(desc.is_http_auth())

        auth = es_auth.ESHttpAuth('admin', 'adminpw')
        desc = es_sink.descriptor.ESDescriptor("https://localhost:9200/",
                                               index_descriptor,
                                               region='us-west-2',
                                               auth=auth)
        self.assertFalse(desc.is_signed())
        self.assertTrue(desc.is_http_auth())

    def test_index_naming_logs6(self):
        auth = es_auth.ESNoAuth()
        base_url = "https://localhost:9200/"
        # Small chance this will fail at midnight. Who's running unit tests at
        # midnight anyway.
        timestamp = es_sink.transport_utils.now_pst().strftime("%Y.%m.%d")
        index_suffix = '-' + timestamp
        url6 = '{}logs{}/log/'.format(base_url, index_suffix)
        desc = es_sink.descriptor.ESDescriptor(base_url, self.TS_ID6, auth=auth)

        self.assertTrue(desc.timestamped())
        self.assertEqual(desc.base_url(), base_url)

        self.assertEqual(desc.base_url_with_index(),
                         '{}logs{}/'.format(base_url, index_suffix))
        self.assertEqual(desc.base_url_6(), url6)
        self.assertEqual(desc.bulk_url(), desc.base_url_with_index() + "_bulk")
        self.assertEqual(desc.search_url(), "{}logs{}/log/_search".format(
                         base_url, index_suffix))
        self.assertEqual(desc.bulk_control_line(),
                         self.ACTION_LINE_6.format(index_suffix))

    def test_index_naming_logs7(self):
        auth = es_auth.ESNoAuth()
        base_url = "https://localhost:9200/"
        # Small chance this will fail at midnight. Who's running unit tests at
        # midnight anyway.
        timestamp = es_sink.transport_utils.now_pst().strftime("%Y.%m.%d")
        index_suffix = '-' + timestamp
        url7 = '{}logs{}/'.format(base_url, index_suffix)
        desc = es_sink.descriptor.ESDescriptor(base_url, self.TS_ID7, auth=auth)

        self.assertTrue(desc.timestamped())
        self.assertEqual(desc.base_url(), base_url)

        self.assertEqual(desc.base_url_with_index(),
                         '{}logs{}/'.format(base_url, index_suffix))
        self.assertEqual(desc.base_url_7(), url7)
        self.assertEqual(desc.bulk_url(), desc.base_url_with_index() + "_bulk")
        self.assertEqual(desc.search_url(), "{}logs{}/_search".format(
                         base_url, index_suffix))
        self.assertEqual(desc.bulk_control_line(),
                         self.ACTION_LINE_7.format(index_suffix))

    def test_untimestamped6(self):
        auth = es_auth.ESNoAuth()
        base_url = "https://localhost:9200/"
        index_suffix = ''
        url6 = '{}logs{}/log/'.format(base_url, index_suffix)
        desc = es_sink.descriptor.ESDescriptor(base_url, self.NO_TS_ID6,
                                               auth=auth)

        self.assertFalse(desc.timestamped())
        self.assertEqual(desc.base_url(), base_url)

        self.assertEqual(desc.base_url_with_index(),
                         '{}logs{}/'.format(base_url, index_suffix))
        self.assertEqual(desc.base_url_6(), url6)
        self.assertEqual(desc.bulk_url(), desc.base_url_with_index() + "_bulk")
        self.assertEqual(desc.search_url(), "{}logs{}/log/_search".format(
                         base_url, index_suffix))
        self.assertEqual(desc.bulk_control_line(),
                         self.ACTION_LINE_6.format(index_suffix))

    def test_untimestamped7(self):
        auth = es_auth.ESNoAuth()
        base_url = "https://localhost:9200/"
        index_suffix = ''
        url7 = '{}logs{}/'.format(base_url, index_suffix)
        desc = es_sink.descriptor.ESDescriptor(base_url, self.NO_TS_ID7,
                                               auth=auth)

        self.assertFalse(desc.timestamped())
        self.assertEqual(desc.base_url(), base_url)

        self.assertEqual(desc.base_url_with_index(),
                         '{}logs{}/'.format(base_url, index_suffix))
        self.assertEqual(desc.base_url_7(), url7)
        self.assertEqual(desc.bulk_url(), desc.base_url_with_index() + "_bulk")
        self.assertEqual(desc.search_url(), "{}logs{}/_search".format(
                         base_url, index_suffix))
        self.assertEqual(desc.bulk_control_line(),
                         self.ACTION_LINE_7.format(index_suffix))




if __name__ == '__main__':
    unittest.main()