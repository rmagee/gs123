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

from gs123.xml_conversion import BarcodeConverter, convert_xml_string
from gs123.conversion import URNConverter
from quartet_capture import models
from quartet_capture.rules import Step, RuleContext


class BaseConversionClass(Step):
    """
    Base class for the conversion steps in this module.
    """

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        self._declared_parameters = {
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
        self.company_prefix_length, \
        self.context_key, \
        self.serial_number_length, \
        self.use_context_key = self._get_parameter_values()

    @property
    def declared_parameters(self):
        return self._declared_parameters

    def on_failure(self):
        pass

    def _get_parameter_values(self):
        """
        Checks all the step parameters for configured or default values
        and rerturns.
        :return: A tuple containing company prefix length, the rule context
        key to examine, the serial number length, and a boolean value
        which determines whether the context key should be used to look
        up data to covert or if the step should convert the data parameter
        passed into the execute function.
        """
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
            'False',
            self.declared_parameters['Use Context Key']
        )
        use_context_key = ('true' == use_context_key.lower())
        if use_context_key:
            self.info('Using context key %s' % context_key)
        else:
            self.info('Using the rule data.')
        return (
            company_prefix_length, context_key,
            serial_number_length, use_context_key
        )


class ListBarcodeConversionStep(BaseConversionClass):
    """
    If a list is passed into the rule as data or via the configurable
    step parameter "Context Key" in which the data is provided in the
    rule context, will convert any items
    in the list to valid URNs.
    """

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        self._declared_parameters["Property"] = \
            "The name of the property to access on the instance.  Check the" \
            " properties on the BarcodeConverter class for available options."
        self.prop_name = self.get_parameter('Property', 'epc_urn')

    def execute(self, data, rule_context: RuleContext):
        self.info('Task parameters: %s',
                  str(self.get_task_parameters(rule_context)))
        to_process = data or rule_context.context.get(self.context_key)
        if isinstance(to_process, list):
            converted = [self.convert(item) for item in to_process]
            if data:
                self.info('Inbound data was converted.  Returning back '
                          'to rule.')
                return converted
            else:
                self.info('The information in context key %s was converted.',
                          self.context_key)
                rule_context[self.context_key] = converted
        else:
            self.warning('No list data was provided for conversion.')

    def convert(self, data):
        """
        Will convert the data parameter to a urn value and return.
        Override this to return a different value from the BarcodeConverter.
        :param data: The barcode value to convert.
        :return: An EPC URN based on the inbound data.
        """
        prop_val = BarcodeConverter(
            data,
            self.company_prefix_length,
            self.serial_number_length
        ).__getattribute__(self.prop_name)
        return prop_val if isinstance(prop_val, str) else prop_val()


class ListURNConversionStep(ListBarcodeConversionStep):
    """
    Converts URN values into barcode values.  Using the Property step parameter
    you can specify what property on the `ListBarcodeConversionStep` object
    to return.
    """

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        self._declared_parameters["Property"] = \
            "The name of the property to access on the instance.  Check the" \
            " properties on the URNConverter class for available options."
        self.prop_name = self.get_parameter('Property', 'get_barcode_value')

    def convert(self, data):
        """
        Will convert the data parameter to a urn value and return.
        Override this to return a different value from the BarcodeConverter.
        :param data: The barcode value to convert.
        :return: An EPC URN based on the inbound data.
        """
        prop_val = URNConverter(
            data
        ).__getattribute__(self.prop_name)
        return prop_val if isinstance(prop_val, str) else prop_val()


class XMLBarcodeConversionStep(BaseConversionClass):
    """
    Will look in the rule context for XML with barcode data in it that the
    gs123 can convert, convert it and replace it with the new converted (to
    urn) data.
    """

    def execute(self, data, rule_context: RuleContext):
        if self.use_context_key:
            barcode_xml = rule_context.context.get(self.context_key, None)
            if isinstance(barcode_xml, bytes):
                barcode_xml = barcode_xml.decode('utf-8')
        else:
            barcode_xml = data
        if barcode_xml:
            converted_data = convert_xml_string(
                barcode_xml,
                int(self.company_prefix_length),
                int(self.serial_number_length)
            ).decode('utf-8')
            self.info('Barcode data has been filtered and replaced where '
                      'possible.')
            if not self.use_context_key and converted_data:
                return converted_data
            else:
                rule_context.context[self.context_key] = converted_data
        else:
            self.warning('No XML was found in the Rule Context under the '
                         'context key %s or the rule had no inbound data.'
                         % self.context_key)
