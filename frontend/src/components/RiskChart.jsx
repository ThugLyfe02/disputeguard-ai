import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function RiskChart({ data }) {

  if (!data) return null;

  const chartData = [
    { name: "Rule", score: data.rule_score },
    { name: "Device", score: data.device_risk_score },
    { name: "Cluster", score: data.cluster_risk_score },
    { name: "Network", score: data.network_risk_score },
    { name: "FraudNetwork", score: data.fraud_network_score },
    { name: "ML", score: data.chargeback_probability }
  ];

  return (
    <LineChart width={600} height={300} data={chartData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis domain={[0,1]} />
      <Tooltip />
      <Line type="monotone" dataKey="score" stroke="#ff4d4f" />
    </LineChart>
  );
}