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
import sys
import click

try:
    from gs123.xml_conversion import convert_xml_file
except ImportError:
    sys.path.append(os.path.join('../',os.path.dirname(__file__)))
    from gs123.xml_conversion import convert_xml_file


@click.command()
@click.option(
    '-i', '--input-file',
    help='An input file with barcode data to convert'
)
@click.option(
    '-o', '--output-file',
    help='The output file for converted data'
)
def main(input_file, output_file):
    """Console script for gs123."""
    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)
    convert_xml_file(input_file, output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
