#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Unit tests for scrapername.

'''
from collections import OrderedDict
from os.path import join

import pytest
from hdx.data.vocabulary import Vocabulary
from hdx.hdx_configuration import Configuration
from hdx.hdx_locations import Locations
from hdx.location.country import Country
from hdx.utilities.downloader import DownloadError
from hdx.utilities.path import temp_dir

from wfp_foodsecurity import generate_dataset_and_showcase, get_countries


class TestScraperName:
    countrydata = {'code': '50', 'iso3': 'GIN'}

    @pytest.fixture(scope='function')
    def configuration(self):
        Configuration._create(hdx_read_only=True, user_agent='test',
                              project_config_yaml=join('tests', 'config', 'project_configuration.yml'))
        Locations.set_validlocations([{'name': 'gin', 'title': 'Guinea'}])  # add locations used in tests
        Country.countriesdata(use_live=False)
        Vocabulary._tags_dict = True
        Vocabulary._approved_vocabulary = {'tags': [{'name': 'hxl'}, {'name': 'food security'}, {'name': 'indicators'}], 'id': '4e61d464-4943-4e97-973a-84673c1aaa87', 'name': 'approved'}

    @pytest.fixture(scope='function')
    def downloader(self):
        class Response:
            pass

        class Download:
            @staticmethod
            def setup(url, post=False, parameters=None):
                if not post:
                    raise DownloadError()

                response = Response()

                if not 'page' in parameters or parameters['page'] == 0:
                    response.headers = {'Transfer-Encoding': 'chunked'}
                else:
                    response.headers = dict()
                if url == 'http://yyy':
                    return response

            @staticmethod
            def get_json():
                return [OrderedDict([('RowNum', 11), ('ID', 3630), ('SvyID', 48), ('PnlID', 1), ('SvyDate', '2015-06-01T00:00:00'), ('SvyYear', 2015), ('SvyMonth', 'June'), ('SvyMonthNum', 6), ('ADM0_NAME', 'Guinea'), ('ADM1_NAME', None), ('ADM2_NAME', None), ('IndpVars', 'ADM0'), ('Variable', 'rCSI'), ('AdminStrata', 'Guinea'), ('Demographic', None), ('NumObs', 2079), ('Mean', 19.7831), ('StDev', 12.4268), ('CnfIntvHi', 20.55715), ('CnfIntvLo', 19.00906), ('Median', 19.21898), ('Pctl5', 1.0), ('Pctl25', 9.0), ('Pctl75', 30.0), ('Pctl95', 40.0), ('HLAvg', 19.0), ('ADM0_CODE', 106.0)]),
                        OrderedDict([('RowNum', 169), ('ID', 3788), ('SvyID', 48), ('PnlID', 1), ('SvyDate', '2015-06-01T00:00:00'), ('SvyYear', 2015), ('SvyMonth', 'June'), ('SvyMonthNum', 6), ('ADM0_NAME', 'Guinea'), ('ADM1_NAME', None), ('ADM2_NAME', None), ('IndpVars', 'HoHSex,ToiletTypeGrp'), ('Variable', 'rCSI'), ('AdminStrata', None), ('Demographic', 'F,Bush pit latrine'), ('NumObs', 80), ('Mean', 25.79668), ('StDev', 12.32078), ('CnfIntvHi', 29.15365), ('CnfIntvLo', 22.4397), ('Median', 28.0), ('Pctl5', 1.41855), ('Pctl25', 18.0), ('Pctl75', 34.80567), ('Pctl95', 45.49957), ('HLAvg', 24.0), ('ADM0_CODE', 106.0)])]

            @staticmethod
            def get_tabular_rows(url, **kwargs):
                if url == 'config/adm0code.csv':
                    return ['ADM0_CODE', 'ADM0_NAME'], [{'ADM0_CODE': '50', 'ADM0_NAME': 'Guinea'}]

        return Download()

    def test_get_countries(self, downloader):
        countriesdata = get_countries('config/adm0code.csv', downloader)
        assert countriesdata == [TestScraperName.countrydata]

    def test_generate_dataset_and_showcase(self, configuration, downloader):
        showcase_url = 'https://vam.wfp.org/CountryPage_assessments.aspx?iso3=%s'
        variables = {'rCSI': 'reduced coping strategy'}
        with temp_dir('wfp-foodsecurity') as folder:
            dataset, showcase, bites_disabled = generate_dataset_and_showcase('http://yyy', showcase_url, downloader, folder, TestScraperName.countrydata, variables)
            assert dataset == {'name': 'wfp-food-security-indicators-for-guinea', 'title': 'Guinea - Food Security Indicators',
                               'maintainer': 'eda0ee04-7436-47f0-87ab-d1b9edcd3bb9', 'owner_org': '3ecac442-7fed-448d-8f78-b385ef6f84e7',
                               'data_update_frequency': '30', 'subnational': '0', 'groups': [{'name': 'gin'}],
                               'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'food security', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'indicators', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}], 'dataset_date': '06/01/2015'}
            resources = dataset.get_resources()
            assert resources == [{'name': 'pblStatsSum', 'description': 'pblStatsSum: Guinea - Food Security Indicators', 'format': 'csv', 'resource_type': 'file.upload', 'url_type': 'upload'},
                                 {'name': 'QuickCharts-pblStatsSum', 'description': 'Cut down data for QuickCharts', 'format': 'csv', 'resource_type': 'file.upload', 'url_type': 'upload'}]

            assert showcase == {'name': 'wfp-food-security-indicators-for-guinea-showcase', 'title': 'Guinea - Food Security Indicators', 'notes': 'Reports on food security for Guinea', 'url': 'https://vam.wfp.org/CountryPage_assessments.aspx?iso3=GIN', 'image_url': 'https://media.licdn.com/media/gcrc/dms/image/C5612AQHtvuWFVnGKAA/article-cover_image-shrink_423_752/0?e=2129500800&v=beta&t=00XnoAp85WXIxpygKvG7eGir_LqfxzXZz5lRGRrLUZw', 'tags': [{'name': 'hxl', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'food security', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}, {'name': 'indicators', 'vocabulary_id': '4e61d464-4943-4e97-973a-84673c1aaa87'}]}
            assert bites_disabled == [True, False, True]
