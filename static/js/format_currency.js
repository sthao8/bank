let formatter = new Intl.NumberFormat("sv-SE", {style: "currency", currency: "SEK"});
function format_currency(amount) {
    return formatter.format(amount)
};