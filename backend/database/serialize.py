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
        'profile_image_url': customer.profile_image_url
    }


def serialize_design(request, design):
    return {
        'id': design.id,
        'wingcash_id': design.wc_id,
        'logo_image_url': design.logo_image_url,
        'title': design.title,
        'fee': str(design.fee),
        'distribution_id': design.distribution_id,
        'wallet_image_url': design.wallet_image_url
    }
