// ============================================================
// RecoverAI - Frontend Application
// ============================================================


// ============================================================
// HELPER FUNCTIONS
// ============================================================

function getElement(id) {
    return document.getElementById(id);
}


function setText(id, value) {
    const element = getElement(id);

    if (element) {
        element.textContent = value;
    }
}


function formatCurrency(value) {
    const number = Number(value) || 0;

    return "₹" + number.toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 2
        }
    );
}


function formatCurrencyShort(value) {
    const number = Number(value) || 0;

    if (number >= 10000000) {
        return "₹" + (number / 10000000).toFixed(2) + "Cr";
    }

    if (number >= 100000) {
        return "₹" + (number / 100000).toFixed(2) + "L";
    }

    if (number >= 1000) {
        return "₹" + (number / 1000).toFixed(1) + "K";
    }

    return formatCurrency(number);
}


function clampPercentage(value) {
    const number = Number(value) || 0;

    return Math.min(
        Math.max(number, 0),
        100
    );
}


// ============================================================
// LOAD DASHBOARD SUMMARY
// ============================================================

async function loadDashboardSummary() {

    try {

        const response = await fetch(
            "/dashboard-summary"
        );

        if (!response.ok) {
            throw new Error(
                "Dashboard summary request failed."
            );
        }

        const data = await response.json();


        // Revenue at Risk
        setText(
            "revenueRisk",
            formatCurrencyShort(
                data.revenue_at_risk
            )
        );


        // Potentially Recoverable
        setText(
            "recoverable",
            formatCurrencyShort(
                data.potentially_recoverable
            )
        );


        // Revenue Recovered
        setText(
            "priority",
            formatCurrencyShort(
                data.recovered_value
            )
        );


        // Recovery Rate
        setText(
            "recoveryRate",
            (
                (Number(data.recovery_rate) || 0) * 100
            ).toFixed(2) + "%"
        );


        // Failed Payments Subtitle
        const metricSub = document.querySelector(
            ".metrics .metric-card:nth-child(1) .metric-sub"
        );

        if (metricSub) {

            metricSub.textContent =
                (
                    Number(data.failed_payments) || 0
                ).toLocaleString("en-IN")
                + " failed payments";

        }


        console.log(
            "Dashboard summary loaded successfully:",
            data
        );

    } catch (error) {

        console.error(
            "Dashboard summary failed:",
            error
        );

    }

}


// ============================================================
// ANALYZE PAYMENT
// ============================================================

async function analyzePayment() {

    const button = document.querySelector(
        ".analyze-button"
    );

    const buttonText = button
        ? button.querySelector("span")
        : null;


    try {

        // Disable button

        if (button) {
            button.disabled = true;
        }


        if (buttonText) {
            buttonText.textContent = "Analyzing...";
        }


        // Get form elements

        const paymentIdElement =
            getElement("paymentId");

        const amountElement =
            getElement("amount");

        const paymentMethodElement =
            getElement("paymentMethod");

        const failureReasonElement =
            getElement("failureReason");

        const attemptNumberElement =
            getElement("attemptNumber");

        const successRateElement =
            getElement("successRate");


        // Validate form elements

        if (
            !paymentIdElement ||
            !amountElement ||
            !paymentMethodElement ||
            !failureReasonElement ||
            !attemptNumberElement ||
            !successRateElement
        ) {

            throw new Error(
                "Payment form elements could not be found."
            );

        }


        // Create payment object

        const payment = {

            payment_id:
                paymentIdElement.value.trim(),

            amount:
                Number(amountElement.value),

            payment_method:
                paymentMethodElement.value,

            failure_reason:
                failureReasonElement.value,

            attempt_number:
                Number(attemptNumberElement.value),

            customer_success_rate:
                Number(successRateElement.value) / 100

        };


        console.log(
            "Sending payment for analysis:",
            payment
        );


        // Validate payment

        if (!payment.payment_id) {

            throw new Error(
                "Please enter a Payment ID."
            );

        }


        if (
            !payment.amount ||
            payment.amount <= 0
        ) {

            throw new Error(
                "Please enter a valid payment amount."
            );

        }


        if (
            payment.customer_success_rate < 0 ||
            payment.customer_success_rate > 1
        ) {

            throw new Error(
                "Customer success rate must be between 0 and 100."
            );

        }


        // Send request

        const response = await fetch(
            "/analyze-payment",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(payment)

            }
        );


        // Read response

        let data;

        try {

            data = await response.json();

        } catch (jsonError) {

            throw new Error(
                "RecoverAI returned an invalid response."
            );

        }


        // Handle backend errors

        if (!response.ok) {

            const message =
                data?.detail ||
                data?.message ||
                "RecoverAI could not analyze this payment.";

            throw new Error(message);

        }


        // Validate response

        if (
            !data ||
            !data.decision
        ) {

            throw new Error(
                "Invalid response received from RecoverAI."
            );

        }


        // Display result

        displayDecision(data);
        loadDashboardSummary();
        loadRecoveryAnalytics();
        loadAuditTrail();

       // Refresh dashboard data after successful analysis
       loadDashboardSummary();
       loadRecoveryAnalytics();
       loadAuditTrail();


        console.log(
            "RecoverAI analysis successful:",
            data
        );


    } catch (error) {

        console.error(
            "Analyze payment error:",
            error
        );


        alert(
            error.message ||
            "Something went wrong while analyzing the payment."
        );


    } finally {

        // Restore button

        if (button) {
            button.disabled = false;
        }


        if (buttonText) {
            buttonText.textContent =
                "Analyze Payment";
        }

    }

}


