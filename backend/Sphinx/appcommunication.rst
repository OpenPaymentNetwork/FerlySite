
.. _App Communication API Calls:
.. _App API:

Communication with App Calls
===============================

.. _Get Expo Token:

Get Expo Token
-------------------------

.. http:post:: ferlyapi.com/get-expo-token

    Gets the expo-token corresponding to device.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful, the response body will be a JSON object with the following attribute:**
            ``expo_token``
                A string containing the expo token for the customer's device.

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Set Expo Token:

Set Expo Token
-------------------------

.. http:post:: ferlyapi.com/set-expo-token

    Sets the expo-token corresponding to the device.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string expo_token:
        Required. The expo-token corresponding to device.

    :statuscode 200:
        **If successful, the response body will be a JSON object with no attributes.**

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _List Designs:

List Designs
-------------------------

.. http:get:: ferlyapi.com/list-designs

    Gets all the listable designs on Ferly.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful, the response body is a JSON object with a list of design objects.** See :ref:`design`.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _List Loyalty Designs:

List Loyalty Designs
-------------------------

.. http:get:: ferlyapi.com/list-loyalty-designs

    Gets all the loyalty designs on Ferly.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful, the response body is a JSON object with a list of loyalty design objects.** See :ref:`design`.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Get Ferly Cash Design:

Get Ferly Cash Design
-------------------------

.. http:get:: ferlyapi.com/get-ferly-cash-design

    Gets the Ferly Cash design.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful, the response body is a JSON object with the Ferly Cash design object.** See :ref:`design`.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Search Market:

Search Market
------------------------

.. http:get:: ferlyapi.com/search-market

    Searches all designs listed in the Marketplace in the Ferly App that contain the given input string.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :query query:
        Search text of the design name.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attribute:** 
            ``results``
                A list of design objects. See :ref:`design`.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.
