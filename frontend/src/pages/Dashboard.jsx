import React, { useState } from "react";

import RiskChart from "../components/RiskChart";
import DeviceTable from "../components/DeviceTable";
import ClusterGraph from "../components/ClusterGraph";

import { scoreTransaction, fetchFraudNetwork } from "../api/fraudApi";

export default function Dashboard() {

  const [fraudResult, setFraudResult] = useState(null);
  const [networkData, setNetworkData] = useState(null);

  const [transactionInput, setTransactionInput] = useState({
    id: "tx_demo_1",
    amount: 100,
    device_hash: "device_demo_123"
  });

  async function runFraudCheck() {

    try {

      const result = await scoreTransaction({
        transaction: {
          id: transactionInput.id,
          amount: transactionInput.amount
        },
        device_hash: transactionInput.device_hash
      });

      setFraudResult(result.fraud_analysis);

      const network = await fetchFraudNetwork(transactionInput.id);

      setNetworkData(network);

    } catch (err) {

      console.error("Fraud check failed", err);

    }
  }

  return (

    <div style={{ padding: 30 }}>

      <h1>DisputeGuard AI</h1>
      <h2>Fraud Intelligence Dashboard</h2>

      {/* ----------------------------- */}
      {/* Transaction Input */}
      {/* ----------------------------- */}

      <div style={{ marginBottom: 30 }}>

        <input
          placeholder="Transaction ID"
          value={transactionInput.id}
          onChange={(e) =>
            setTransactionInput({
              ...transactionInput,
              id: e.target.value
            })
          }
        />

        <input
          placeholder="Amount"
          type="number"
          value={transactionInput.amount}
          onChange={(e) =>
            setTransactionInput({
              ...transactionInput,
              amount: Number(e.target.value)
            })
          }
        />

        <input
          placeholder="Device Hash"
          value={transactionInput.device_hash}
          onChange={(e) =>
            setTransactionInput({
              ...transactionInput,
              device_hash: e.target.value
            })
          }
        />

        <button onClick={runFraudCheck}>
          Run Fraud Analysis
        </button>

      </div>

      {/* ----------------------------- */}
      {/* Risk Score Chart */}
      {/* ----------------------------- */}

      {fraudResult && (
        <div style={{ marginBottom: 40 }}>

          <h3>Fraud Risk Breakdown</h3>

          <RiskChart data={fraudResult.scores} />

        </div>
      )}

      {/* ----------------------------- */}
      {/* Device Intelligence */}
      {/* ----------------------------- */}

      {fraudResult && fraudResult.signals.device_risk && (

        <div style={{ marginBottom: 40 }}>

          <h3>Device Intelligence</h3>

          <DeviceTable
            devices={[
              {
                device: transactionInput.device_hash,
                reuse_score:
                  fraudResult.scores.device_risk_score,
                cluster_size:
                  fraudResult.signals.graph_cluster?.cluster_size || 0
              }
            ]}
          />

        </div>

      )}

      {/* ----------------------------- */}
      {/* Fraud Network Graph */}
      {/* ----------------------------- */}

      {networkData && (

        <div>

          <h3>Fraud Network</h3>

          <ClusterGraph
            nodes={networkData.nodes}
            edges={networkData.edges}
          />

        </div>

      )}

    </div>
  );
}