
.. _Invitation API Calls:
.. _Invitation  API:

Invitation  API Calls
===============================

.. _Invite:

Invite
------------------------

.. http:post:: ferlyapi.com/invite

    Sends an invitation to join Ferly to an email or phone number.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string recipient:
        Required. The email or phone number to whom the invitation should be sent.

    :statuscode 200:
        **If successful, the response body will be a JSON object with no attributes.**

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Accept Code:

Accept Code
-------------------------------

.. http:post:: /accept-code

    Redeems and completes and invitation sent with cash so that the cash sent gets put into the customers wallet.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string code:
        Required. The code given in the cash invitation.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attribute.** 
            ``transfer``
                The updated :ref:`TransferDetail` object.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Get Invalid Code Count:

Get Invalid Code Count
-------------------------------

.. http:get:: ferlyapi.com/get-invalid-code-count

    Returns the amount of invalid invitation codes the user has entered for the day.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attribute.** 
            ``count``
                The invalid count for the current day.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Update Invalid Code Count:

Update Invalid Code Count
---------------------------------------


.. http:post:: ferlyapi.com/update-invalid-code-count

    Updates the amount of invalid invitation codes the user has entered for the day.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json bool invalid_result:
        Required. Whether the last invitation code entered was valid or not.

.. _Retract:
.. _Resend:

Transfer API
---------------------------------------


.. http:post:: ferlyapi.com/retract

    See :http:post:`ferlyapi.com/retract`

.. http:post:: ferlyapi.com/resend

    See :http:post:`ferlyapi.com/retract`

.. http:get:: ferlyapi.com/get_transfer_details

    Used to control and monitor the cash invitation. :http:post:`ferlyapi.com/retract` cancels the cash invitation so that the cash invitation code becomes invalid. :http:post:`ferlyapi.com/resend` sends the recipient a reminder cash invitation. :http:post:`ferlyapi.com/get_transfer_details` gets information about the state of a cash invitation.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string transfer_id:
        Required. The transfer id of the cash invitation.

    :statuscode 200:
        Successful. The response body is a JSON object with the following attribute:
            ``transfer``
                A TransferDetail object. See :ref:`TransferDetail`

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

    :statuscode 400:
        The parameters are not invalid.
    :statuscode 401:
        The access token is missing or not valid.
    :statuscode 403:
        The access token is valid but the app is not authorized to access this function.
