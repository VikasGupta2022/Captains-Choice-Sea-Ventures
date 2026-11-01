from app.routes.view_routes import templates
from app.services.booking_service import booking_service
from unittest.mock import MagicMock

def test_all_templates_render():
    req = MagicMock()
    mock_booking = MagicMock(
        booking_ref='GSB-20261101-ABCD',
        route_name='Gateway of India to Mandwa',
        trip_type='one_way',
        boat_name='Speedster 24',
        travel_date='2026-11-05',
        time_slot='10:00 AM',
        passengers=4,
        customer_name='Test Passenger',
        customer_phone='917506920614',
        total_fare=6500,
        advance_required=2000,
        balance_due=4500,
        razorpay_payment_id='pay_123',
        razorpay_order_id='ord_123'
    )
    ctx = {
        'request': req,
        'app_name': "Captain's Choice Sea Ventures",
        'app_tagline': 'Fastest Transfers',
        'whatsapp_phone': '917506920614',
        'whatsapp_display_phone': '+91 7506920614',
        'whatsapp_default_url': 'https://wa.me/917506920614',
        'jetty_location': 'Jetty No. 5, Gateway of India',
        'google_maps_url': 'https://maps.google.com',
        'contact_email': 'gatewayspeedboat@gmail.com',
        'is_mock': True,
        'routes': booking_service.get_routes(),
        'boats': booking_service.get_fleet(),
        'addons': booking_service.get_addons(),
        'time_slots': booking_service.get_time_slots(),
        'active_nav': 'home',
        'selected_category': 'all',
        'preselect_boat': '',
        'preselect_route': '',
        'preselect_trip_type': 'one_way',
        'razorpay_key_id': 'rzp_test_123',
        'booking': mock_booking,
        'selected_addons': [],
        'wa_support_url': 'https://wa.me/917506920614',
        'bookings': [mock_booking],
        'payments': [],
        'events': [],
        'total_revenue': 2000
    }

    template_names = [
        'base.html',
        'index.html',
        'fleet.html',
        'booking.html',
        'confirmation.html',
        'admin.html'
    ]

    for t_name in template_names:
        tpl = templates.get_template(t_name)
        rendered = tpl.render(ctx)
        assert len(rendered) > 100
        assert "7506920614" in rendered
