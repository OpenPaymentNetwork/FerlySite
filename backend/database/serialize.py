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
        'logo_image_url': design.logo_image_url,
        'title': design.title,
        'fee': str(design.fee),
        'distribution_id': design.distribution_id,
        'wallet_image_url': design.wallet_image_url,
        'field_color': design.field_color,
        'field_dark': design.field_dark,
    }

def serialize_card_request(request, card_request):
    return {
        'id': card_request.id,
        'customer_id': card_request.customer_id,
        'name': card_request.name,
        'address_line1': card_request.line1,
        'address_line2': card_request.line2,
        'city': card_request.city,
        'state': card_request.state,
        'zip':  card_request.zip_code,
        'verified': card_request.verified,
    }
