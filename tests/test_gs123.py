# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

import os

import django
from django.test import TestCase
from django.db.utils import IntegrityError

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
django.setup()

from quartet_capture import models
from quartet_capture.rules import Rule

from gs123.conversion import BarcodeConverter, URNConverter, FNC1
from gs123.xml_conversion import convert_xml_file, convert_xml_string
from gs123.check_digit import calculate_check_digit


class TestGs123(TestCase):
    """Tests for `gs123` package."""

    def test_01_21_no_parens_leading_zeros(self):
        converter = BarcodeConverter(
            '011234567890123421003456789012',
            6
        )
        self.assertEqual(converter.gtin14, '12345678901234')
        self.assertEqual(converter.serial_number_field, '003456789012')
        self.assertEqual(converter.company_prefix, '234567')
        self.assertEqual(converter.indicator_digit, '1')
        self.assertEqual(converter.check_digit, '4')
        self.assertEqual(converter.item_reference, '890123')
        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:234567.1890123.3456789012')

    def test_01_21_no_parens(self):
        converter = BarcodeConverter(
            '01003005406390512110008344372010',
            6
        )
        self.assertEqual(converter.gtin14, '00300540639051')
        self.assertEqual(converter.serial_number, '10008344372010')
        self.assertEqual(converter.company_prefix, '030054')
        self.assertEqual(converter.indicator_digit, '0')
        self.assertEqual(converter.check_digit, '1')
        self.assertEqual(converter.item_reference, '063905')
        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:030054.0063905.10008344372010')

    def test_01_21_no_parens_12_digit(self):
        converter = BarcodeConverter(
            '013030054063905221100000001307',
            6
        )
        self.assertEqual(converter.gtin14, '30300540639052')
        self.assertEqual(converter.serial_number, '100000001307')
        self.assertEqual(converter.company_prefix, '030054')
        self.assertEqual(converter.indicator_digit, '3')
        self.assertEqual(converter.check_digit, '2')
        self.assertEqual(converter.item_reference, '063905')
        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:030054.3063905.100000001307')

    def test_01_21_with_parens(self):
        converter = BarcodeConverter(
            '(01)12345678901234(21)123456789012',
            6
        )
        self.assertEqual(converter.gtin14, '12345678901234')
        self.assertEqual(converter.serial_number, '123456789012')
        self.assertEqual(converter.company_prefix, '234567')
        self.assertEqual(converter.indicator_digit, '1')
        self.assertEqual(converter.check_digit, '4')
        self.assertEqual(converter.item_reference, '890123')
        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:234567.1890123.123456789012')

    def test_sscc_18(self):
        converter = BarcodeConverter(
            '00050991510019004305',
            company_prefix_length=7
        )
        self.assertEqual(converter.company_prefix, "5099151")
        self.assertEqual(converter.serial_number_field, "001900430")

    def test_01_21_17_10_with_parens(self):
        converter = BarcodeConverter(
            '(01)00312345678901(21)000000000001(17)191231(10)ABC123',
            6
        )
        self.assertEqual(converter.gtin14, '00312345678901')
        self.assertEqual(converter.serial_number_field, '000000000001')
        self.assertEqual(converter.serial_number, '1')
        self.assertEqual(converter.company_prefix, '031234')
        self.assertEqual(converter.indicator_digit, '0')
        self.assertEqual(converter.check_digit, '1')
        self.assertEqual(converter.item_reference, '567890')
        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:031234.0567890.1')

    def test_01_21_17_10_no_parens(self):
        converter = BarcodeConverter(
            '0100312345678901210000000000011719123110ABC123',
            company_prefix_length=6,
            max_serial_number_length=12
        )
        self.assertEqual(converter.gtin14, '00312345678901')
        self.assertEqual(converter.serial_number, '1')
        self.assertEqual(converter.serial_number_field, '000000000001')
        self.assertEqual(converter.company_prefix, '031234')
        self.assertEqual(converter.indicator_digit, '0')
        self.assertEqual(converter.check_digit, '1')
        self.assertEqual(converter.item_reference, '567890')
        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:031234.0567890.1')
        self.assertEqual(converter.lot, 'ABC123')
        self.assertEqual(converter.expiration_date, '191231')

    def test_01_21_17_10_no_parens_FNC1(self):
        converter = BarcodeConverter(
            '010031234567890121000000000000001\x1D1719123110ABC123\x1D',
            company_prefix_length=6,
        )
        self.assertEqual(converter.gtin14, '00312345678901')
        self.assertEqual(converter.serial_number_field, '000000000000001')
        self.assertEqual(converter.serial_number, '1')
        self.assertEqual(converter.company_prefix, '031234')
        self.assertEqual(converter.indicator_digit, '0')
        self.assertEqual(converter.check_digit, '1')
        self.assertEqual(converter.item_reference, '567890')
        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:031234.0567890.1')
        self.assertEqual(converter.lot, 'ABC123')
        self.assertEqual(converter.expiration_date, '191231')

    def test_01_21_17_10_no_parens_FNC1_padded(self):
        converter = BarcodeConverter(
            '010031234567890121000000000000001\x1D1719123110ABC123\x1D',
            company_prefix_length=6,
        )
        self.assertEqual(converter.gtin14, '00312345678901')
        self.assertEqual(converter.serial_number_field, '000000000000001')
        self.assertEqual(converter.serial_number, '1')
        self.assertEqual(converter.padded_serial_number, '000000000000001')
        self.assertEqual(converter.company_prefix, '031234')
        self.assertEqual(converter.indicator_digit, '0')
        self.assertEqual(converter.check_digit, '1')
        self.assertEqual(converter.item_reference, '567890')
        self.assertEqual(converter.padded_epc_urn,
                         'urn:epc:id:sgtin:031234.0567890.000000000000001')

        self.assertEqual(converter.epc_urn,
                         'urn:epc:id:sgtin:031234.0567890.1')

        self.assertEqual(converter.lot, 'ABC123')
        self.assertEqual(converter.expiration_date, '191231')

    def test_sscc18_with_parens(self):
        converter = BarcodeConverter(
            '(00)012345612345678907',
            6
        )
        self.assertEqual(converter.extension_digit, '0')
        self.assertEqual(converter.sscc18, '012345612345678907')
        self.assertEqual(converter.serial_number, '1234567890')
        self.assertEqual(converter.check_digit, '7')
        self.assertEqual(converter.company_prefix, '123456')
        self.assertEqual(
            converter.epc_urn,
            'urn:epc:id:sscc:123456.01234567890'
        )

    def test_sscc18_without_parens_7_cp_len(self):
        converter = BarcodeConverter(
            '00012345612345678907',
            7, 12
        )
        self.assertEqual(converter.extension_digit, '0')
        self.assertEqual(converter.sscc18, '012345612345678907')
        self.assertEqual(converter.serial_number, '234567890')
        self.assertEqual(converter.check_digit, '7')
        self.assertEqual(converter.company_prefix, '1234561')
        self.assertEqual(
            converter.epc_urn,
            'urn:epc:id:sscc:1234561.0234567890'
        )

    def test_sscc18_without_parens(self):
        converter = BarcodeConverter(
            '00012345612345678907',
            6
        )
        self.assertEqual(converter.extension_digit, '0')
        self.assertEqual(converter.sscc18, '012345612345678907')
        self.assertEqual(converter.serial_number, '1234567890')
        self.assertEqual(converter.check_digit, '7')
        self.assertEqual(converter.company_prefix, '123456')
        self.assertEqual(
            converter.epc_urn,
            'urn:epc:id:sscc:123456.01234567890'
        )

    def test_bad_barcode(self):
        with self.assertRaises(BarcodeConverter.BarcodeNotValid):
            converter = BarcodeConverter(
                '012392348439', 6
            )

    def test_check_digits(self):
        self.assertEqual(
            calculate_check_digit("0099999999998"),
            "00999999999986"
        )
        self.assertEqual(
            calculate_check_digit("12345678901234567"),
            "123456789012345675"
        )
        self.assertEqual(
            calculate_check_digit("123456789012"),
            "1234567890128"
        )

    def test_file_conversion(self):
        curpath = os.path.join(os.path.dirname(__file__),
                               'data/serialnumbers.xml')
        output_file_path = os.path.join(os.path.dirname(__file__),
                                        'data/converted.xml')
        convert_xml_file(curpath, output_file_path, company_prefix_length=6,
                         serial_number_length=10)

    def test_sscc_file_conversion(self):
        curpath = os.path.join(os.path.dirname(__file__),
                               'data/ssccs.xml')
        output_file_path = os.path.join(os.path.dirname(__file__),
                                        'data/sscc_converted.xml')
        convert_xml_file(curpath, output_file_path, company_prefix_length=6,
                         serial_number_length=10)

    def test_string_conversion(self):
        data = """<?xml version='1.0' encoding='UTF-8'?>
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
    <S:Body>
        <ns2:serialNumbersRequestResponse xmlns:ns2="urn:test:soap">
            <SNResponse>
                <ReceivingSystem>0344444000006</ReceivingSystem>
                <SendingSystem>0344444000006</SendingSystem>
                <ActionCode>C</ActionCode>
                <EncodingType>SGTIN</EncodingType>
                <IDType>GS1_SER</IDType>
                <ObjectKey>
                    <Name>GTIN</Name>
                    <Value>00377713112102</Value>
                </ObjectKey>
                <RandomizedNumberList>
                    <SerialNo>0100377713112102211RFXVHNPA111</SerialNo>
                    <SerialNo>01003777131121022114R2FANWAG12</SerialNo>
                    <SerialNo>0100377713112102212FWA6AVK7614</SerialNo>
                    <SerialNo>0100377713112102212NN3NG5VK415</SerialNo>
                    <SerialNo>01003777131121022119KNN3H4A145</SerialNo>
                    <SerialNo>01003777131121022125P4N3X8NP45</SerialNo>
                    <SerialNo>01003777131121022116326N1GFV75</SerialNo>
                    <SerialNo>010037771311210221148NNK9N7488</SerialNo>
                    <SerialNo>01003777131121022115WANPT8KR34</SerialNo>
                    <SerialNo>01003777131121022113CK6FRH7R88</SerialNo>
                    <SerialNo>0100377713112102211X769VGH1G7J</SerialNo>
                    <SerialNo>010037771311210221325NV1T32FSD</SerialNo>
                    <SerialNo>01003777131121022117F4VTPWR5CV</SerialNo>
                    <SerialNo>0100377713112102212P5W5R9WRGED</SerialNo>
                    <SerialNo>0100377713112102211NK693FK75FF</SerialNo>
                    <SerialNo>0100377713112102212F397C3455LM</SerialNo>
                    <SerialNo>0100377713112102212F76HPVFF5ED</SerialNo>
                    <SerialNo>0100377713112102212CWRCFTTPTEW</SerialNo>
                    <SerialNo>0100377713112102211N3F9PTP14DF</SerialNo>
                    <SerialNo>010037771311210221245RV96KFHJK</SerialNo>
                </RandomizedNumberList>
            </SNResponse>
        </ns2:serialNumbersRequestResponse>
    </S:Body>
</S:Envelope>"""
        ret = convert_xml_string(data, company_prefix_length=6)
        print(ret)

    def test_bytes_step(self):
        """
        Test the XMLBarcodeConversion step.
        :return: None
        """
        data = b"""<?xml version='1.0' encoding='UTF-8'?>
        <S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
            <S:Body>
                <ns2:serialNumbersRequestResponse xmlns:ns2="urn:test:soap">
                    <SNResponse>
                        <ReceivingSystem>0344444000006</ReceivingSystem>
                        <SendingSystem>0344444000006</SendingSystem>
                        <ActionCode>C</ActionCode>
                        <EncodingType>SGTIN</EncodingType>
                        <IDType>GS1_SER</IDType>
                        <ObjectKey>
                            <Name>GTIN</Name>
                            <Value>00377713112102</Value>
                        </ObjectKey>
                        <RandomizedNumberList>
                            <SerialNo>0100377713112102211RFXVHNPA111</SerialNo>
                            <SerialNo>01003777131121022114R2FANWAG12</SerialNo>
                            <SerialNo>0100377713112102212FWA6AVK7614</SerialNo>
                            <SerialNo>0100377713112102212NN3NG5VK415</SerialNo>
                            <SerialNo>01003777131121022119KNN3H4A145</SerialNo>
                            <SerialNo>01003777131121022125P4N3X8NP45</SerialNo>
                            <SerialNo>01003777131121022116326N1GFV75</SerialNo>
                            <SerialNo>010037771311210221148NNK9N7488</SerialNo>
                            <SerialNo>01003777131121022115WANPT8KR34</SerialNo>
                            <SerialNo>01003777131121022113CK6FRH7R88</SerialNo>
                            <SerialNo>0100377713112102211X769VGH1G7J</SerialNo>
                            <SerialNo>010037771311210221325NV1T32FSD</SerialNo>
                            <SerialNo>01003777131121022117F4VTPWR5CV</SerialNo>
                            <SerialNo>0100377713112102212P5W5R9WRGED</SerialNo>
                            <SerialNo>0100377713112102211NK693FK75FF</SerialNo>
                            <SerialNo>0100377713112102212F397C3455LM</SerialNo>
                            <SerialNo>0100377713112102212F76HPVFF5ED</SerialNo>
                            <SerialNo>0100377713112102212CWRCFTTPTEW</SerialNo>
                            <SerialNo>0100377713112102211N3F9PTP14DF</SerialNo>
                            <SerialNo>010037771311210221245RV96KFHJK</SerialNo>
                        </RandomizedNumberList>
                    </SNResponse>
                </ns2:serialNumbersRequestResponse>
            </S:Body>
        </S:Envelope>"""
        db_rule, db_task, db_step = self._create_rule()
        c_rule = Rule(db_task.rule, db_task)
        c_rule.context.context['NUMBER_RESPONSE'] = data
        c_rule.execute('')
        self.assertTrue('urn:epc:id:sgtin:037771.0311210.1RFXVHNPA111' in
                        c_rule.context.context['NUMBER_RESPONSE'])
        c_rule.context.context['NUMBER_RESPONSE'] = data
        c_rule.execute('')
        self.assertTrue('urn:epc:id:sgtin:037771.0311210.1RFXVHNPA111' in
                        c_rule.context.context['NUMBER_RESPONSE'])

    def test_string_step(self):
        """
        Test the XMLBarcodeConversion step.
        :return: None
        """
        data = """<?xml version='1.0' encoding='UTF-8'?>
        <S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
            <S:Body>
                <ns2:serialNumbersRequestResponse xmlns:ns2="urn:test:soap">
                    <SNResponse>
                        <ReceivingSystem>0344444000006</ReceivingSystem>
                        <SendingSystem>0344444000006</SendingSystem>
                        <ActionCode>C</ActionCode>
                        <EncodingType>SGTIN</EncodingType>
                        <IDType>GS1_SER</IDType>
                        <ObjectKey>
                            <Name>GTIN</Name>
                            <Value>00377713112102</Value>
                        </ObjectKey>
                        <RandomizedNumberList>
                            <SerialNo>0100377713112102211RFXVHNPA111</SerialNo>
                            <SerialNo>01003777131121022114R2FANWAG12</SerialNo>
                            <SerialNo>0100377713112102212FWA6AVK7614</SerialNo>
                            <SerialNo>0100377713112102212NN3NG5VK415</SerialNo>
                            <SerialNo>01003777131121022119KNN3H4A145</SerialNo>
                            <SerialNo>01003777131121022125P4N3X8NP45</SerialNo>
                            <SerialNo>01003777131121022116326N1GFV75</SerialNo>
                            <SerialNo>010037771311210221148NNK9N7488</SerialNo>
                            <SerialNo>01003777131121022115WANPT8KR34</SerialNo>
                            <SerialNo>01003777131121022113CK6FRH7R88</SerialNo>
                            <SerialNo>0100377713112102211X769VGH1G7J</SerialNo>
                            <SerialNo>010037771311210221325NV1T32FSD</SerialNo>
                            <SerialNo>01003777131121022117F4VTPWR5CV</SerialNo>
                            <SerialNo>0100377713112102212P5W5R9WRGED</SerialNo>
                            <SerialNo>0100377713112102211NK693FK75FF</SerialNo>
                            <SerialNo>0100377713112102212F397C3455LM</SerialNo>
                            <SerialNo>0100377713112102212F76HPVFF5ED</SerialNo>
                            <SerialNo>0100377713112102212CWRCFTTPTEW</SerialNo>
                            <SerialNo>0100377713112102211N3F9PTP14DF</SerialNo>
                            <SerialNo>010037771311210221245RV96KFHJK</SerialNo>
                        </RandomizedNumberList>
                    </SNResponse>
                </ns2:serialNumbersRequestResponse>
            </S:Body>
        </S:Envelope>"""
        db_rule, db_task, db_step = self._create_rule()
        c_rule = Rule(db_task.rule, db_task)
        c_rule.context.context['NUMBER_RESPONSE'] = data.encode('utf-8')
        c_rule.execute('')
        self.assertTrue('urn:epc:id:sgtin:037771.0311210.1RFXVHNPA111' in
                        c_rule.context.context['NUMBER_RESPONSE'])

    def test_params(self):
        data = """<?xml version='1.0' encoding='UTF-8'?>
        <S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
            <S:Body>
                <ns2:serialNumbersRequestResponse xmlns:ns2="urn:test:soap">
                    <SNResponse>
                        <ReceivingSystem>0344444000006</ReceivingSystem>
                        <SendingSystem>0344444000006</SendingSystem>
                        <ActionCode>C</ActionCode>
                        <EncodingType>SGTIN</EncodingType>
                        <IDType>GS1_SER</IDType>
                        <ObjectKey>
                            <Name>GTIN</Name>
                            <Value>00377713112102</Value>
                        </ObjectKey>
                        <RandomizedNumberList>
                            <SerialNo>0100377713112102211RFXVHNPA1111712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022114R2FANWAG121712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212FWA6AVK76141712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212NN3NG5VK4151712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022119KNN3H4A1451712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022125P4N3X8NP451712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022116326N1GFV751712311910LOT777</SerialNo>
                            <SerialNo>010037771311210221148NNK9N74881712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022115WANPT8KR341712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022113CK6FRH7R881712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102211X769VGH1G7J1712311910LOT777</SerialNo>
                            <SerialNo>010037771311210221325NV1T32FSD1712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022117F4VTPWR5CV1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212P5W5R9WRGED1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102211NK693FK75FF1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212F397C3455LM1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212F76HPVFF5ED1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212CWRCFTTPTEW1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102211N3F9PTP14DF1712311910LOT777</SerialNo>
                            <SerialNo>010037771311210221245RV96KFHJK1712311910LOT777</SerialNo>
                        </RandomizedNumberList>
                    </SNResponse>
                </ns2:serialNumbersRequestResponse>
            </S:Body>
        </S:Envelope>"""
        db_rule, db_task, db_step = self._create_rule()
        company_prefix_length = models.StepParameter.objects.create(
            name='Company Prefix Length',
            value='7',
            step=db_step
        )
        serial_number_length = models.StepParameter.objects.create(
            name='Serial Number Length',
            value='10',
            step=db_step
        )
        c_rule = Rule(db_task.rule, db_task)
        c_rule.context.context['NUMBER_RESPONSE'] = data.encode('utf-8')
        c_rule.execute('')
        self.assertTrue('urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111' in
                        c_rule.context.context['NUMBER_RESPONSE'])
        c_rule = Rule(db_task.rule, db_task)
        c_rule.context.context['NUMBER_RESPONSE'] = ''
        c_rule.execute('')
        self.assertTrue('urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111' not in
                        c_rule.context.context['NUMBER_RESPONSE'])

    def test_parse_rule_data(self):
        data = """<?xml version='1.0' encoding='UTF-8'?>
        <S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
            <S:Body>
                <ns2:serialNumbersRequestResponse xmlns:ns2="urn:test:soap">
                    <SNResponse>
                        <ReceivingSystem>0344444000006</ReceivingSystem>
                        <SendingSystem>0344444000006</SendingSystem>
                        <ActionCode>C</ActionCode>
                        <EncodingType>SGTIN</EncodingType>
                        <IDType>GS1_SER</IDType>
                        <ObjectKey>
                            <Name>GTIN</Name>
                            <Value>00377713112102</Value>
                        </ObjectKey>
                        <RandomizedNumberList>
                            <SerialNo>0100377713112102211RFXVHNPA1111712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022114R2FANWAG121712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212FWA6AVK76141712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212NN3NG5VK4151712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022119KNN3H4A1451712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022125P4N3X8NP451712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022116326N1GFV751712311910LOT777</SerialNo>
                            <SerialNo>010037771311210221148NNK9N74881712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022115WANPT8KR341712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022113CK6FRH7R881712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102211X769VGH1G7J1712311910LOT777</SerialNo>
                            <SerialNo>010037771311210221325NV1T32FSD1712311910LOT777</SerialNo>
                            <SerialNo>01003777131121022117F4VTPWR5CV1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212P5W5R9WRGED1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102211NK693FK75FF1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212F397C3455LM1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212F76HPVFF5ED1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102212CWRCFTTPTEW1712311910LOT777</SerialNo>
                            <SerialNo>0100377713112102211N3F9PTP14DF1712311910LOT777</SerialNo>
                            <SerialNo>010037771311210221245RV96KFHJK1712311910LOT777</SerialNo>
                        </RandomizedNumberList>
                    </SNResponse>
                </ns2:serialNumbersRequestResponse>
            </S:Body>
        </S:Envelope>"""
        db_rule, db_task, db_step = self._create_rule()
        models.StepParameter.objects.create(
            name='Company Prefix Length',
            value='7',
            step=db_step
        )
        models.StepParameter.objects.create(
            name='Serial Number Length',
            value='10',
            step=db_step
        )
        sp = models.StepParameter.objects.get(
            name='Use Context Key',
        )
        sp.step = db_step
        sp.value = 'False'
        sp.save()
        c_rule = Rule(db_task.rule, db_task)
        data = c_rule.execute(data)

    def test_parse_urn_data(self):
        rule, task, conversion_step = self._create_urn_rule()
        c_rule = Rule(task.rule, task)
        vals = [
            'urn:epc:id:sgtin:077722.0011210.12CW68RW6G',
            'urn:epc:id:sgtin:077722.0011210.11X8KN3H4W',
            'urn:epc:id:sgtin:077722.0011210.29A1X6F8KR',
            'urn:epc:id:sgtin:077722.0011210.15684ART9V',
            'urn:epc:id:sgtin:077722.0011210.2KK8NT4264'
        ]
        c_rule.execute(vals)
        print(c_rule.data)

    def _create_rule(self):
        db_rule = models.Rule()
        db_rule.name = 'xml_barcode_conversion'
        db_rule.description = 'XML Barcode conversion step rule.'
        db_rule.save()
        rp = models.RuleParameter(name='test name', value='test value',
                                  rule=db_rule)
        rp.save()
        # create a new step
        conversion_step = models.Step()
        conversion_step.name = 'parse-barcodes'
        conversion_step.description = 'Convert barcodes to urns.'
        conversion_step.order = 1
        conversion_step.step_class = 'gs123.steps.XMLBarcodeConversionStep'
        conversion_step.rule = db_rule
        conversion_step.save()

        ucc_param = models.StepParameter.objects.create(
            name='Use Context Key',
            value='True',
            step=conversion_step,
        )

        db_task = models.Task(
            rule=db_rule,
            status='QUEUED',
        )
        return db_rule, db_task, conversion_step

    def _create_urn_rule(self):
        db_rule = models.Rule()
        db_rule.name = 'List URN Conversion'
        db_rule.description = 'Converts a list of URN values to barcodes.'
        db_rule.save()

        conversion_step = models.Step()
        conversion_step.name = 'List URN Parser'
        conversion_step.description = 'Parse a list of URN values.'
        conversion_step.order = 1
        conversion_step.step_class = 'gs123.steps.ListURNConversionStep'
        conversion_step.rule = db_rule
        conversion_step.save()

        db_task = models.Task(
            rule=db_rule,
            status='QUEUED',
        )
        return db_rule, db_task, conversion_step

    def test_urn_to_barcode(self):
        urnc = URNConverter(
            'urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111'
        )
        self.assertEqual(
            urnc.get_barcode_value(),
            '0100377713112109211RFXVHNPA111'
        )

    def test_parens(self):
        urnc = URNConverter(
            'urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111'
        )
        self.assertEqual(
            urnc.get_barcode_value(parenthesis=True),
            '(01)00377713112109(21)1RFXVHNPA111'
        )

    def test_lot_batch(self):
        urnc = URNConverter(
            'urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111'
        )
        self.assertEqual(
            urnc.get_barcode_value(
                lot='ABC123',
                expiration='181231'
            ),
            '0100377713112109211RFXVHNPA1111718123110ABC123'
        )

    def test_lot_batch_parens(self):
        urnc = URNConverter(
            'urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111'
        )
        self.assertEqual(
            urnc.get_barcode_value(
                lot='ABC123',
                expiration='181231',
                parenthesis=True
            ),
            '(01)00377713112109(21)1RFXVHNPA111(17)181231(10)ABC123'
        )

    def test_padding(self):
        urnc = URNConverter(
            'urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111'
        )
        self.assertEqual(
            urnc.get_barcode_value(
                serial_number_length=14,
                serial_number_padding=True
            ),
            '010037771311210921001RFXVHNPA111',
        )

    def test_fnc1(self):
        urnc = URNConverter(
            'urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111'
        )
        self.assertEqual(
            urnc.get_barcode_value(
                lot='ABC123',
                expiration='181231',
                insert_control_char=True
            ),
            '0100377713112109211RFXVHNPA111{0}1718123110ABC123'.format(FNC1)
        )

    def test_serial_number(self):
        urnc = URNConverter(
            'urn:epc:id:sgtin:0377713.011210.1RFXVHNPA111'
        )
        self.assertEqual(
            urnc.serial_number,
            '1RFXVHNPA111'
        )

    def test_gcp_from_urn(self):
        urnc_gtin_1 = URNConverter('urn:epc:id:sgtin:35555555555.01.123')
        urnc_gtin_2 = URNConverter('urn:epc:id:sgtin:355555555555.0.123')
        urnc_sscc_1 = URNConverter('urn:epc:id:sscc:35555555555.110001')
        urnc_sscc_2 = URNConverter('urn:epc:id:sscc:355555555555.11001')

        self.assertEqual(urnc_gtin_1.company_prefix, '35555555555')
        self.assertEqual(urnc_gtin_2.company_prefix, '355555555555')
        self.assertEqual(urnc_sscc_1.company_prefix, '35555555555')
        self.assertEqual(urnc_sscc_2.company_prefix, '355555555555')


    def _fixture_teardown(self):
        try:
            super()._fixture_teardown()
        except IntegrityError:
            pass

