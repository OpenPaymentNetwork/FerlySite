.. index:: ! TransferDetail

.. _TransferDetail:

TransferDetail
--------------

Provides full details about a transfer.


Common Attributes
~~~~~~~~~~~~~~~~~

.. index:: end

``end``
    String: the :term:`ISO 8601` timestamp when the transfer ended, or ``null``. This is set only once. The platform sometimes resumes transfers after they end, but the ``end`` field records only the first time the transfer ended.

.. index:: run_state

``run_state``
    String: one of ``ended``, ``paused``, ``stuck``, ``runnable``, or ``running``. If the transfer is completed or canceled, run_state is usually ``ended``. If the transfer is waiting for something, run_state is ``paused``. If the transfer is doing something now, run_state is ``running``. If there was an internal error, run_state may be ``stuck`` or ``runnable``.

.. index:: activity_count

``activity_count``
    Integer: the number of activities executed so far by this transfer.  Webhooks can use this information to ignore transfer states received out of order.

.. index:: sender_personal_id

``sender_personal_id``
    String: the ID of the personal profile who sent this transfer. For example, when John Doe sends cash from his business named ACME, the ``sender_id`` is ACME's profile ID and the ``sender_personal_id`` is John Doe's profile ID. When John Doe sends from his own wallet, the ``sender_id`` and ``sender_personal_id`` are both John Doe's profile ID.  When the sender's personal profile ID is unknown, this is ``null``.

.. index:: recipient_personal_id

``recipient_personal_id``
    String: the ID of the personal profile who received this transfer. The value is ``null`` when waiting for a payment code or invitation.

.. index:: private

``private``
    True if the transfer is private.

.. index:: posts

``posts``
    A list of Post objects created by this transfer.

.. index:: steps_html

``steps_html``
    HTML describing the steps (also known as activities) taken by the transfer from the perspective of the authenticated profile. Most of the content is in an <ol> (ordered list) tag. The number of steps per transfer depends on the transfer type, but typical transfers have at least 2 steps and usually fewer than 20 steps. Many activities exist only for internal bookkeeping, so not every activity is visible.

.. index:: payment_codes

``payment_codes``
    If the authenticated profile is the sender, this is the list of the sender's active :ref:`PaymentCode` objects for this transfer. Otherwise this list is empty.

.. index:: loyalty

``loyalty``
    If the recipient issued loyalty cash to the sender as part of this transfer, this attribute lists what loyalty cash was sent.

.. index:: stakeholders

``stakeholders``
    The list of participants (stakeholders) in the transfer.  Each item in the list is an object containing ``id`` and ``roles`` attributes, where ``id`` is a profile ID and ``roles`` is the list of roles (as strings) the profile has in the transfer.  The possible roles are currently:

        - distributor
        - distribution_recipient
        - fee_recipient
        - issuer
        - merchant
        - recipient
        - sender
        - settler

.. index:: card_acceptor

``card_acceptor``
    If this transfer is a payment using a card and the platform knows the location of the receiving merchant, this attribute is an object containing ``location_id`` and ``location_name``, both of which are short strings. If the transfer is not a card payment or the location is not known, this attribute is not provided.

.. index:: invitation_code

``invitation_code``
    If this transfer is an invitation, the authenticated profile is a participant in the transfer, the recipient has been invited to the transfer using an invitation code, and the ``invitation_type`` for the transfer is ``code_shared``, this attribute reveals the invitation code so that others can help the recipient. If only the recipient should see the code, the ``invitation_type`` should instead be set to ``code_private``.

.. index:: sent_count

``sent_count``
    If this transfer is an invitation, this attribute indicates how many times the invitation message has been sent. Apps may use this information to limit the number of times users are permitted to re-send invitation messages. This attribute is not present if the transfer is not an invitation.

.. index:: alarms

``alarms``
    Some transfers have timed event triggers called alarms; this list attribute reveals certain kinds of alarms. Each item in the list is an object with ``name`` (a string) and ``timestamp`` (an ISO 8601 string). One important alarm is named ``alarm.expire_invitation``, which indicates when an invitation will expire automatically.


Redeem Transfer Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~

These attributes are included in the :ref:`TransferDetail` object when the transfer ``workflow_type`` is ``redeem`` or ``fxdeposit``.

.. index:: rdfi_name

``rdfi_name``
    The name of the receiving depository financial institution (RDFI).

.. index:: account_number_redacted

``account_number_redacted``
    The receiving account number.

