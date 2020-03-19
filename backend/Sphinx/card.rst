
.. _Card API Calls:
.. _Card API:

Card API Calls
===============================


.. _Add A Card:

Add A Card
------------------------

.. http:post:: ferlyapi.com/add-card

    Associate a Ferly Card with the customer. The customer then can use the card to redeem gift value.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string pan:
        Required. The ferly card number.

    :<json string pin:
        Required. The pin to use at the point of sale during redemption.

    :statuscode 200:
        If successful, the response body is a JSON object with the following attribute:
            ``result``
                A boolean representing whether the card was associated with the customer successfully.

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Delete A Card:

Delete A Card
-------------------------

.. http:post:: ferlyapi.com/delete-card

    Disassociate the ferly card and the customer. The customer may no longer redeem gift value with that gift card. The card may then be associated with any customer including the same customer through :http:post:`ferlyapi.com/add-card`.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string card_id:
        Required. The card identification number. This may be obtained from :http:get:`ferlyapi.com/profile`.

    :statuscode 200:
        **If successful, the response body is a JSON object with no attributes:**

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Change Card Pin:

Change Card Pin
------------------------

.. http:post:: ferlyapi.com/change-pin

    Changes the pin used in conjunction with the Ferly card that will be used at point of sale during redemption. If no card is currently associated with the customer then the pin should be set during :http:post:`ferlyapi.com/add-card`. 


    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string card_id:
        Required. The card identification number. This may be obtained from :http:get:`ferlyapi.com/profile`.

    :<json string pin:
        Required. The new pin to use at point of sale during redemption.

    :statuscode 200:
        **If successful, the response body is a JSON object with no attributes:**

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Suspend Card:

Suspend Card
-------------------------------


.. http:post:: ferlyapi.com/suspend-card


    Suspends card associated with customer so that the card's ability to spend cash is disabled without removing the card association to the customer.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string card_id:
        Required. The card identification number. This may be obtained from :http:get:`ferlyapi.com/profile`.

    :statuscode 200:
        **If successful, the response body is a JSON object with no attributes:**

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Unsuspend Card:

Unsuspend Card
-------------------------------


.. http:post:: ferlyapi.com/unsuspend-card


    Unsuspends card associated with customer so that the card's ability to spend cash is re-enabled.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string card_id:
        Required. The card identification number. This may be obtained from :http:get:`ferlyapi.com/profile`.

    :statuscode 200:
        **If successful, the response body is a JSON object with no attributes:**

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Verify Address:

Get Address On File To Send Ferly Card
---------------------------------------


.. http:get:: ferlyapi.com/verify-address

    Gets the last address the customer had a Ferly card sent to them.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attributes:**
            ``id``
                A id of the card request.
            ``customer_id``
                The id of the customer.
            ``name``
                The name of the customer.
            ``address_line1``
                The first line of address.
            ``address_line2``
                The second line of address.
            ``city``
                The city of the customer's address.
            ``state``
                The state of the customer's address.
            ``zip``
                The zip code of the customer's address.
            ``verified``
                Whether the customer has verified their address before.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Request Card:

Request Card
---------------------------------------


.. http:post:: ferlyapi.com/request-card

    Verify and save the United States mailing address that a customer requested a new Ferly Card be mailed to.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string name:
        Required. The customer name.

    :<json string line1:
        Required. The first line of mailing address.

    :<json string line2:
        Required. The second line of mailing address.

    :<json string city:
        Required. The city of the mailing address.

    :<json string state:
        Required. The two digit state abbreviation of the mailing address.

    :<json string zip_code:
        Required. The five digit zip code of the mailing address.

    :<json string verified:
        Optional. A field given to help determine if the address has been verified by the customer.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attributes:**
            ``name``
                The name of the customer.
            ``line1``
                The first line of address.
            ``line2``
                The second line of address.
            ``city``
                The city of the customer's address.
            ``state``
                The state of the customer's address.
            ``zip_code``
                The zip code of the customer's address.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.