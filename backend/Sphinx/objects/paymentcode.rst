.. index:: ! PaymentCode

.. _PaymentCode:

PaymentCode
-----------

A payment code is a short numeric code representing a payment to be completed when the code is presented to a cashier. A sender can have multiple payment codes at a time.

.. warning:: While apps should show the payment code to the person or business who sent it, apps MUST NOT reveal the payment code to the potential recipient.

Attributes
~~~~~~~~~~

.. index:: url

``url``
    The web URL of this payment code. Only the sender is allowed to see it. Example: |sample_paycode_url|

.. index:: transfer_id

``transfer_id``
    String: the ID of the transfer connected with the payment code.

.. index:: currency

``currency``
    String: an :term:`ISO 4217` currency (3 uppercase letters).

.. index:: amount

``amount``
    String: the maximum amount of cash the payment code will release to the recipient. Example: ``20.00``.

.. index:: created

``created``
    String: the :term:`ISO 8601` date and time when the code was created.

.. index:: modified

``modified``
    String: the :term:`ISO 8601` date and time when the code was last modified.

.. index:: expires

``expires``
    String: the :term:`ISO 8601` date and time when the code will expire. At expiration, the cancels the transfer.

.. index:: sender_id

``sender_id``
    String: the ID of the profile who created the code.

.. index:: recipient_id

``recipient_id``
    String: the ID of the profile who can accept the code. Currently, recipients of payment codes are always businesses.

.. index:: code

``code``
    String: the payment code. Contains 4 or more digits. Only the sender should see this code.

Used In
~~~~~~~

- :ref:`TransferDetail`
