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
import math

def calculate_check_digit(data):
    """
    Given a numeric string of n length, will calculate a GS1 compliant
    check digit according to instructions supplied here:
    https://www.gs1.org/how-calculate-check-digit-manually
    :param data: A numeric string of data.
    :return: The input string with the appropriate check digit applied.
    """
    sum = 0
    factors = [1,3] if len(data) & 1 else[3, 1]
    for i in range(len(data)):
        sum += int(data[i]) * factors[0] if i & 1 else int(data[i]) * factors[1]
    return "%s%s" % (data, str(int(math.ceil(sum/10.0)) * 10 - sum))
