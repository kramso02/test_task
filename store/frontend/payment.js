const stripe = Stripe(STRIPE_API_KEY);

document.getElementById('buy-btn').addEventListener('click', async () => {
    const response = await fetch('/create_checkout_session/');
    const session = await response.json()

    if (session.id.startsWith("test_id")) {
        window.location.href = "/success/";
        return;
    }

    stripe.redirectToCheckout({ sessionId: session.id })
})