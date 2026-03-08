import React, { useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";

export default function ClusterGraph({ nodes = [], edges = [] }) {

  const fgRef = useRef();

  // Convert edges to graph links
  const links = edges.map(e => ({
    source: e.source,
    target: e.target
  }));

  const graphData = {
    nodes: nodes,
    links: links
  };

  return (
    <div style={{ height: "600px", width: "100%" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}

        nodeLabel="label"

        nodeCanvasObject={(node, ctx, globalScale) => {

          const risk = node.risk_score || 0;

          // Stripe-style risk coloring
          let color = "#4CAF50";     // green (safe)

          if (risk > 0.8) color = "#ff0000";
          else if (risk > 0.5) color = "#ff9800";
          else if (risk > 0.2) color = "#ffc107";

          // Node size scales with cluster importance
          const size = 4 + (node.cluster_size || 1) * 0.5;

          ctx.beginPath();
          ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();

          // Node label
          const label = node.label;
          const fontSize = 10 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "#ffffff";
          ctx.fillText(label, node.x + size + 2, node.y + size + 2);
        }}

        linkColor={(link) => {

          // velocity signal
          const velocity = link.velocity || 0;

          if (velocity > 0.8) return "#ff0000";
          if (velocity > 0.5) return "#ff9800";
          return "#999";
        }}

        linkWidth={(link) => {
          const velocity = link.velocity || 0;
          return 1 + velocity * 4;
        }}

        linkDirectionalParticles={(link) => {
          const velocity = link.velocity || 0;
          return velocity > 0.6 ? 2 : 0;
        }}

        linkDirectionalParticleWidth={2}

        backgroundColor="#0b0f19"
      />
    </div>
  );
}