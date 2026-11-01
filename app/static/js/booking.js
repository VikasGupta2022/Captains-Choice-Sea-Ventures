// Gateway Speedboat Interactive Booking Wizard Logic

document.addEventListener("DOMContentLoaded", () => {
    const bookingForm = document.getElementById("bookingForm");
    const dateInput = document.getElementById("bookingDate");
    const timeSlotSelect = document.getElementById("timeSlotSelect");
    const passengerCountInput = document.getElementById("passengerCount");
    const payBtn = document.getElementById("payBtn");
    const payBtnText = document.getElementById("payBtnText");

    // Live preview elements
    const summaryRouteName = document.getElementById("summaryRouteName");
    const summaryTripType = document.getElementById("summaryTripType");
    const summaryDateDisplay = document.getElementById("summaryDateDisplay");
    const summaryBoatImg = document.getElementById("summaryBoatImg");
    const summaryBoatName = document.getElementById("summaryBoatName");
    const summaryPax = document.getElementById("summaryPax");
    const summarySlot = document.getElementById("summarySlot");
    const summaryBaseFare = document.getElementById("summaryBaseFare");
    const summaryRoundTripRow = document.getElementById("summaryRoundTripRow");
    const summaryAddonsFare = document.getElementById("summaryAddonsFare");
    const summaryTotalFare = document.getElementById("summaryTotalFare");
    const summaryAdvanceFare = document.getElementById("summaryAdvanceFare");
    const summaryBalanceFare = document.getElementById("summaryBalanceFare");
    const contextWhatsAppBtn = document.getElementById("contextWhatsAppBtn");

    // Mock Modal Elements
    const mockPaymentModal = document.getElementById("mockPaymentModal");
    const modalBookingRef = document.getElementById("modalBookingRef");
    const modalAmount = document.getElementById("modalAmount");
    const modalOrderId = document.getElementById("modalOrderId");
    const modalConfirmSuccessBtn = document.getElementById("modalConfirmSuccessBtn");
    const modalCancelBtn = document.getElementById("modalCancelBtn");

    let currentOrderData = null;

    // Set default date to today
    if (dateInput) {
        const today = new Date().toISOString().split("T")[0];
        if (!dateInput.value) {
            dateInput.value = today;
        }
        dateInput.min = today;
    }

    // Helper: Collect current form selections
    function getFormSelections() {
        const routeRadio = document.querySelector('input[name="route_id"]:checked');
        const boatRadio = document.querySelector('input[name="boat_id"]:checked');
        const tripTypeRadio = document.querySelector('input[name="trip_type"]:checked');
        
        const addonCheckboxes = document.querySelectorAll('input[name="addons"]:checked');
        const addons = Array.from(addonCheckboxes).map(cb => cb.value);

        return {
            route_id: routeRadio ? routeRadio.value : "gateway-mandwa",
            boat_id: boatRadio ? boatRadio.value : "speedboat-yamaha-8",
            trip_type: tripTypeRadio ? tripTypeRadio.value : "one_way",
            travel_date: dateInput ? dateInput.value : "",
            time_slot: timeSlotSelect ? timeSlotSelect.value : "07:00 AM",
            passengers: parseInt(passengerCountInput ? passengerCountInput.value : "4", 10) || 4,
            addons: addons
        };
    }

    // Recalculate price and update live preview
    async function updateCalculations() {
        const data = getFormSelections();

        try {
            const resp = await fetch("/api/bookings/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    boat_id: data.boat_id,
                    route_id: data.route_id,
                    trip_type: data.trip_type,
                    passengers: data.passengers,
                    addons: data.addons
                })
            });

            if (!resp.ok) {
                console.error("Calculation failed", await resp.text());
                return;
            }

            const fare = await resp.json();

            // Update UI
            if (summaryRouteName) summaryRouteName.textContent = fare.route_name;
            if (summaryTripType) summaryTripType.textContent = fare.trip_type === "round_trip" ? "Round-Trip (10% Off)" : "One-Way Transfer";
            if (summaryDateDisplay) summaryDateDisplay.textContent = data.travel_date ? `${data.travel_date} (${data.time_slot})` : "Date Pending";
            if (summaryBoatName) summaryBoatName.textContent = fare.boat_name;
            if (summaryBoatImg && fare.boat_image) summaryBoatImg.src = fare.boat_image;
            if (summaryPax) summaryPax.textContent = `${data.passengers} Passengers`;
            if (summarySlot) summarySlot.textContent = `${data.time_slot} Slot`;

            if (summaryBaseFare) summaryBaseFare.textContent = `₹${fare.base_fare.toLocaleString("en-IN")}`;
            if (summaryAddonsFare) summaryAddonsFare.textContent = `₹${fare.addons_fare.toLocaleString("en-IN")}`;
            if (summaryTotalFare) summaryTotalFare.textContent = `₹${fare.total_fare.toLocaleString("en-IN")}`;
            if (summaryAdvanceFare) summaryAdvanceFare.textContent = `₹${fare.advance_required.toLocaleString("en-IN")}`;
            if (summaryBalanceFare) summaryBalanceFare.textContent = `₹${fare.balance_due.toLocaleString("en-IN")}`;

            if (summaryRoundTripRow) {
                if (fare.trip_type === "round_trip") {
                    summaryRoundTripRow.classList.remove("hidden");
                } else {
                    summaryRoundTripRow.classList.add("hidden");
                }
            }

            if (payBtnText) {
                payBtnText.textContent = `Pay Advance (₹${fare.advance_required.toLocaleString("en-IN")}) & Confirm`;
            }

            // Update context-aware WhatsApp link
            if (contextWhatsAppBtn) {
                const waMessage = `Hello Captain's Choice! 🚤\nI am planning a trip:\n• Boat: ${fare.boat_name}\n• Route: ${fare.route_name}\n• Date: ${data.travel_date} at ${data.time_slot}\n• Passengers: ${data.passengers}\n• Advance: ₹${fare.advance_required.toLocaleString("en-IN")}\nCould you please confirm the jetty schedule?`;
                contextWhatsAppBtn.href = `https://wa.me/917506920614?text=${encodeURIComponent(waMessage)}`;
            }

        } catch (err) {
            console.error("Error calculating fare", err);
        }
    }

    // Attach reactive listeners to all inputs
    const reactiveInputs = document.querySelectorAll('input[name="route_id"], input[name="boat_id"], input[name="trip_type"], input[name="addons"], #bookingDate, #timeSlotSelect, #passengerCount');
    reactiveInputs.forEach(el => {
        el.addEventListener("change", updateCalculations);
        el.addEventListener("input", updateCalculations);
    });

    // Initial calculation on page load
    updateCalculations();

    // FORM SUBMISSION & RAZORPAY / MOCK CHECKOUT
    if (bookingForm) {
        bookingForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const name = document.getElementById("custName")?.value.trim();
            const phone = document.getElementById("custPhone")?.value.trim();
            const email = document.getElementById("custEmail")?.value.trim();
            const specialRequests = document.querySelector('input[name="special_requests"]')?.value.trim();

            if (!name || !phone) {
                alert("Please fill in your Full Name and WhatsApp Contact Number.");
                return;
            }

            const selections = getFormSelections();

            // Disable button
            payBtn.disabled = true;
            payBtn.classList.add("opacity-75", "cursor-wait");
            payBtnText.textContent = "Initiating Secure Checkout...";

            try {
                // 1. Create booking in database & generate Razorpay order
                const createResp = await fetch("/api/bookings/create", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        customer_name: name,
                        customer_phone: phone,
                        customer_email: email,
                        boat_id: selections.boat_id,
                        route_id: selections.route_id,
                        trip_type: selections.trip_type,
                        travel_date: selections.travel_date,
                        time_slot: selections.time_slot,
                        passengers: selections.passengers,
                        addons: selections.addons,
                        special_requests: specialRequests
                    })
                });

                if (!createResp.ok) {
                    const err = await createResp.json();
                    alert(`Booking creation error: ${err.detail || "Unable to process booking."}`);
                    resetPayButton();
                    return;
                }

                const orderData = await createResp.json();
                currentOrderData = orderData;

                // 2. Check if Mock Mode or Real Razorpay
                if (orderData.is_mock) {
                    // Open Simulation Modal
                    if (modalBookingRef) modalBookingRef.textContent = orderData.booking_ref;
                    if (modalAmount) modalAmount.textContent = `₹${orderData.advance_required.toLocaleString("en-IN")}`;
                    if (modalOrderId) modalOrderId.textContent = orderData.razorpay_order_id;
                    if (mockPaymentModal) {
                        mockPaymentModal.classList.remove("hidden");
                        mockPaymentModal.classList.add("flex");
                    }
                } else {
                    // Real Razorpay standard checkout popup
                    const options = {
                        key: orderData.razorpay_key_id,
                        amount: orderData.advance_required * 100, // paise
                        currency: orderData.currency || "INR",
                        name: "Captain's Choice Sea Ventures",
                        description: `Speedboat Booking: ${orderData.boat_name}`,
                        image: "/static/images/logo.jpg",
                        order_id: orderData.razorpay_order_id,
                        prefill: {
                            name: orderData.customer_name,
                            contact: orderData.customer_phone,
                            email: orderData.customer_email || ""
                        },
                        notes: {
                            booking_ref: orderData.booking_ref
                        },
                        theme: {
                            color: "#0F2B48"
                        },
                        handler: async function (response) {
                            // Client signature verification
                            await verifyAndCompletePayment({
                                booking_ref: orderData.booking_ref,
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_signature: response.razorpay_signature
                            });
                        },
                        modal: {
                            ondismiss: function () {
                                resetPayButton();
                            }
                        }
                    };

                    const rzp = new Razorpay(options);
                    rzp.on("payment.failed", function (response) {
                        alert(`Payment Failed: ${response.error.description}`);
                        resetPayButton();
                    });
                    rzp.open();
                }

            } catch (error) {
                console.error("Booking submission error:", error);
                alert("Something went wrong processing your request. Please try again.");
                resetPayButton();
            }
        });
    }

    // Modal Simulation Confirmation Button
    if (modalConfirmSuccessBtn) {
        modalConfirmSuccessBtn.addEventListener("click", async () => {
            if (!currentOrderData) return;
            modalConfirmSuccessBtn.disabled = true;
            modalConfirmSuccessBtn.textContent = "Verifying with Server...";

            await verifyAndCompletePayment({
                booking_ref: currentOrderData.booking_ref,
                razorpay_order_id: currentOrderData.razorpay_order_id,
                razorpay_payment_id: `pay_sim_${Date.now()}`,
                razorpay_signature: "simulated_success_signature"
            });
        });
    }

    // Modal Cancel Button
    if (modalCancelBtn) {
        modalCancelBtn.addEventListener("click", () => {
            if (mockPaymentModal) {
                mockPaymentModal.classList.add("hidden");
                mockPaymentModal.classList.remove("flex");
            }
            resetPayButton();
        });
    }

    // Verify Payment and Redirect
    async function verifyAndCompletePayment(payload) {
        try {
            const verifyResp = await fetch("/api/payments/verify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!verifyResp.ok) {
                const err = await verifyResp.json();
                alert(`Payment verification failed: ${err.detail}`);
                resetPayButton();
                return;
            }

            const result = await verifyResp.json();
            // Redirect to Boarding Pass / Confirmation Page
            window.location.href = `/booking/${result.booking_ref}`;

        } catch (err) {
            console.error("Verification error:", err);
            alert("Payment verification error. Please check your network connection.");
            resetPayButton();
        }
    }

    function resetPayButton() {
        if (payBtn) {
            payBtn.disabled = false;
            payBtn.classList.remove("opacity-75", "cursor-wait");
            updateCalculations();
        }
    }
});
