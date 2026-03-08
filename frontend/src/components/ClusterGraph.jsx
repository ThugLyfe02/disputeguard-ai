import React from "react";
import ForceGraph2D from "react-force-graph-2d";

/*
ClusterGraph

Visualizes fraud network clusters using a force-directed graph.

Nodes:
  transactions
  devices
  merchants
  emails

Edges:
  relationships extracted from fraud graph

Data format expected:

{
  nodes: [{ id: "tx_1", type: "transaction" }],
  links: [{ source: "tx_1", target: "device_abc" }]
}
*/

export default function ClusterGraph({ nodes = [], edges = [] }) {

  const graphData = {
    nodes: nodes,
    links: edges
  };

  const nodeColor = node => {
    switch (node.type) {
      case "device":
        return "#ff4d4f";
      case "merchant":
        return "#1890ff";
      case "transaction":
        return "#52c41a";
      case "email":
        return "#faad14";
      default:
        return "#999";
    }
  };

  return (
    <div style={{ border: "1px solid #eee", padding: 10 }}>

      <h3>Fraud Network Graph</h3>

      <ForceGraph2D
        graphData={graphData}

        nodeLabel={node => `${node.id} (${node.type})`}

        nodeAutoColorBy="type"

        nodeCanvasObject={(node, ctx, globalScale) => {

          const label = node.id;
          const fontSize = 12 / globalScale;

          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = nodeColor(node);
          ctx.beginPath();

          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
          ctx.fill();

          ctx.fillStyle = "#333";
          ctx.fillText(label, node.x + 8, node.y + 3);
        }}

        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.002}

      />

    </div>
  );
}