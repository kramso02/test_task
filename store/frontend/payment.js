const stripe = Stripe(STRIPE_PUBLIC_KEY);

document.getElementById('buy-btn').addEventListener('click', async () => {
    const response = await fetch(`/buy/${ITEM_ID}/`);
    const session = await response.json()

    if (session.id.startsWith("test_id")) {
        window.location.href = "/success/";
        return;
    }

    stripe.redirectToCheckout({ sessionId: session.id })
})