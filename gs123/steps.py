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

from gs123.xml_conversion import convert_xml_string
from quartet_capture.rules import Step, RuleContext


class XMLBarcodeConversionStep(Step):
    """
    Will look in the rule context for XML with barcode data in it that the
    gs123 can convert, convert it and replace it with the new converted (to
    urn) data.
    """

    def execute(self, data, rule_context: RuleContext):
        # get the context key if configured
        company_prefix_length = self.get_or_create_parameter(
            'Company Prefix Length',
            '6',
            self.declared_parameters['Company Prefix Length']
        )
        serial_number_length = self.get_or_create_parameter(
            'Serial Number Length',
            '12',
            self.declared_parameters['Serial Number Length']
        )
        context_key = self.get_or_create_parameter(
            'Context Key',
            'NUMBER_RESPONSE',
            self.declared_parameters['Context Key']
        )
        use_context_key = self.get_or_create_parameter(
            'Use Context Key',
            'True',
            self.declared_parameters['Use Context Key']
        )
        use_context_key = ('true' == use_context_key.lower())
        self.info('Using context key %s' % context_key)
        if use_context_key:
            barcode_xml = rule_context.context.get(context_key, None)
        else:
            barcode_xml = data
        if barcode_xml:
            converted_data = convert_xml_string(
                barcode_xml,
                int(company_prefix_length),
                int(serial_number_length)
            ).decode('utf-8')
            self.info('Barcode data has been filtered and replaced where '
                      'possible.')
            if not use_context_key and converted_data:
                return converted_data
            else:
                rule_context.context[context_key] = converted_data
        else:
            self.warning('No XML was found in the Rule Context under the '
                         'context key %s or the rule had no inbound data.'
                         % context_key)

    @property
    def declared_parameters(self):
        return {
            "Context Key": "The context key where the data "
                           "to be converted can "
                           "be located.  Default is NUMBER_RESPONSE",
            "Use Context Key": "Whether or not to look in the context using "
                               "the context key for XML to convert. Default "
                               "is True.  If false, the step will "
                               "look in the inbound data for barcodes "
                               "to convert.",
            "Serial Number Length": "The length of the serial number field if "
                                    "the barcode data does not have delimited "
                                    "app identifiers with "
                                    "parenthesis and also "
                                    "has lot and expiry fields. "
                                    "Default is 12.",
            "Company Prefix Length": "The length of the company prefix.  "
                                     "Default is 6."
        }

    def on_failure(self):
        pass
