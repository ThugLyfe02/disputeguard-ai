import React, { useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";

/*
ClusterGraph

Fraud network visualization used in the DisputeGuard dashboard.

Visual signals implemented:

• Node color = risk score
• Node size = cluster importance
• Edge color/width = velocity signal
• Pulse animation = high risk nodes
• Heatmap overlay = large fraud rings
*/

export default function ClusterGraph({ nodes = [], edges = [] }) {

  const fgRef = useRef();

  const graphData = {
    nodes,
    links: edges
  };

  return (
    <div style={{ height: "650px", width: "100%" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}

        nodeLabel={node => `${node.label || node.id}`}

        nodeCanvasObject={(node, ctx, globalScale) => {

          const risk = node.risk_score || 0;
          const clusterSize = node.cluster_size || 1;

          // -----------------------------
          // Risk Color Mapping
          // -----------------------------

          let color = "#4CAF50"; // safe

          if (risk > 0.8) color = "#ff0000";
          else if (risk > 0.5) color = "#ff9800";
          else if (risk > 0.2) color = "#ffc107";

          const size = 4 + clusterSize * 0.6;

          // -----------------------------
          // FRAUD RING HEATMAP
          // -----------------------------

          if (clusterSize > 8) {

            const heatRadius = clusterSize * 6;

            const gradient = ctx.createRadialGradient(
              node.x,
              node.y,
              0,
              node.x,
              node.y,
              heatRadius
            );

            gradient.addColorStop(0, "rgba(255,0,0,0.25)");
            gradient.addColorStop(1, "rgba(255,0,0,0)");

            ctx.beginPath();
            ctx.fillStyle = gradient;
            ctx.arc(node.x, node.y, heatRadius, 0, 2 * Math.PI);
            ctx.fill();
          }

          // -----------------------------
          // FRAUD RING PULSE
          // -----------------------------

          if (risk > 0.8) {

            const pulse = (Date.now() / 300) % 10;

            ctx.beginPath();
            ctx.arc(node.x, node.y, size + pulse, 0, 2 * Math.PI);
            ctx.strokeStyle = "rgba(255,0,0,0.35)";
            ctx.lineWidth = 2;
            ctx.stroke();
          }

          // -----------------------------
          // Draw Node
          // -----------------------------

          ctx.beginPath();
          ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();

          // -----------------------------
          // Node Label
          // -----------------------------

          const label = node.label || node.id;

          const fontSize = 11 / globalScale;

          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "#ffffff";

          ctx.fillText(
            label,
            node.x + size + 2,
            node.y + size + 2
          );
        }}

        // -----------------------------
        // Edge Velocity Visualization
        // -----------------------------

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

        // -----------------------------
        // Directional Particle Flow
        // -----------------------------

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