function myFunction() {
    var x = document.getElementById("myLinks");
    if (x.style.display === "flex") {
        x.style.display = "none";
    } else {
        x.style.display = "flex";
        x.style.flexDirection = "column";
        x.style.marginTop = "80px";
        x.style.backgroundColor = "rgba(237, 226, 226, 0.8)";
    }
}

const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

hamburger.addEventListener("click",()=>{
    hamburger.classList.toggle("active")
    navMenu.classList.toggle("active")
})

document.querySelectorAll(".nav-link").forEach(n => n.addEventListener("click",()=>{
    hamburger.classList.remove("active")
    navMenu.classList.remove("active")
}))

  function openStripeCheckout() {
    var amount = document.getElementById("amount-input").value;

    // Create a Stripe Checkout Session
    fetch("/create-checkout-session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        amount: amount * 100,
      }),
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (session) {
        var stripe = Stripe('{{public_key}}');
        stripe.redirectToCheckout({ sessionId: session.id })
          .then(function (result) {
            // Handle any errors during the redirect to checkout
            console.error(result.error.message);
          });
      })
      .catch(function (error) {
        console.error("Error:", error);
      });
  }
