
.. _Recovery API Calls:
.. _Recovery API:

Recovery API Calls
===============================


.. _Recover:


Recover
------------------------

.. http:post:: ferlyapi.com/recover

     Recovers a Ferly Users account

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string login:
        Required. The email or phone number the customer used to signup or put in their recovery settings.

    :statuscode 200:
        **If successful, the response body is a JSON object with the following attributes:** 
            ``login_type``
                A string representing whether the login type is an email or phone number.
            ``secret``
                A string that authenticates the user's device for the duration of the authentication attempt. The client should not share this string with other devices. In subsequent authentication API calls, the client must send the secret.
            ``attempt_path``
                The path inside the platform API for updating or accessing the new authentication attempt. It looks like ``/aa/<attempt_id>``.
            ``code_length``
                The length of the code the user should enter. The length is currently either 6 or 9 digits depending on the authentication flow type, but the platform may expand the code length if necessary.
            ``factor_id``
                An opaque random string that identifies which factor the user should attempt to authenticate. The factor_id changes for each authentication factor attempt.
            ``revealed_codes``
                In development sandboxes and testing environments, this is a list of human-readable strings that reveal the authentication codes sent to the user through email, SMS, or another channel. This allows testers to skip the communication channel. In production, this attribute does not exist.

        **If unsuccessful, the response body is a JSON object with one of the following attributes:**
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Recover Code:

Recover Code
------------------------

.. http:post:: ferlyapi.com/recover-code

     Verify's the code to recover the account is correct and if so completes the recover process by remapping the account to the new device token.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string code:
        Required. The secret code sent to the recovery email or phone number.

    :<json string secret:
        Required. The secret returned from :http:post:`ferlyapi.com/recover`.

    :<json string factor_id:
        Required. The factor_id returned from :http:post:`ferlyapi.com/recover`.

    :<json string recaptcha_response:
        Conveys the response provided by the invisible ReCAPTCHA widget. This field is required when the platform detects excessive attempts to guess passwords or authentication codes..

    :<json string attempt_path:
        Required. The attempt_path returned from :http:post:`ferlyapi.com/recover`.

    :<json string expo_token:
        Optional. expo_token corresponding to the new device on which the account is being recovered from.

    :<json string os:
        Optional. The os on which the device is being run on.

    :statuscode 200:
        **If successful, the response body will be a JSON object with no attributes.**

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Add a UID:

Add UID
-------------------------------


.. http:post:: ferlyapi.com/add-uid

    Begin adding a UID (email address or SMS phone number) to the wallet. The platform will send a random code through the specified communication channel. After your app receives a response from this API call, it should prompt the user to enter the received code. Once the user inputs the code, your app should call :http:post:`ferlyapi.com/confirm-uid` to finish adding the UID.

    :Permission Required: change_settings. Change the authenticated profile’s personal settings like the password or login information. Used in Settings API Calls.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string login:
        Required. The email address or phone number to add. The formatting is flexible: email addresses may be capitalized and phone numbers may contain dashes and parentheses, depending on the country.
    :<json string uid_type:
        Required. If provided, must be either ``email`` or ``phone``.

    :statuscode 200:
        **If successful, the response body will be a JSON object with the following attributes:**
            ``attempt_id``
                A string that identifies this attempt to add a UID.
            ``secret``
                A string that authenticates the user's device for the duration of the attempt to add a UID.
            ``code_length``
                The length of the code the user should enter. The length is currently either 6 or 9 digits depending on the authentication flow type, but the platform may expand the code length if necessary.
            ``revealed_codes``
                In development sandboxes and testing environments, this is a list of human-readable strings that reveal the authentication codes sent to the user through email, SMS, or another channel. This allows testers to skip the communication channel. In production, this attribute does not exist.

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Confirm Uid:

Finish Adding a UID
-------------------

.. http:post:: ferlyapi.com/confirm-uid

    Finish adding a UID (email address or SMS phone number) to the wallet. The app calls this after :http:post:`ferlyapi.com/add-uid`.

    :Permission Required: change_settings. Change the authenticated profile’s personal settings like the password or login information. Used in Settings API Calls.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string attempt_id:
        Required. The ``attempt_id`` received from the :http:post:`ferlyapi.com/add-uid` API call.
    :<json string secret:
        Required. The ``secret`` received from the :http:post:`ferlyapi.com/add-uid` API call.
    :<json string code:
        Required. The code entered by the user.
    :<json string replace_uid:
        Optional. If provided, and the code entry is successful, the platform will remove the specified UID from the wallet while adding the new UID. This is a way to let users "edit" their email address or phone number.
    :<json string recaptcha_response:
        Conveys the response provided by the invisible ReCAPTCHA widget. This field is required when the platform detects excessive attempts to guess passwords or authentication codes.

    :statuscode 200:
        **If successful, the response body will be a JSON object with no attributes.**

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.
