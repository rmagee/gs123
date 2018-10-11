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
from io import BytesIO, StringIO
from lxml import etree
from gs123.conversion import BarcodeConverter


def convert_xml_string(data: str,
                       company_prefix_length: int = 6,
                       serial_number_length: int = 12):
    if isinstance(data, bytes):
        elements = etree.iterparse(BytesIO(data),
                                   events=('start', 'end',),
                                   remove_comments=True)
    elif isinstance(data, str):
        elements = etree.iterparse(BytesIO(data.encode('utf-8')),
                                   events=('start', 'end',),
                                   remove_comments=True)

    with StringIO('') as output_file:
        _parse_xml(company_prefix_length, elements,
                   serial_number_length)
        return (etree.tostring(elements.root))


def convert_xml_file(file_path: str,
                     output_file_path: str,
                     company_prefix_length: int = 6,
                     serial_number_length: int = 12):
    """
    Converts an inbound XML file into an outbound XML file with all of the
    barcodes converted to EPC URN values.
    :param file_path: The file to parse.
    :param output_file_path: The new file to create.
    :param company_prefix_length: The length of the company prefix in the
    barcodes. Default is 6.
    :param serial_number_length: The serial number length.  Default is 12.
    :return: None.
    """
    elements = etree.iterparse(file_path, events=('start', 'end',),
                               remove_comments=True)
    with open(output_file_path, 'wb+') as output_file:
        _parse_xml(company_prefix_length, elements,
                   serial_number_length)
        output_file.write(etree.tostring(elements.root))
        output_file.flush()


def _parse_xml(company_prefix_length, elements,
               serial_number_length):
    for event, element in elements:
        try:
            if event == 'end':
                bc = BarcodeConverter(
                    element.text,
                    company_prefix_length=company_prefix_length,
                    serial_number_length=serial_number_length
                )
                element.text = bc.epc_urn
            for name, value in element.items():
                bc = BarcodeConverter(
                    value,
                    company_prefix_length=company_prefix_length,
                    serial_number_length=serial_number_length
                )
                element.set(name, bc.epc_urn)

        except BarcodeConverter.BarcodeNotValid:
            pass
