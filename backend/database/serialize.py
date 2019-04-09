def serialize_invitation(request, invitation):
    return {
        'id': invitation.id,
        'created': str(invitation.created),
        'recipient': invitation.recipient,
        'status': invitation.status
    }


def serialize_customer(request, customer):
    return {
        'id': customer.id,
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'username': customer.username,
        'picture': customer.image_url
    }


def serialize_design(request, design):
    return {
        'id': design.id,
        'wingcash_id': design.wc_id,
        'url': design.image_url,
        'title': design.title,
        'distribution_id': design.distribution_id,
        'wallet_url': design.wallet_url
    }
