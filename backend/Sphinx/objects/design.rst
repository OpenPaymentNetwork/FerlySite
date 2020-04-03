.. index:: ! design

.. _design:

design
--------------

The attributes of a design object of which one holds cash.


Common Attributes
~~~~~~~~~~~~~~~~~

.. index:: id

``id``
    String: the id of the design.

.. index:: title

``title``
    String: the title of the location to which the design cash belongs.

.. index:: fee

``fee``
    String: the fee to buy value of that design.

.. index:: distribution_id

``distribution_id``
    String: the distribution id also used in the data base of a third party.

.. index:: wallet_image_url

``wallet_image_url``
    String: the wallet image url.

``authorized_merchant``
    Boolean: true if merchant is an authorized merchant otherwise false.

Used In
~~~~~~~

- :http:get:`ferlyapi.com/history`
- :http:get:`ferlyapi.com/list-designs`
- :http:get:`ferlyapi.com/search-market`
