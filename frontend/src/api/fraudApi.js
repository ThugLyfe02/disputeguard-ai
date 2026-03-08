/*
fraudApi.js

Frontend client for the DisputeGuard AI fraud APIs.

All dashboard components call this file instead of calling
the backend directly.

Architecture

React UI
   ↓
fraudApi.js
   ↓
FastAPI Fraud APIs
*/

const API_BASE = "http://localhost:8000";   // change later for production
const API_KEY = "test_api_key";             // replace with real key later



// --------------------------------------------------
// Generic Request Helper
// --------------------------------------------------

async function apiRequest(endpoint, options = {}) {

    const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            ...(options.headers || {})
        },
        ...options
    });

    if (!response.ok) {

        const text = await response.text();

        throw new Error(
            `API error ${response.status}: ${text}`
        );
    }

    return response.json();
}



// --------------------------------------------------
// Fraud Risk Scoring
// --------------------------------------------------

export async function scoreTransaction(transaction, deviceHash) {

    return apiRequest("/fraud/score", {
        method: "POST",
        body: JSON.stringify({
            transaction: transaction,
            device_hash: deviceHash
        })
    });

}



// --------------------------------------------------
// Fraud Network Graph
// --------------------------------------------------

export async function getFraudNetwork() {

    return apiRequest("/fraud/network");

}



// --------------------------------------------------
// Fraud Cluster Investigation
// --------------------------------------------------

export async function getFraudCluster(entity) {

    return apiRequest(`/fraud/network/${entity}`);

}



// --------------------------------------------------
// Fraud Ring Detection
// --------------------------------------------------

export async function detectFraudRing(entity) {

    return apiRequest(`/fraud/network/ring/${entity}`);

}



// --------------------------------------------------
// Device Intelligence
// --------------------------------------------------

export async function getDeviceRisk(deviceHash) {

    return apiRequest(`/device-risk/${deviceHash}`);

}



// --------------------------------------------------
// Reputation Intelligence
// --------------------------------------------------

export async function getReputation(entityType, entityId) {

    return apiRequest(`/reputation/${entityType}/${entityId}`);

}



// --------------------------------------------------
// Dashboard Metrics
// --------------------------------------------------

export async function getFraudMetrics() {

    return apiRequest("/metrics");

}



// --------------------------------------------------
// Real-Time Fraud Event Feed
// --------------------------------------------------

export async function getRecentFraudEvents(limit = 20) {

    return apiRequest(`/events/recent?limit=${limit}`);

}



// --------------------------------------------------
// Graph Signal Cache (Stripe-style optimization)
// --------------------------------------------------

export async function getGraphSignals(node) {

    return apiRequest(`/fraud/graph-signals/${node}`);

}



// --------------------------------------------------
// Fraud Dashboard Summary
// --------------------------------------------------

export async function getDashboardOverview() {

    return apiRequest("/fraud/dashboard");

}