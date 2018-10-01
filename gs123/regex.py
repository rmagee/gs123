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

# To edit this go here: https://regex101.com/r/v9CJm9/3

import re

_NUMERIC_GS1_01_21_OPTIONAL_17_10 = (r'^\(01\)(?P<gtin14>[0-9]{14})'
                                     r'\(21\)(?P<serial_number>[0-9, A-Z]{1,20})'
                                     r'(\(17\)(?P<expiration_date>[0-9]{6})?'
                                     r'\(10\)(?P<lot>[a-zA-Z0-9]{1,20}))?$')

# to edit https://regex101.com/r/TSraS8/1
_NO_PARENS_NUMERIC_GS1_01_21 = (r'^01(?P<gtin14>[0-9]{14})21(?P<serial_number>'
                                r'[0-9,A-Z]{1,20})$')

# to edit https://regex101.com/r/H0fHK8/2/
# the {%serial_number_length%} must be replaced at run-time by the
# calling application
_NO_PARENS_NUMERIC_GS1_01_21_OPTIONAL_17_10 = \
    (r'^01(?P<gtin14>[0-9]{14})'
     r'21(?P<serial_number>[0-9,A-Z]{{%serial_number_length%}})'
     r'(17(?P<expiration_date>(\d{6}))'
     r'10(?P<lot>[\x21-\x22\x25-\x2F\x30-\x39\x41-\x5A\x5F\x61-\x7A]{0,20}))?$')

NUMERIC_GS1_01_21_OPTIONAL_17_10 = re.compile(
    _NUMERIC_GS1_01_21_OPTIONAL_17_10)

NO_PARENS_NUMERIC_GS1_01_21 = re.compile(_NO_PARENS_NUMERIC_GS1_01_21)


def get_no_parens_numeric_gs1_01_21_optional_17_10(serial_number_length=12):
    """
    Will return a matching compiled regular expression to use in barcode values
    that have a fixed length serial number field but not parenthesis in the
    app identifiers.
    :param serial_number_length: The length of the fixed serial number field.
    :return: A compiled regular expression.
    """
    pattern = _NO_PARENS_NUMERIC_GS1_01_21_OPTIONAL_17_10.replace(
        '{%serial_number_length%}', str(serial_number_length)
    )
    return re.compile(pattern)

# https://regex101.com/r/H0fHK8/5
_FNC1_SERIAL = r'^01(?P<gtin14>[0-9]{14})21(?P<serial_number>[0-9,A-Z]*?(\x1d\b))(17(?P<expiration_date>[0-9]{6})10(?P<lot>[\x21-\x22\x25-\x2F\x30-\x39\x41-\x5A\x5F\x61-\x7A]{0,20}))?'
FNC1_SERIAL = re.compile(_FNC1_SERIAL)

# https://regex101.com/r/ivtuux/1/
_SSCC = r'^(00|\(00\))(?P<sscc18>\d{18})$'
SSCC = re.compile(_SSCC)

# https://regex101.com/r/wjN6lC/1/
NO_PARENS_NUMERIC_GS1_01_21_IN_DOC = r'01(?P<gtin14>[0-9]{14})21(?P<serial_number>[0-9,A-Z]{1,20})'
