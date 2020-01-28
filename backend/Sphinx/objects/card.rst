.. index:: ! card

.. _card:

card
--------------

The attributes of a card object.


Attributes
~~~~~~~~~~~~~~~~~

.. index:: Card_id

``Card_id``
    String: the customer's card number.

.. index:: expiration

``expiration``
    String: the customer's card expiration date.

.. index:: pan_redacted

``pan_redacted``
    String: the card number with only the last four digits showing.

.. index:: suspended

``suspended``
    String: whether the card is currently suspended.


Used In
~~~~~~~

- :http:get:`ferlyapi.com/profile`
