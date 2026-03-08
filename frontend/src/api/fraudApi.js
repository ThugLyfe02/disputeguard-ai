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
        throw new Error(`API error: ${response.status}`);
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
// Fraud Cluster
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
// Device Risk
// --------------------------------------------------

export async function getDeviceRisk(deviceHash) {

    return apiRequest(`/device-risk/${deviceHash}`);

}


// --------------------------------------------------
// Reputation
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