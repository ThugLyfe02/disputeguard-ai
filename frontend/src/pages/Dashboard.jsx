import React, { useState } from "react";

import RiskChart from "../components/RiskChart";
import DeviceTable from "../components/DeviceTable";
import ClusterGraph from "../components/ClusterGraph";
import FraudFeed from "../components/FraudFeed";

import { scoreTransaction, getFraudNetwork } from "../api/fraudApi";


export default function Dashboard() {

  const [fraudData, setFraudData] = useState(null);
  const [networkData, setNetworkData] = useState(null);

  const [transactionInput, setTransactionInput] = useState({
    id: "tx_demo_1",
    amount: 120,
    device_hash: "device_demo_abc"
  });


  // --------------------------------------------------
  // Run Fraud Analysis
  // --------------------------------------------------

  async function runFraudCheck() {

    try {

      const result = await scoreTransaction({
        transaction: {
          id: transactionInput.id,
          amount: transactionInput.amount
        },
        device_hash: transactionInput.device_hash
      });

      setFraudData(result.fraud_analysis);

      // fetch network graph
      const network = await getFraudNetwork(transactionInput.id);

      setNetworkData(network);

    } catch (error) {

      console.error("Fraud analysis failed:", error);

    }

  }


  return (

    <div style={{ padding: 40 }}>

      <h1>DisputeGuard AI</h1>
      <h2>Fraud Intelligence Dashboard</h2>

      {/* ------------------------------------ */}
      {/* Transaction Input Panel */}
      {/* ------------------------------------ */}

      <div style={{ marginBottom: 40 }}>

        <h3>Test Fraud Analysis</h3>

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
          type="number"
          placeholder="Amount"
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

        <button
          style={{ marginLeft: 10 }}
          onClick={runFraudCheck}
        >
          Run Fraud Analysis
        </button>

      </div>


      {/* ------------------------------------ */}
      {/* Fraud Risk Chart */}
      {/* ------------------------------------ */}

      {fraudData && (

        <div style={{ marginBottom: 50 }}>

          <h3>Fraud Risk Breakdown</h3>

          <RiskChart scores={fraudData.scores} />

        </div>

      )}


      {/* ------------------------------------ */}
      {/* Device Intelligence */}
      {/* ------------------------------------ */}

      {fraudData && fraudData.signals && (

        <div style={{ marginBottom: 50 }}>

          <h3>Device Intelligence</h3>

          <DeviceTable
            devices={[
              {
                device: transactionInput.device_hash,
                reuse_score: fraudData.scores.device_risk_score,
                cluster_size:
                  fraudData.signals.graph_cluster?.cluster_size || 0
              }
            ]}
          />

        </div>

      )}


      {/* ------------------------------------ */}
      {/* Fraud Network Graph */}
      {/* ------------------------------------ */}

      {networkData && (

        <div style={{ marginBottom: 50 }}>

          <h3>Fraud Network</h3>

          <ClusterGraph
            nodes={networkData.nodes}
            edges={networkData.edges}
          />

        </div>

      )}


      {/* ------------------------------------ */}
      {/* Real-Time Fraud Feed */}
      {/* ------------------------------------ */}

      <div style={{ marginTop: 50 }}>

        <FraudFeed />

      </div>

    </div>

  );

}