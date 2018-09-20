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

import unittest
from click.testing import CliRunner

from gs123.conversion import BarcodeConverter
from gs123 import cli


class TestGs123(unittest.TestCase):
    """Tests for `gs123` package."""

    def test_01_21_no_parens(self):
        converter = BarcodeConverter(
            '011234567890123421123456789012',
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
            serial_number_length=12
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

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'gs123.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
