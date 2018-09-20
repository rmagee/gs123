
Using the GS123 Python Module
=============================
**Note:** this is a copy of the included Jupyter notebook included in this
documents directory.  If you'd like to try out some of the code shown here,
install *Jupyter*:

.. code-block:: text

    pip install jupyter

Then run jupyter within the docs directory of this code base

.. code-block:: text

    jupyter notebook

Once your browser brings up the directory, click on the `examples.pynb`
and you'll be able to run the code within this document.

.. code:: ipython3

    import os
    import sys
    nb_dir = os.path.split(os.getcwd())[0]
    if nb_dir not in sys.path:
        sys.path.append(nb_dir)

Converting GTIN-14 Barcodes
---------------------------

The GS123 Module is primarily used to convert GTIN-14 barcodes, URNs and
other GS1 identifiers of different types. This section will highlight
how to deal with GS1 GTIN-14 barcodes of different types. The first
thing we will do is import the library’s ``conversion`` module. Then we
pass in barcode string along with a company prefix length indicator.
After that, as you can see, we have access to all of the constituent
parts of the GTIN along with a URN representation of that GTIN barcode.

01-21 With No Parenthesis
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    from gs123 import conversion

    # here we create a new GTIN converter and pass in a GTIN (01 21) string along
    # with the legnth of the company prefix in the GTIN-14 portion (6 is the default)
    converter = conversion.BarcodeConverter('011234567890123421123456789012',6)
    # then we have access to the properties of the GTIN and the serial number
    print(converter.check_digit)
    print(converter.company_prefix)
    print(converter.epc_urn)
    print(converter.gtin14)
    print(converter.serial_number)
    print(converter.serial_number_field)
    print(converter.indicator_digit)
    print(converter.item_reference)


.. parsed-literal::

    4
    234567
    urn:epc:id:sgtin:234567.1890123.123456789012
    12345678901234
    123456789012
    123456789012
    1
    890123


01-21 With Parenthesis (GS1 App Identifiers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    from gs123 import conversion

    # here we create a new GTIN converter and pass in a GTIN (01 21) string along
    # with the legnth of the company prefix in the GTIN-14 portion (6 is the default)
    converter = conversion.BarcodeConverter('(01)12345678901234(21)123456789012',6)
    # then we have access to the properties of the GTIN and the serial number
    print(converter.check_digit)
    print(converter.company_prefix)
    print(converter.epc_urn)
    print(converter.gtin14)
    print(converter.serial_number)
    print(converter.serial_number_field)
    print(converter.indicator_digit)
    print(converter.item_reference)


.. parsed-literal::

    4
    234567
    urn:epc:id:sgtin:234567.1890123.123456789012
    12345678901234
    123456789012
    123456789012
    1
    890123


01-21-17-10 Without Parenthesis (Fixed Serial Number Field Length)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below we will parse a serialized GTIN barcode value with a expiration
date and lot fields. This value below does not have any parenthesis
around its application identifiers so we need a hint in the constructor
for the lenght of the serial number (in this case 12). If there is an
FNC1 character at the end of the serial-number, this is not required.

.. code:: ipython3

    converter = conversion.BarcodeConverter(
        '0100312345678901210000000000011719123110ABC123',
        company_prefix_length=6,
        serial_number_length=12
    )
    print(converter.check_digit)
    print(converter.company_prefix)
    print(converter.epc_urn)
    print(converter.gtin14)
    print(converter.indicator_digit)
    print(converter.item_reference)
    print(converter.lot)
    print(converter.expiration_date)



.. parsed-literal::

    1
    031234
    urn:epc:id:sgtin:031234.0567890.1
    00312345678901
    0
    567890
    ABC123
    191231


01-21-17-10 Without Parenthesis (FNC1 Delimiter for Serial Number)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since the serial number field in a typical serialized barcode is
variable length, we either need to know the length ahead of time or need
a delimiter such as the parenthesis around the app identifiers or a FNC1
delimiter which is a hidden character (ASCII hex value x1d). Below we
parse a barcode with an FNC1 delimiter.

.. code:: ipython3

    converter = conversion.BarcodeConverter(
        '010031234567890121000000000001\x1D1719123110ABC123',
        company_prefix_length=6
    )
    print(converter.check_digit)
    print(converter.company_prefix)
    print(converter.epc_urn)
    print(converter.gtin14)
    print(converter.serial_number)
    print(converter.serial_number_field)
    print(converter.indicator_digit)
    print(converter.item_reference)
    print(converter.lot)
    print(converter.expiration_date)


.. parsed-literal::

    1
    031234
    urn:epc:id:sgtin:031234.0567890.1
    00312345678901
    1
    000000000001
    0
    567890
    ABC123
    191231


01-21-17-10 With Parenthesis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here we have the parenthesis around the app identifiers…

.. code:: ipython3

    converter = conversion.BarcodeConverter(
        '(01)00312345678901(21)000000000001(17)191231(10)ABC123',
        company_prefix_length=6
    )
    print(converter.check_digit)
    print(converter.company_prefix)
    print(converter.epc_urn)
    print(converter.gtin14)
    print(converter.serial_number)
    print(converter.serial_number_field)
    print(converter.indicator_digit)
    print(converter.item_reference)
    print(converter.lot)
    print(converter.expiration_date)


.. parsed-literal::

    1
    031234
    urn:epc:id:sgtin:031234.0567890.1
    00312345678901
    1
    000000000001
    0
    567890
    ABC123
    191231


SSCC-18 Conversion
------------------

You can use the same class to convert SSCC-18s, the only difference
being that you’ll be accessing different properties of the class for the
extension digit along with the SSCC-18 value and that some of the
properties unique to GTIN-14s will be ``None``.

SSCC-18 No Parenthesis
~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    converter = conversion.BarcodeConverter(
        '(00)012345612345678907',
        6
    )
    print(converter.check_digit)
    print(converter.company_prefix)
    print(converter.epc_urn)
    print(converter.extension_digit)
    print(converter.sscc18)
    print(converter.serial_number)
    print(converter.serial_number_field)



.. parsed-literal::

    7
    123456
    urn:epc:id:sscc:123456.01234567890
    0
    012345612345678907
    1234567890
    1234567890


SSCC-18 No Parenthesis
~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    converter = conversion.BarcodeConverter(
        '00012345612345678907',
        6
    )
    print(converter.check_digit)
    print(converter.company_prefix)
    print(converter.epc_urn)
    print(converter.extension_digit)
    print(converter.sscc18)
    print(converter.serial_number)
    print(converter.serial_number_field)


.. parsed-literal::

    7
    123456
    urn:epc:id:sscc:123456.01234567890
    0
    012345612345678907
    1234567890
    1234567890