// ============================================================
// DISPLAY AI DECISION
// ============================================================

function displayDecision(data) {

    const decision = data?.decision;


    if (!decision) {

        console.error(
            "No decision found in API response."
        );

        return;

    }


    // Recovery probability

    const probability =
        Number(decision.recovery_probability) || 0;


    setText(
        "probability",
        (probability * 100).toFixed(2) + "%"
    );


    // Recommended action

    setText(
        "recommendedAction",
        decision.recommended_action || "N/A"
    );


    // Expected recovery

    setText(
        "expectedRecovery",
        formatCurrency(
            decision.expected_recovery
        )
    );


    // Expected net recovery

    setText(
        "expectedNet",
        formatCurrency(
            decision.expected_net_recovery
        )
    );


    // Decision reason

    setText(
        "reason",
        decision.reason ||
        "No decision reason available."
    );


    // Decision status

    setText(
        "decisionStatus",
        decision.guardrail
            ? "GUARDRAIL"
            : "DECISION"
    );


    // Alternatives

    const alternatives =
        Array.isArray(decision.alternatives)
            ? decision.alternatives
            : [];


    const retry =
        alternatives.find(
            item => item.action === "RETRY"
        );


    const reminder =
        alternatives.find(
            item =>
                item.action === "SEND_REMINDER"
        );


    // RETRY

    if (retry) {

        const retryProbability =
            (Number(retry.probability) || 0) * 100;


        setText(
            "retryProbability",
            retryProbability.toFixed(2) + "%"
        );


        const retryBar =
            getElement("retryBar");


        if (retryBar) {

            retryBar.style.width =
                clampPercentage(
                    retryProbability
                ) + "%";

        }


        setText(
            "retryNet",
            formatCurrency(
                retry.expected_net
            )
        );

    }


    // SEND REMINDER

    if (reminder) {

        const reminderProbability =
            (Number(reminder.probability) || 0) * 100;


        setText(
            "reminderProbability",
            reminderProbability.toFixed(2) + "%"
        );


        const reminderBar =
            getElement("reminderBar");


        if (reminderBar) {

            reminderBar.style.width =
                clampPercentage(
                    reminderProbability
                ) + "%";

        }


        setText(
            "reminderNet",
            formatCurrency(
                reminder.expected_net
            )
        );

    }


    // Safe scroll

    const decisionPanel =
        getElement("decisionPanel");


    if (decisionPanel) {

        decisionPanel.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });

    }


    console.log(
        "Decision displayed successfully."
    );

}


// ============================================================
// RECOVERY ANALYTICS
// ============================================================

async function loadRecoveryAnalytics() {

    try {

        const response = await fetch(
            "/recovery-analytics"
        );


        if (!response.ok) {

            throw new Error(
                "Recovery analytics request failed."
            );

        }


        const data =
            await response.json();


        // ====================================================
        // SUMMARY
        // ====================================================

        setText(
            "overallRecovery",
            (
                (Number(data.overall_recovery_rate) || 0)
                * 100
            ).toFixed(2) + "%"
        );


        setText(
            "totalInterventions",
            (
                Number(data.total_interventions) || 0
            ).toLocaleString("en-IN")
        );


        setText(
            "totalSuccesses",
            (
                Number(data.total_successes) || 0
            ).toLocaleString("en-IN")
        );


        // ====================================================
        // ACTION PERFORMANCE
        // ====================================================

        const actionContainer =
            getElement("actionAnalytics");


        if (
            actionContainer &&
            Array.isArray(data.action_performance)
        ) {

            actionContainer.innerHTML = "";


            data.action_performance.forEach(
                item => {

                    const rateValue =
                        (
                            Number(item.recovery_rate) || 0
                        ) * 100;


                    const rate =
                        rateValue.toFixed(2);


                    const attempts =
                        (
                            Number(item.attempts) || 0
                        ).toLocaleString("en-IN");


                    const successes =
                        (
                            Number(item.successes) || 0
                        ).toLocaleString("en-IN");


                    const row =
                        document.createElement("div");


                    row.className =
                        "analytics-row";


                    // CORRECTED HTML
                    row.innerHTML = `
                        <div class="analytics-info">

                            <strong>
                                ${item.action || "Unknown"}
                            </strong>

                            <small>
                                ${attempts} attempts ·
                                ${successes} recoveries
                            </small>

                            <div class="analytics-progress">

                                <div
                                    class="analytics-progress-fill"
                                    style="width: ${clampPercentage(rateValue)}%">
                                </div>

                            </div>

                        </div>

                        <strong class="analytics-rate">
                            ${rate}%
                        </strong>
                    `;


                    actionContainer.appendChild(row);

                }
            );

        }


        // ====================================================
        // FAILURE PERFORMANCE
        // ====================================================

        const failureContainer =
            getElement("failureAnalytics");


        if (
            failureContainer &&
            Array.isArray(data.failure_performance)
        ) {

            failureContainer.innerHTML = "";


            data.failure_performance.forEach(
                item => {

                    const rateValue =
                        (
                            Number(item.recovery_rate) || 0
                        ) * 100;


                    const rate =
                        rateValue.toFixed(2);


                    const attempts =
                        (
                            Number(item.attempts) || 0
                        ).toLocaleString("en-IN");


                    const row =
                        document.createElement("div");


                    row.className =
                        "analytics-row";


                    row.innerHTML = `

                        <div class="analytics-info">

                            <strong>
                                ${item.failure_reason || "Unknown"}
                            </strong>

                            <small>
                                ${item.action || "Unknown"}
                                ·
                                ${attempts} attempts
                            </small>

                            <div class="analytics-progress">

                                <div
                                    class="analytics-progress-fill"
                                    style="width: ${clampPercentage(rateValue)}%">
                                </div>

                            </div>

                        </div>

                        <strong class="analytics-rate">
                            ${rate}%
                        </strong>

                    `;


                    failureContainer.appendChild(row);

                }
            );

        }


        console.log(
            "Recovery analytics loaded successfully:",
            data
        );


    } catch (error) {

        console.error(
            "Recovery analytics failed:",
            error
        );

    }

}


