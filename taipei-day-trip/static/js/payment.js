/**
 * Booking payment page.
 * - Initialize TapPay SDK and set up card fields
 * - Validate card input and toggle submit button accordingly
 * - On submit: get prime, create order and process payment
 */


async function initTapPay() {

    const submitBtn = document.querySelector(".bookingConfirmBtn");
    submitBtn.setAttribute("disabled", true);
    

    try {
        // Get App ID and App key for setup
        let configResponse = await fetch("/api/tappay/config");

        let config = await configResponse.json();

        TPDirect.setupSDK(config.appId, config.appKey, "sandbox");

        // Style setup
        var fields = {
            number: {
                element: '#card-number',
                placeholder: '**** **** **** ****'
            },
            expirationDate: {
                element: '#card-expiration-date',
                placeholder: 'MM / YY'
            },
            ccv: {
                element: '#card-ccv',
                placeholder: 'ccv'
            }
        }

        TPDirect.card.setup({
            fields: fields,
            styles: {
                'input': {
                    "padding": "10px",
                    "border-radius": "5px",
                    "background-color": "#FFFFFF",
                    "color": "#000000",
                    "border": "1px solid #E8E8E8"
                },
                // Styling ccv field
                'input.ccv': {
                    'font-size': '14px'
                },
                // Styling expiration-date field
                'input.expiration-date': {
                    'font-size': '14px'
                },
                // Styling card-number field
                'input.card-number': {
                    'font-size': '14px'
                },
                ':focus': {
                    'color': 'black'
                },
                '.valid': {
                    'color': 'green'
                },
                '.invalid': {
                    'color': 'red'
                },
                '@media screen and (max-width: 400px)': {
                    'input': {
                        'color': 'orange'
                    }
                }
            },
            isMaskCreditCardNumber: true,
            maskCreditCardNumberRange: {
                beginIndex: 6,
                endIndex: 11
            }
        });


        // Status display for credit card input
        function setFormGroupStatus(tpFieldId, status) {
            const tpField = document.getElementById(tpFieldId);
            const group = tpField.closest(".formRow");
            group.classList.remove("is-error", "is-success");
            if (status === "error") {
                group.classList.add("is-error");
            }
            if (status === "success") {
                group.classList.add("is-success");
            }
        }


        // Listen for card input status updates
        TPDirect.card.onUpdate(function (update) {
            // update.canGetPrime === true
            // --> you can call TPDirect.card.getPrime()
            if (update.canGetPrime) {
                // Enable submit Button to get prime.
                submitBtn.removeAttribute("disabled");
            } else {
                // Disable submit Button to get prime.
                submitBtn.setAttribute("disabled", true);
            }
                                                    

            // Number field is invalid
            if (update.status.number === 2) {
                setFormGroupStatus("card-number", "error");
            } else if (update.status.number === 0) {
                setFormGroupStatus("card-number", "success");
            } else {
                setFormGroupStatus("card-number", "normal");
            }
            
            // Expiry field is invalid
            if (update.status.expiry === 2) {
                setFormGroupStatus("card-expiration-date", "error");
            } else if (update.status.expiry === 0) {
                setFormGroupStatus("card-expiration-date", "success");
            } else {
                setFormGroupStatus("card-expiration-date", "normal");
            }
            
            // CCV field is invalid
            if (update.status.ccv === 2) {
                setFormGroupStatus("card-ccv", "error");
            } else if (update.status.ccv === 0) {
                setFormGroupStatus("card-ccv", "success");
            } else {
                setFormGroupStatus("card-ccv", "normal");
            }
        });


        // Get Prime: Triggered when user clicks the submit button
        function onSubmit(event) {
            event.preventDefault()

            // Get status of TapPay Fields
            const tappayStatus = TPDirect.card.getTappayFieldsStatus()

            
            // Check if possible to get Prime
            if (tappayStatus.canGetPrime === false) {
                alert("Cannot get prime");
                return;
            }

            submitBtn.setAttribute("disabled", true);
            submitBtn.textContent = "處理中...";
            document.getElementById("loadingOverlay").style.display = "flex";


            // Get prime
            TPDirect.card.getPrime( async (result) => {
                if (result.status !== 0) {
                    alert("Get prime error " + result.msg);
                    resetSubmitBtn();
                    return;
                }
                // alert('Get prime successful, prime: ' + result.card.prime);

                const token = localStorage.getItem("token");

                let OrderResponse = await fetch("/api/orders", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json", 
                        "Authorization": "Bearer " + token 
                    },
                    body: JSON.stringify({
                        prime: result.card.prime,
                        name: document.getElementById("contactName").value,
                        email: document.getElementById("contactEmail").value,
                        phone: document.getElementById("contactNumber").value
                    })
                });

                let OrderResult = await OrderResponse.json();

                // Direct user to thankyou page
                if (OrderResult.data && OrderResult.data.number) {
                    window.location.replace("/thankyou?number=" + OrderResult.data.number);
                } else {
                    alert(OrderResult.message || "Payment failed. Please try again.");
                    resetSubmitBtn();
                }
            });
        }

        function resetSubmitBtn() {
            submitBtn.removeAttribute("disabled");
            submitBtn.textContent = "確認訂購並付款";
            document.getElementById("loadingOverlay").style.display = "none";
        }

        submitBtn.addEventListener("click", onSubmit);
    } catch (err) {
        console.error(" Initialize TapPay fails: ", err);
        alert("Payment failed. Please check your card.");
        resetSubmitBtn();
    }
}

document.addEventListener("DOMContentLoaded", initTapPay());