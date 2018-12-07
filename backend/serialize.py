def serialize_invitation(request, invitation):
    return {
        'id': invitation.id,
        'created': str(invitation.created),
        'recipient': invitation.recipient,
        'status': invitation.status
    }


def serialize_user(request, user):
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'picture': user.image_url
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
