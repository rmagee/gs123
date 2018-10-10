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

import re
from gs123 import regex

FNC1 = '\x1D'


class BarcodeConverter:
    """
    Converts barcode values to URN values.
    """

    def __init__(self, barcode_val: str,
                 company_prefix_length: int,
                 serial_number_length: int = 12):
        """
        Initializes a new conversion class from a serialized GTIN in either
        01...21...17...10 or (01)...(21)...(17...(10) or 01...21 or
        (01)...(21) formats.  Once the inbound barcode value is parsed,
        the constituent components of both the GTIN-14 and the overall barcode
        itself are available via the properties of the class.  See the unit
        tests in this package for usage examples or consult the included
        documentation's *jupyter notebook*.

        :param barcode_val: The barcode value to convert.
        :param company_prefix_length: The company prefix.
        :param serial_number_length: The length of the serial number if
        the app identifiers do not have parenthesis and there are 17 and 10
        fields after the serial number field.
        """
        self._company_prefix_length = company_prefix_length
        self._serial_number_length = serial_number_length
        self._gtin14 = None
        self._sscc18 = None
        self._extension_digit = None
        self._serial_number = None
        self._lot = None
        self._expiration_date = None
        self._indicator_digit = None
        self._company_prefix = None
        self._item_reference = None
        self._check_digit = None
        self._sgtin_pattern = 'urn:epc:id:sgtin:{0}.{1}{2}.{3}'
        self._sscc_pattern = 'urn:epc:id:sscc:{0}.{1}{2}'
        self._is_gtin = False
        match = False
        if not barcode_val:
            raise self.BarcodeNotValid('No barcode was present.')
        if barcode_val.startswith('(01)'):
            match = regex.NUMERIC_GS1_01_21_OPTIONAL_17_10.match(
                barcode_val
            )
        elif barcode_val.startswith('(00)') or barcode_val.startswith('00'):
            match = regex.SSCC.match(
                barcode_val
            )
        if not match:
            # try to split by fnc1 character
            vals = self._fnc1_split(barcode_val)
            if not match:
                match = regex.NO_PARENS_NUMERIC_GS1_01_21.match(
                    barcode_val
                )
            if not match:
                match = regex.get_no_parens_numeric_gs1_01_21_optional_17_10(
                ).match(
                    barcode_val
                )
            if not match:
                match = regex.FNC1_SERIAL.match(
                    barcode_val
                )
        if match:
            self._populate(match)
        else:
            raise self.BarcodeNotValid(
                'The barcode %s was not valid against the regular expressions '
                'available in the module.' % barcode_val
            )

    @property
    def sscc18(self):
        return self._sscc18

    @property
    def extension_digit(self):
        return self._extension_digit

    @property
    def gtin14(self) -> str:
        """
        Returns the GTIN 14 for the class.
        :return: A string value with GTIN 14
        """
        return self._gtin14

    @property
    def serial_number(self) -> str:
        """
        Returns the serial number as a string with any leading zeros stripped.
        To get a non-stripped or non-altered serial number, use the
        `serial_number_field` property.
        :return: Serial number as string.
        """
        return self._serial_number.lstrip("0")

    @property
    def serial_number_field(self) -> str:
        """
        For the `serial_number` property, any leading zeros will be stripped
        from the serial number field if they are leading
        zeros.  This function will return the leading zeros if any were
        present.
        :return:
        """
        return self._serial_number

    @property
    def lot(self) -> str:
        """
        Returns the lot number as a string or None if no lot number was in
        the barcode.
        :return: String or None
        """
        return self._lot

    @property
    def expiration_date(self) -> str:
        """
        Returns the expiration date section of the barcode as a string or
        none if no expiration date was included.
        :return: Expiry as string or None
        """
        return self._expiration_date

    @property
    def indicator_digit(self) -> str:
        return self._gtin14[0]

    @property
    def item_reference(self) -> str:
        """
        The item reference number as taken from the barcode value.
        """
        return self._gtin14[self._company_prefix_length + 1:13]

    @property
    def company_prefix(self) -> str:
        """
        The company prefix as taken from the barcode value.
        :return: String
        """
        if self._gtin14:
            ret = self._gtin14[1:self._company_prefix_length + 1]
        else:
            ret = self._sscc18[1:self._company_prefix_length + 1]
        return ret

    @property
    def check_digit(self) -> str:
        """
        The original check digit supplied in the barcode.
        :return:
        """
        if self._gtin14:
            ret = self._gtin14[13]
        else:
            ret = self._sscc18[17]
        return ret

    @property
    def epc_urn(self) -> str:
        """
        Returns a GS1 EPC URN value for the given barcode.
        :return: String GS1 EPC URN for the barcode.
        """
        if self._gtin14:
            ret = self._sgtin_pattern.format(
                self.company_prefix,
                self.indicator_digit,
                self.item_reference,
                self.serial_number.lstrip("0")
            )
        else:
            ret = self._sscc_pattern.format(
                self.company_prefix,
                self.extension_digit,
                self.serial_number_field
            )
        return ret

    @property
    def epc_urn_fixed_serial(self) -> str:
        """
        Will return a (technically not-valid) EPC URN value with the
        serial number as it was reported in the barcode- meaning if there
        was any left zero padding, that padding will be included in the
        serial number field.
        :return:
        """
        return self._sgtin_pattern.format(
            self.company_prefix,
            self.indicator_digit,
            self.item_reference,
            self.serial_number_field
        )

    def _fnc1_split(self, barcode_val: str) -> list:
        """
        Splits the barcode value by the GS1 FNC1 (Ascii GS) character.
        :param barcode_val: The value to split
        :return: A list of strings.
        """
        return barcode_val.split('\x1d')

    def _populate(self, match) -> None:
        """
        If there is an inbound barcode that produces a match,
        this function will populate the class with all of the
        necessary converted properties.
        :param match: The Match object.
        :return: None
        """
        group_dict = match.groupdict()
        self._gtin14 = group_dict.get('gtin14')
        if self.gtin14:
            self._serial_number = group_dict['serial_number'].strip()
            self._expiration_date = group_dict.get('expiration_date')
            self._lot = group_dict.get('lot')
        else:  # this means we have an SSCC
            self._sscc18 = group_dict['sscc18']
            self._serial_number = self._sscc18[
                                  1 + self._company_prefix_length:17]
            self._extension_digit = self._sscc18[0]

    class BarcodeNotValid(BaseException):
        pass
