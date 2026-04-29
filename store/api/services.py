import stripe


def get_or_create_stripe_coupon(discount):
    if discount.stripe_coupon_id:
        return discount.stripe_coupon_id

    coupon = stripe.Coupon.create(
        percent_off=discount.percent,
        duration="once",
        name=discount.name,
    )

    discount.stripe_coupon_id = coupon.id
    discount.save()

    return coupon.id


def get_or_create_stripe_tax(tax):
    if tax.stripe_tax_id:
        return tax.stripe_tax_id

    tax_rate = stripe.TaxRate.create(
        display_name=tax.name,
        percentage=tax.percent,
        inclusive=False,
    )

    tax.stripe_tax_id = tax_rate.id
    tax.save()

    return tax_rate.id
