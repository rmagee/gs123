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
        context_key = self.get_parameter('ContextKey', 'NUMBER_RESPONSE')
        self.info('Using context key %s' % context_key)
        barcode_xml = rule_context.context[context_key]
        self.info('Barcode data has been filtered and replaced where '
                  'possible.')
        rule_context.context[context_key] = convert_xml_string(
            barcode_xml).decode('utf-8')

    @property
    def declared_parameters(self):
        {"ContextKey", "The context key where the data to be converted can "
                       "be located.  Default is NUMBER_RESPONSE"}

    def on_failure(self):
        pass
