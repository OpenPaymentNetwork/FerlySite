
.. _Customer API Calls:
.. _Customer API:

Customer API Calls
===============================


.. _Obtain Customer Profile:

Obtain Customer Profile
------------------------

.. http:get:: ferlyapi.com/profile

    Gets the customer profile information.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        If successful the response body is a JSON object with these attributes:
            ``first_name``
                A string containing the customer's first name.
            ``last_name``
                A string containing the customer's last name.
            ``username``
                A string containing the customer's username.
            ``profile_image_url``
                A string containing the url to the customer's profile image.
            ``amounts``
                An array of amounts of customer's Ferly cash.
            ``uids``
                A array of strings containing the customer's uids.
            ``recents``
                An array of recent customer objects who the customer has sent money to. See :ref:`customer`.
            ``cards``
                A card object. See :ref:`card`.

        If unsuccessful the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Get Customer Name:

Get Customer Name
------------------------

.. http:get:: ferlyapi.com/get-customer-name

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string recipient_id:
        Required. The id of recipient.

    :statuscode 200:
        If successful the response body is a JSON object with the following attribute: 
            ``name``
                A string containing the full name of customer in the form first name last name. (e.g. John Smith)

        If unsuccessful the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Upload Profile Image:

Upload Profile Image
------------------------

.. http:post:: ferlyapi.com/upload-profile-image

    :reqheader Authorization: See :ref:`Authorization Header`.
    
    A multipart/form-data object should be passed to the body with the following key value pairs. 
        ``image``
             An object with these attributes:

                 ``uri``
                     A string containing the uri of the image.
                 ``name``
                     A string prefixed with "photo." followed by the filetype. (e.g. photo.png)
                 ``image``
                     A string prefixed with "image/" followed by the filetype. (e.g. image/png)

    An easy way to create the form data object is with Javascript.

    :statuscode 200:
        **If successful the response body will be a JSON object with no attributes.**

        If unsuccessful the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Search Customers:

Search Customers
------------------------

