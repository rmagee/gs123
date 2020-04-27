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
from gs123.check_digit import calculate_check_digit

FNC1 = '\x1D'


class BarcodeConverter:
    """
    Converts barcode values to URN values.
    """

    def __init__(self, barcode_val: str,
                 company_prefix_length: int,
                 max_serial_number_length: int = 14):
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
        :param max_serial_number_length: The length of the serial number if
        the app identifiers do not have parenthesis and there are 17 and 10
        fields after the serial number field.
        """
        self._company_prefix_length = company_prefix_length
        self._max_serial_number_length = max_serial_number_length
        self._gtin14 = None
        self._sscc18 = None
        self._extension_digit = None
        self._serial_number = None
        self._padded_serial_number = None
        self._lot = None
        self._expiration_date = None
        self._indicator_digit = None
        self._company_prefix = None
        self._item_reference = None
        self._check_digit = None
        self._sgtin_pattern = 'urn:epc:id:sgtin:{0}.{1}{2}.{3}'
        self._sscc_pattern = 'urn:epc:id:sscc:{0}.{1}{2}'
        self._is_gtin = False
        if not barcode_val:
            raise self.BarcodeNotValid('No barcode was present.')
        match = regex.match_pattern(barcode_val, max_serial_number_length)
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
    def padded_serial_number(self) -> str:
        """
        Returns as Serial Number, as-is.
        :return: Serial Number as string.
        """
        return self._padded_serial_number

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
                self.serial_number
            )
        else:
            ret = self._sscc_pattern.format(
                self.company_prefix,
                self.extension_digit,
                self.serial_number_field
            )
        return ret

    @property
    def padded_epc_urn(self) -> str:
        """
          If the Barcode is a GTIN-14, this will return the Serial Number 'as-is'. Meaning the
          Serial Number will not have leading Zeros removed.
          :return: String GS1 EPC URN for the Barcode
        """

        if self._gtin14:
            ret = self._sgtin_pattern.format(
                self.company_prefix,
                self.indicator_digit,
                self.item_reference,
                self.padded_serial_number
            )
        else:
            return self.epc_urn
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
            self.padded_serial_number
        )

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
            self._serial_number = str(
                group_dict['serial_number'].strip('\x1d'))
            self._padded_serial_number = self._serial_number
            self._expiration_date = group_dict.get('expiration_date')
            self._lot = group_dict.get('lot')
        else:  # this means we have an SSCC
            self._sscc18 = group_dict['sscc18']
            self._serial_number = self._sscc18[
                                  1 + int(self._company_prefix_length):17]
            self._extension_digit = self._sscc18[0]

    class BarcodeNotValid(BaseException):
        pass


class URNConverter(BarcodeConverter):
    """
    Converts an EPC urn to a valid barcode.
    """

    def __init__(self, urn_value: str):
        """
        Will convert the urn_value into a valid barcode.
        :param urn_value: A urn to convert.
        :param lot: If the lot is supplied an app identifier field of 10 will
        be added to the barcode
        :param expiration: If an expiration date value is supplied, this will
        be added to the barcode as a 17 field/app identifier value.
        """
        self._gtin14 = None
        self.is_sgtin = True
        for pattern in regex.urn_patterns:
            match = pattern.match(
                urn_value
            )
            if match:
                self._populate(match, urn_value)

    def _populate(self, match, urn_value: str):
        """
        Will populate the class parameters based on the match where
        applicable.
        :param match: The regular expression match
        :return: None
        """
        groups = match.groupdict()
        self._serial_number = str(groups.get('serial_number'))
        self._padded_serial_number = self._serial_number
        self._company_prefix = groups.get('company_prefix')
        if self._company_prefix:
            self._company_prefix_length = len(self._company_prefix)
        if urn_value.startswith('urn:epc:id:sgtin:'):
            self._handle_sgtin_urn(groups, urn_value)
        elif urn_value.startswith('urn:epc:id:sscc:'):
            self._handle_sscc_urn(groups, urn_value)

    def _handle_sscc_urn(self, groups, urn_value):
        """
        Extracts sscc info from the urn value and the regex groups.
        :param groups: The groups that were matched.
        :param urn_value: The original urn.
        :return: None
        """
        self.is_sgtin = False
        serial_number = groups.get('serial_number')
        self._extension_digit = serial_number[:1]
        self._serial_number = serial_number[1:]
        barcode = '%s%s' % (self._extension_digit, self._company_prefix)
        padding_length = 17 - len(barcode)
        serial_number = self._serial_number.zfill(padding_length)
        barcode = '%s%s' % (barcode, serial_number)
        self._sscc18 = calculate_check_digit(barcode)

    def _handle_sgtin_urn(self, groups, urn_value):
        """
        Extracts sgtin info from the urn value and the regex groups.
        :param groups: The groups that were matched.
        :param urn_value: The original urn.
        :return: None
        """
        item_reference = groups.get('item_reference')
        self._item_reference = item_reference[1:]
        self._indicator_digit = item_reference[:1]
        self._gtin14 = '{0}{1}{2}'.format(
            self._indicator_digit,
            self._company_prefix,
            self._item_reference
        )
        if len(self._gtin14) != 13:
            raise URNNotValid(
                'The urn %s is not valid. The parts representing the '
                'GTIN-14 should be 13 digits in length total.'
                % urn_value
            )
        self._gtin14 = calculate_check_digit(self._gtin14)

    def get_barcode_value(self, lot=None, expiration=None,
                          insert_control_char=False, parenthesis=False,
                          serial_number_padding=False,
                          serial_number_length=12,
                          padding_character='0'):
        """
        Returns the properly formatted barcode value.
        :param lot: pass this in if you'd like to add a lot (10)
        app identifier and lot value
        :param expiration: Pass this in if you'd like to add an expiration (17)
        and an expiration value
        :param insert_control_char: Set to true if you'd like an FNC1
        delimiter inserted after the serial number field.
        :param parenthesis: Set to true if you'd like parenthesis around all
        app identifiers.
        :param serial_number_padding: Set to true to pad serial numbers in
        SGTIN barcodes.
        :param serial_number_length: Set the length of the serial number length
        if you plan to pad it.
        :param padding_character: The character to pad the serial number with-
        default is zero
        :return: The properly formatted barcode string.
        """
        if self.is_sgtin:
            return self._get_gtin_barcode_val(
                lot=lot, expiration=expiration,
                insert_control_char=insert_control_char,
                parenthesis=parenthesis,
                serial_number_padding=serial_number_padding,
                serial_number_length=serial_number_length,
                padding_character=padding_character
            )
        else:
            return self._get_sscc_barcode_val(parenthesis=parenthesis)

    def _get_gtin_barcode_val(self, lot=None, expiration=None,
                              insert_control_char=False, parenthesis=False,
                              serial_number_padding=False,
                              serial_number_length=12,
                              padding_character='0') -> str:
        """
        Returns the barcode value for this instance.
        :return: A string representing the barcode.
        """
        if serial_number_padding:
            serial_number = self.serial_number.rjust(serial_number_length,
                                                     padding_character)
        else:
            serial_number = self.serial_number
        format_string = '(01){0}(21){1}' if parenthesis else '01{0}21{1}'
        barcode = format_string.format(
            self.gtin14,
            serial_number
        )
        if insert_control_char:
            barcode = '%s%s' % (barcode, FNC1)
        if expiration:
            if len(expiration) > 6:
                raise InvalidFieldDataError(
                    'The length of the expiration date must be six characters '
                    'long in YYMMDD format per GS1 standards.'
                )
            format_string = '%s(17)%s' if parenthesis else '%s17%s'
            barcode = format_string % (barcode, expiration)
        if lot:
            format_string = '%s(10)%s' if parenthesis else '%s10%s'
            barcode = format_string % (barcode, lot)
        return barcode

    def _get_sscc_barcode_val(self, parenthesis=False) -> str:
        format_string = '(00)%s' if parenthesis else '00%s'
        barcode = '%s%s' % (self.extension_digit, self.company_prefix)
        padding_length = 17 - len(barcode)
        serial_number = self._serial_number.zfill(padding_length)
        barcode = '%s%s' % (barcode, serial_number)
        return format_string % calculate_check_digit(barcode)


class URNNotValid(Exception):
    """
    Raised by instances when the inbound urn value is malformed.
    """
    pass


class InvalidFieldDataError(Exception):
    """
    Raised if inbound data is bad.
    """
    pass