// ============================================================
// INITIALIZE APPLICATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "RecoverAI application initialized."
        );


        loadDashboardSummary();


        loadRecoveryAnalytics();

    }
);


// =====================================================
// AUDIT TRAIL
// =====================================================

async function loadAuditTrail() {
    const tableBody = document.getElementById("auditTableBody");
    const recordCount = document.getElementById("auditRecordCount");
    const emptyState = document.getElementById("auditEmptyState");

    // Stop safely if Audit Trail elements are not on the page
    if (!tableBody || !recordCount || !emptyState) {
        return;
    }

    try {
        // Show loading state
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="audit-loading">
                    Loading audit records...
                </td>
            </tr>
        `;

        emptyState.style.display = "none";

       const response = await fetch("/audit-trail");

        if (!response.ok) {
            throw new Error(
                `Audit API error: ${response.status}`
            );
        }

        const data = await response.json();

        const records = data.records || [];
        const totalRecords = data.total_records || 0;

        // Update record count
        recordCount.textContent =
            `${totalRecords} decision record${totalRecords === 1 ? "" : "s"}`;

        // Clear table
        tableBody.innerHTML = "";

        // Show empty state
        if (records.length === 0) {
            emptyState.style.display = "block";
            return;
        }

        // Hide empty state
        emptyState.style.display = "none";

        // Add records to table
        records.forEach((record) => {

            const row = document.createElement("tr");

            const timestamp = record.timestamp
                ? new Date(record.timestamp).toLocaleString()
                : "—";

            const paymentId =
                record.payment_id || "—";

            const amount =
                Number(record.amount || 0)
                    .toLocaleString("en-IN", {
                        style: "currency",
                        currency: "INR",
                        maximumFractionDigits: 2
                    });

            const failureReason =
                record.failure_reason || "—";

            // Support different backend structures safely
            const decision =
                record.decision || {};

            const action =
                decision.recommended_action ||
                record.recommended_action ||
                "—";

            const probability =
                decision.recovery_probability ??
                record.recovery_probability;

            const probabilityText =
                probability !== undefined &&
                probability !== null
                    ? `${(Number(probability) * 100).toFixed(2)}%`
                    : "—";

            row.innerHTML = `

                <td>
                    ${timestamp}
                </td>

                <td>
                    ${paymentId}
                </td>

                <td>
                    ${amount}
                </td>

                <td>
                    <span class="failure-badge">
                        ${failureReason}
                    </span>
                </td>

                <td>
                    <span class="action-badge ${action.toLowerCase().replace(/_/g, "-")}">
                        ${action.replace(/_/g, " ")}
                    </span>
                </td>

                <td>
                    ${probabilityText}
                </td>

            `;

            tableBody.appendChild(row);
        });

    } catch (error) {

        console.error(
            "Unable to load Audit Trail:",
            error
        );

        recordCount.textContent =
            "Unable to load records";

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="audit-loading">
                    Unable to load audit records.
                </td>
            </tr>
        `;
    }
}


// =====================================================
// AUDIT TRAIL REFRESH BUTTON
// =====================================================

const refreshAuditBtn =
    document.getElementById("refreshAuditBtn");

if (refreshAuditBtn) {

    refreshAuditBtn.addEventListener(
        "click",
        () => {
            loadAuditTrail();
        }
    );
}


// =====================================================
// LOAD AUDIT TRAIL WHEN PAGE STARTS
// =====================================================

loadAuditTrail();