.. index:: redeem_amount

``redeem_amount``
    The amount to be received into the RDFI account.

.. index:: fee_amount

``fee_amount``
    The fee paid for the transfer.

.. index:: ach_type

``ach_type``
    A string: either 'checking' or 'savings'.

.. index:: effective_date

``effective_date``
    The date when the money is scheduled to arrive.



FX Deposit Transfer Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These attributes are included in the :ref:`TransferDetail` object when the transfer ``workflow_type`` is ``fxdeposit``. (The ``redeem`` transfer attributes are included as well.)

.. index:: dfi_error

``dfi_error``
    If an error occurred in the transfer, this object may be added to the transfer. It has two attributes: ``error``, an error code as a string, and ``message``, a string.

.. index:: dfi_result

``dfi_result``
    If the transfer was successful, this is an object containing information provided by the receiving depository financial institution. The content of the object varies based on the RDFI and the method of integration.

.. index:: hold_seconds

``hold_seconds``
    The number of seconds this transfer is to be placed on hold before automatic completion. 1800 (30 minutes) is a common value.

.. index:: holding_until

``holding_until``
    If the transfer is on hold, this attribute contains the :term:`ISO 8601` timestamp indicating when the transfer will be completed automatically.

.. index:: dest_amount
.. index:: dest_currency

``dest_amount`` and ``dest_currency``
    The amount to be deposited after currency exchange.

.. index:: source_amount
.. index:: source_currency

``source_amount`` and ``source_currency``
    The amount provided by the sender, including fees, before currency exchange.

.. index:: source_amount_without_fee

``source_amount_without_fee``
    The amount provided by the sender, without fees.

.. index:: fx_rate

``fx_rate``
    The currency exchange rate, as a string. As an example, if 1 USD = 18.4 MXN, and the sender converts from USD to MXN, then ``fx_rate`` is ``18.4``.

.. index:: fx_quote_id

``fx_quote_id``
    String: the currency exchange quote ID provided at the start of the transfer.

.. index:: fx_holder_id

``fx_holder_id``
    The profile ID of the holder who provided currency exchange services for this transfer.



Bill Transfer Attributes
~~~~~~~~~~~~~~~~~~~~~~~~

These attributes are included in the :ref:`TransferDetail` object when the transfer ``workflow_type`` is ``bill``.

.. index:: confirmed

``confirmed``
    Boolean: True if the sender has confirmed that the payment has been sent.  Note that the user may still cancel after confirming payment.

.. index:: reminder_count

``reminder_count``
    Integer: The number of times the platform has sent an email requesting payment for this transfer.

.. index:: bankcard_number

``bankcard_number``
    String: The payee account number.  The customer should use the ``bankcard_number`` as the account ID when filling out the bill payment form so the platform can uniquely identify the customer.

.. index:: design_id

``design_id``
    String: The ID of the cash design the platform will provide upon payment.

.. index:: issuer_id

``issuer_id``
    String: The profile ID of the issuer of the selected cash design.

.. index:: agreement_id

``agreement_id``
    String: The ID of the agreement that allows the distributor (who is also the transfer recipient, in this case) to distribute the cash.

.. index:: confirm_timestamp

``confirm_timestamp``
    String: The :term:`ISO 8601` date when the customer confirmed payment. May be ``null``.

.. index:: declared_bank

``declared_bank``
    String: The name of the bank the customer sent payment from, as declared at payment confirmation. May be ``null``.

.. index:: declared_amount

``declared_amount``
    String: The amount of the payment as declared by the customer. May be ``null``.

.. index:: declared_date

``declared_date``
    String: The date of the payment as declared by the customer, in ``YYYY-MM-DD`` format.  May be ``null``, and may be different from ``confirm_timestamp``.


Card Payment Error Transfer Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These attributes are included in the :ref:`TransferDetail` object when the transfer ``workflow_type`` is ``card_payment_error``. A card payment error transfer is created (for informational purposes) when a card payment fails.

.. index:: pan_redacted

``pan_redacted``
    The PAN (primary account number) of the card that was used, with all but the last 4 digits redacted using ``X`` characters.

.. index:: reason

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

.. index:: available_amount

``available_amount``
    When the ``reason`` is ``insufficient_funds``, this attribute is a decimal string containing the amount of funds the sender had that qualified for payment to the merchant. Otherwise, this attribute is an empty string.




Used In
~~~~~~~

- :http:post:`ferlyapi.com/Send`
