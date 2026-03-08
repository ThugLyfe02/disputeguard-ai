import React from "react";

export default function ClusterGraph({ nodes, edges }) {

  if (!nodes) return null;

  return (
    <div>
      <h3>Fraud Cluster</h3>

      <p>Nodes: {nodes.length}</p>
      <p>Edges: {edges.length}</p>

      <ul>
        {nodes.map((n, i) => (
          <li key={i}>{n.label}</li>
        ))}
      </ul>
    </div>
  );
}