.. http:get:: ferlyapi.com/search-customers

    Searches for and returns all customers whose first or last name contain the given input.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :query query:
        Search text of the customer name.

    :statuscode 200:
        **If successful the response body is a JSON object with the following attribute.** 
            ``results``
                A list of ``customer`` objects. See :ref:`customer`.

        **If unsuccessful the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.` 

.. _Edit Profile:

Edit Profile
------------------------

.. http:post:: ferlyapi.com/edit-profile

    Updates a customer's profile information.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string username:
        Required. The username to be used by the customer.

    :<json string first_name:
        Required. The first name to be used by the customer.

    :<json string last_name:
        Required. The last name to be used by the customer.

    :statuscode 200:
        **If successful the response body will be a JSON object with no attributes.**

        If unsuccessful the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _History:

History
------------------------

.. http:get:: ferlyapi.com/history

    Request and return the customer's transfer history.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json integer limit:
        Optional. The amount of results to return.

    :<json integer offset:
        Optional. The offset of when to begin returning results. (Skips results until offset reached.)

    :statuscode 200:
        **If successful the response body is a JSON object with the following attributes:**
            ``has_more``
                A boolean representing if there are more history results.

            ``history``
                A list of history objects that contain the following attributes:

                    ``id``
                        A string containing the transfer id.
                    ``sent_count``
                        If this transfer is an invitation, this attribute indicates how many times the invitation message has been sent. Apps may use this information to limit the number of times users are permitted to re-send invitation messages. This attribute is empty if the transfer is not an invitation.
                    ``amount``
                        String containing a decimal amount.
                    ``transfer_type``
                        A string containing the type of transfer.
                    ``counter_party``
                        A string containing the other party's name to whom the transfer was with.
                    ``design``
                        A design object. See :ref:`design`.
                    ``design_title``
                        A string containing the title or name of the design location.
                    ``design_logo_image_url``
                        A string containing the design logo image url.
                    ``timestamp``
                        A string containing the timestamp of the history item.
                    ``trade_Designs_Received``
                        An array of the titles of the designs that received cash in a trade exchange.

        **If unsuccessful the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Send:

Send Cash
------------------------

.. http:post:: ferlyapi.com/send

    Send Money as an invitation containing a code to redeem the cash to a non Ferly user or directly into the wallet of an existing Ferly user.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json decimal amount:
        Required. The amount of money to send.

    :<json string design_id:
        Required. The id of the close loop design location to which the cash belongs.

    :<json string recipient_id:
        Required. The uid (email prefixed with email: or phone number prefixed with phone:) of the recipient or their Ferly customer id.

    :<json string sender:
        Optional. The uid (email prefixed with email: or phone number prefixed with phone:) of the sender or their Ferly customer id.

    :<json string message:
        Optional. A custom message sent to the recipient along with the cash.

    :<json string invitation_type:
         Optional string specifying link, code_private, or code_shared. This attribute applies only when the transfer is an invitation to the recipient. If the invitation type is link, the platform sends a web link (URL) for accepting the invitation. If the invitation type is code_private, the platform sends a secret alphanumeric code to the recipient; the sender will not be allowed to see the code. If the invitation type is code_shared, the platform sends a secret alphanumeric code and allows other transfer participants to see the code for the purpose of helping the recipient.

    :<json integer invitation_code_length:
        Optional number specifying how many characters should be in the invitation code (if the transfer is an invitation). A minimum of 6 characters is required. More characters mean the code takes longer to enter but is less guessable. The code consists of digits and uppercase letters. Apps may present invitation codes with embedded dashes (-) for readability; the platform ignores the dashes.

    :statuscode 200:
        Successful. The response body is a JSON object with the following attribute:
            ``transfer``
                A TransferDetail object. See :ref:`TransferDetail`.

    :statuscode 400:
        The parameters are not invalid.
    :statuscode 401:
        The access token is missing or not valid.
    :statuscode 403:
        The access token is valid but the app is not authorized to access this function.

.. _Transfer:

Request Transfer Details
------------------------

.. http:get:: ferlyapi.com/transfer

    Requests and returns transfer details of a transfer mostly relating to buy transfers. To get full transfer details use :http:get:`ferlyapi.com/get_transfer_details`.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string transfer_id:
        Required. The id of the transfer of which to return the transfer details.

    :statuscode 200:
        **If successful the response body is a JSON object with the following attributes:**
            ``card_acceptor``
                If this transfer is a payment using a card and the platform knows the location of the receiving merchant, this attribute is an object containing ``location_id`` and ``location_name``, both of which are short strings. If the transfer is not a card payment or the location is not known, this attribute is not provided.

            ``pan_redacted``
                The PAN (primary account number) of the card that was used, with all but the last 4 digits redacted using ``X`` characters.

            ``available_amount``
                When the ``reason`` is ``insufficient_funds``, this attribute is a decimal string containing the amount of funds the sender had that qualified for payment to the merchant. Otherwise, this attribute is an empty string.

            ``reason``
                An identifier describing the reason why the card payment failed. The possible values include:

                    ``denied_externally``
                        The payment was denied by the  merchant or network.

                    ``card_suspended``
                        The card is suspended.

                    ``card_holder_not_found``
                        No wallet is linked to the card.

                    ``merchant_not_found``
                        The receiving merchant could not be identified.

                    ``preauth_not_allowed``
                        The merchant does not allow pre-authorized transactions.

                    ``transaction_type_not_supported``
                        The specified transaction type is not supported.

                    ``cash_back_not_supported``
                        Cash back transactions are not supported.

                    ``no_funds``
                        The sender has no funds accepted by the merchant.

                    ``insufficient_funds``
                        The sender does not have sufficient funds accepted by the merchant.

                    ``reversal_original_not_found``
                        A reversal of a transfer was attempted, but the original transfer could not be found.

                    ``reversal_system_error``
                        An internal system error occurred while reversing the transfer.

            ``expiration``
                When an invitation will expire automatically.
            ``convenience_fee``
                A decimal number indicating the convenience fee of the transfer.

            ``cc_brand``
                A string representing the card type used to purchase gift value. (e.g. Visa)

            ``cc_last4``
                A string representing the last four digits of the card number used to purchase gift value.

            ``message``
                A string containing the message sent in conjuction with :http:post:`ferlyapi.com/add-card`.

            ``counter_party_profile_image_url``
                A string containing the profile image url.

        **If unsuccessful the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Trade:

Request Trade
------------------------

.. http:post:: ferlyapi.com/trade

    Initiates a trade request that exchanges one or more design cash for one or more other design cash.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json array amounts:
        Required. An array of string amounts each being the amount of corresponding loop_id that is being transferred.

    :<json array loop_ids:
        Required. An array of string ids each being the id of the design cash where the corresponding amount will be transferred.

    :<json array expect_amounts:
        Required. An array of string amounts each being the amount of corresponding loop_id that is being received from the trade.

    :<json array expect_loop_ids:
        Required. An array of string ids each being the id of the design cash where the corresponding amount will be received from the trade.

    :<json open_loop:
        Required. True if converting open loop cash from ACH transfer to Ferly Cash.

    :statuscode 200:
        **If successful the response body is a JSON object with the following attribute:**
            ``transfer_id``
                The id needed for the accept_trade call.

        **If unsuccessful the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Accept Trade:

Accept and Complete Trade
------------------------

.. http:post:: ferlyapi.com/accept_trade

    Accepts and Completes the trade initiated in :http:post:`ferlyapi.com/trade` call.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json array loop_ids:
        Required. The expect_loop_ids from the trade call.

    :<json string transfer_id:
        Required. The transfer_id from the trade call.

    :<json open_loop:
        Required. True if converting open loop cash from ACH transfer to Ferly Cash.

    :statuscode 200:
        **If successful the response body is a JSON object with the following attribute:**
            ``transfer_id``
                The id used to get transfer details if needed from :http:get:`ferlyapi.com/transfer` call.

        **If unsuccessful the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.


.. _Get ACH ACCOUNT:

Get ACH Account
------------------------

.. http:post:: ferlyapi.com/get-ach

    Get or create a matching funding proxy for the ACH network.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :statuscode 200:
        **If successful the response body is a JSON object with the following attributes:**
            ``routing_number``
                The routing number of the ACH funding proxy.
            ``account_number``
                Generated automatically.
            ``created``
                The UTC ISO 8601 when the funding proxy was created.

        **If unsuccessful the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.