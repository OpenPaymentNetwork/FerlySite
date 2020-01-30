
.. _Stripe API Calls:
.. _Stripe API:

Stripe API Calls
===============================

.. _List Stripe Sources:

List Stripe Sources
------------------------

.. http:get:: ferlyapi.com/list-stripe-sources

    Returns a list of stripe card sources saved on file to which one can use to buy Ferly Cash.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attribute.** 
            ``sources``
                A list of stripe card sources saved on file. Contains the following attributes:

                    ``id``
                        the id of the stripe source.
                    ``last_four``
                        the last four numbers on the card.
                    ``brand``
                        the brand of the source. (e.g. Visa)

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Delete-Stripe-Source:

Delete-Stripe-Source
-------------------------

.. http:post:: ferlyapi.com/delete-stripe-source

    Deletes a payment stripe source on file.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string source_id:
        Required. The id of the stripe source given from :http:get:`ferlyapi.com/list-stripe-sources`.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attribute.** 
            ``result``
                a boolean representing whether the source was found and deleted.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Purchase:

Purchase
------------------------

.. http:post:: ferlyapi.com/purchase

    Purchases Ferly cash to specified wallet design.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string source_id:
        Required. The id of the stripe source given from :http:get:`ferlyapi.com/list-stripe-sources`.

    :<json string fee:
        Required. The fee that matches the specified wallet design fee found from :http:get:`ferlyapi.com/list-designs`.

    :<json string design_id:
        Required. The wallet design id of the Ferly cash being purchased. Can be found from :http:get:`ferlyapi.com/list-designs`.

    :<json decimal amount:
        Required. The amount of Ferly cash being purchased.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attribute.** 
            ``result``
                a boolean representing whether the Ferly Cash was successfully purchased.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.
