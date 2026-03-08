import React, { useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";

export default function ClusterGraph({ nodes = [], edges = [] }) {

  const fgRef = useRef();

  const links = edges.map(e => ({
    source: e.source,
    target: e.target,
    velocity: e.velocity || 0
  }));

  const graphData = {
    nodes,
    links
  };

  return (
    <div style={{ height: "600px", width: "100%" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}

        nodeLabel="label"

        nodeCanvasObject={(node, ctx, globalScale) => {

          const risk = node.risk_score || 0;
          const clusterSize = node.cluster_size || 1;

          // -------------------------
          // Risk coloring
          // -------------------------

          let color = "#4CAF50";

          if (risk > 0.8) color = "#ff0000";
          else if (risk > 0.5) color = "#ff9800";
          else if (risk > 0.2) color = "#ffc107";

          const size = 4 + clusterSize * 0.5;

          // -------------------------
          // FRAUD RING PULSE EFFECT
          // -------------------------

          if (risk > 0.8) {

            const pulse = (Date.now() / 300) % 10;

            ctx.beginPath();
            ctx.arc(node.x, node.y, size + pulse, 0, 2 * Math.PI);
            ctx.strokeStyle = "rgba(255,0,0,0.3)";
            ctx.lineWidth = 2;
            ctx.stroke();

          }

          // -------------------------
          // Draw Node
          // -------------------------

          ctx.beginPath();
          ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();

          // -------------------------
          // Node label
          // -------------------------

          const label = node.label;
          const fontSize = 10 / globalScale;

          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "#ffffff";
          ctx.fillText(label, node.x + size + 2, node.y + size + 2);
        }}

        linkColor={(link) => {

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