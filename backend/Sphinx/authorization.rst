
.. _Authentication:

Authentication
==================

.. _Authorization Header:

Authorization Header
--------------------

The ``Authorization`` HTTP header is required for most API calls. The header line takes the following form:

    ``Authorization: Bearer ACCESS_TOKEN``

``ACCESS_TOKEN`` is an access token received through :http:post:`ferlyapi.com/newSignup` or :http:post:`ferlyapi.com/recover` or created by client and sent in the authorization header in those same two calls. This token should not be shared and kept secret.

.. _Signup:

Signup
-------------------------

.. http:post:: ferlyapi.com/newSignup

    Begins the signup process with Ferly.

    :reqheader Authorization: Optional. See :ref:`Authorization Header`. 

    :<json string login: Required. The phone or email the user wishes to signup with.

    :<json string username: Required. The username the user wishes to signup with. It must contain greaten than 3 but less than 21 characters, start with a letter, and contain only letters, numbers, and periods.

    :statuscode 200:
        **If successful, the response body will be a JSON object with the following attributes:**
            ``token``
                The access token to be used in future calls. See :ref:`Authorization Header`.
            ``attempt_path``
                The path inside the platform API for updating or accessing the new authentication attempt. It looks like ``/aa/<attempt_id>/``.

            ``secret``
                A string that authenticates the user's device for the duration of the authentication attempt. The client should not share this string with other devices. In subsequent authentication API calls, the client must send the secret.

            ``factor_id``
                An opaque random string that identifies which factor the user should attempt to authenticate. The factor_id changes for each authentication factor attempt.

            ``code_length``
                The length of the code the user should enter. The length is currently either 6 or 9 digits depending on the authentication flow type, but the platform may expand the code length if necessary.

            ``revealed_codes``
                In development sandboxes and testing environments, this is a list of human-readable strings that reveal the authentication codes sent to the user through email, SMS, or another channel. This allows testers to skip the communication channel. In production, this attribute does not exist.

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Authorize UID:

Authorize UID
------------------

.. http:post:: ferlyapi.com/auth-uid

    Receive a code that validates the user's control of a UID. The client calls this API after the user enters a code after the user has called :http:post:`ferlyapi.com/newSignup`.

    :<json string factor_id: Required. The factor_id returned from newSignup.

    :<json string code: Required. The code entered by the user.

    :<json string recaptcha_response:
        Conveys the response provided by the invisible ReCAPTCHA widget. This field is required when the platform detects excessive attempts to guess passwords or authentication codes.

    :<json string attempt_path: Required. The attempt path returned from newSignup.

    :<json string secret: Required. The secret returned from newSignup.

        **If successful, the response body will be a JSON object with the following attributes:**
            ``profile_id``
                This is the id of a registered profile. This field will only have data if the user is already registered and should be logged in instead of completing registration.

            ``expo_token``
                This is the registered profile's expo_token. It will only have data if profile_id is returned and we have the expo_token on file.
            ``os``
                This is the registered profile's os. It will only have data if profile_id is returned and we have the os on file.

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Login:

Login
-------------------------

.. http:post:: ferlyapi.com/login

    Called after :http:post:`ferlyapi.com/auth-uid` when a profile_id is returned. Allows a user to be authenticated to a new device and logged in when finding that their account already exists on file during signup.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string profile_id:
        Required. The profile_id returned from :http:post:`ferlyapi.com/auth-uid`.

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

.. _Set Signup Data:

Set Signup Data
---------------------

.. http:post:: ferlyapi.com/set-signup-data

    Called after :http:post:`ferlyapi.com/auth-uid` when a profile_id is not returned to continue signup process.

    :<json string first_name: Required. First name of customer.

    :<json string last_name: Required. Last name of customer.

    :<json string attempt_path: Required. The attempt path returned from newSignup.

    :<json string secret: Required. The secret returned from newSignup.

    :statuscode 200:
        **If successful, the response body will be a JSON object with no attributes.**

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Signup Finish:

Signup Finish
--------------

.. http:post:: ferlyapi.com/signup-finish

    Called after :http:post:`ferlyapi.com/set-signup-data`. Acceptance of terms and conditions of using Ferly.

    :<json bool agreed: Required. Indicates the user agreed to the terms and conditions.

    :<json string attempt_path: Required. The attempt path returned from newSignup.

    :<json string secret: Required. The secret returned from newSignup.

        **If successful, the response body will be a JSON object with the following attribute:**
            ``profile_id``
                This is the id of a registered profile.

        If unsuccessful, the response body is a JSON object with one of the following attributes:
            ``invalid``
                A string explaining why the input was invalid.
            ``error``
                A string explaining the error that occured.

.. _Register:

Register
------------------------

.. http:post:: ferlyapi.com/register

    Associate a device with a new customer and wallet and completes the signup process. Called after :http:post:`ferlyapi.com/signup-finish`.

    :reqheader Authorization: See :ref:`Authorization Header`. This is the token received from :http:post:`ferlyapi.com/newSignup`.

    :<json string first_name:
        Required. The customer's first name.

    :<json string last_name:
        Required. The customer's last name.

    :<json string username:
        Required. The customer's username.

    :<json string profile_id:
        Required. The profile_id returned from :http:post:`ferlyapi.com/signup-finish`.

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
