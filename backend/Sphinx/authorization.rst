
.. _Authentication:

Authentication
==================

.. _Authorization Header:

Authorization Header
--------------------

The ``Authorization`` HTTP header is required for most API calls. The header line takes the following form:

    ``Authorization: Bearer ACCESS_TOKEN``

``ACCESS_TOKEN`` is an access token received through an :ref:`Authentication`.

.. _Signup:

Signup
-------------------------

.. http:post:: ferlyapi.com/newSignup

    Begins the signup process with Ferly.

    :reqheader Authorization: See :ref:`Authorization Header`.

    :<json string login: Required. The phone or email the user wishes to signup with.

    :<json string username: Required. The username the user wishes to signup with.

.. _Authorize UID:

Authorize UID
------------------

.. http:post:: ferlyapi.com/auth-uid

    Receive a code that validates the user's control of a UID. The client calls this API after the user enters a code after the user has called :http:post:`ferlyapi.com/newSignup`.

    :<json string factor_id: The factor_id returned from newSignup.

    :<json string code: The code entered by the user.

    :<json string recaptcha_response:
        Conveys the response provided by the invisible ReCAPTCHA widget. This field is required when the platform detects excessive attempts to guess passwords or authentication codes.

    :<json string attempt_path: The attempt path returned from newSignup.

    :<json string secret: The secret returned from newSignup.



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

.. _Set Signup Data:

Set Signup Data
---------------------

.. http:post:: ferlyapi.com/set-signup-data

    Called after :http:post:`ferlyapi.com/auth-uid` when a profile_id is not returned to continue signup process.

    :<json string first_name: First name of customer.

    :<json string last_name: Last name of customer.

    :<json string attempt_path: The attempt path returned from newSignup.

    :<json string secret: The secret returned from newSignup.

.. _Signup Finish:

Signup Finish
--------------

.. http:post:: ferlyapi.com/signup-finish

    Called after :http:post:`ferlyapi.com/set-signup-data`. Acceptance of terms and conditions of using Ferly.

    :<json bool agreed: Indicates the user agreed to the terms and conditions.

    :<json string attempt_path: The attempt path returned from newSignup.

    :<json string secret: The secret returned from newSignup.

.. _Register:

Register
------------------------

.. http:post:: ferlyapi.com/register

    Associate a device with a new customer and wallet and completes the signup process. Called after :http:post:`ferlyapi.com/signup-finish`.

    :reqheader Authorization: See :ref:`Authorization Header` The ACCESS_TOKEN the caller wants to use for future authentication is passed at this point.

    :<json string first_name:
        Required. The customer's first name.

    :<json string last_name:
        Required. The customer's last name.

    :<json string username:
        Required. The customer's username.

    :<json string profile_id:
        Required. The profile_id returned from :http:post:`ferlyapi.com/auth-uid`.

    :<json string expo_token:
        Optional. expo_token corresponding to the new device on which the account is being recovered from.

    :<json string os:
        Optional. The os on which the device is being run on.
