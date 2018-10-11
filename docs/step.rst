Using the XML Barcode Conversion Step
=====================================

The `gs123.steps` python module contains a `quartet_capture` step for use
in the QU4RTET Open Source EPCIS system.  This step will convert any data
within a specific rule's context under a configurable key name.  The
default key for data to be converted is `NUMBER_RESPONSE` to have the step
look elsewhere for XML data with barcodes to convert, see the step parameters
table below for more info.

--------------------------

Step Parameters
---------------
The following step parameters can be used to configure the step such that
it parses barcode data differently and can look within different rule context
keys for XML data to convert.

:Context Key:
    The name of the `quartet_capture.rules.Rule.rule_context.context`
    key to retrieve the XML data from.  The default value is `NUMBER_RESPONSE`.
    If you have XML data with barcodes that need to be converted within
    a different context variable, you can change the key name using the
    ** Context Key ** step parameter
:Company Prefix Length:
    The length of the company prefix.  This is necessary to create properly
    formatted URNs.  The default value is 6.  Change this accordingly.
:Serial Number Length:
    This is only needed if you are converting 01-21-17-10 barcode strings
    that have no delimiting parenthesis around the application identifiers.
    The default is 12.

Class Path
----------

The class path for the Step configuration in QU4RTET capture is:

.. code-block:: text

    gs123.steps.XMLBarcodeConversionStep
