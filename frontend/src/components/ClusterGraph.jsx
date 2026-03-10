import React, { useRef, useState, useCallback } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { getFraudCluster } from "../api/fraudApi";

/*
ClusterGraph

Fraud network visualization used in the DisputeGuard dashboard.

Visual signals implemented:

• Node color = risk score
• Node size = cluster importance
• Edge color/width = velocity signal
• Pulse animation = high risk nodes
• Heatmap overlay = large fraud rings
• Investigation panel = click a node to inspect
• Fraud ring mode = toggle enhanced ring visualization
*/

// --------------------------------------------------
// Investigation Side Panel
// --------------------------------------------------

function InvestigationPanel({ data, onClose }) {

  if (!data) return null;

  const { node, cluster } = data;
  const risk = node.risk_score || 0;
  const clusterSize = node.cluster_size || 0;

  const riskLabel =
    risk > 0.8 ? "CRITICAL" :
    risk > 0.5 ? "HIGH" :
    risk > 0.2 ? "MEDIUM" : "LOW";

  const riskColor =
    risk > 0.8 ? "#ff0000" :
    risk > 0.5 ? "#ff9800" :
    risk > 0.2 ? "#ffc107" : "#4CAF50";

  return (
    <div style={{
      position: "absolute",
      top: 0,
      right: 0,
      width: "320px",
      height: "100%",
      background: "rgba(11, 15, 25, 0.95)",
      borderLeft: "1px solid #333",
      color: "#e0e0e0",
      padding: "16px",
      overflowY: "auto",
      fontFamily: "monospace",
      fontSize: "13px",
      zIndex: 10,
    }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <strong style={{ fontSize: "15px" }}>Investigation</strong>
        <button
          onClick={onClose}
          style={{
            background: "none", border: "1px solid #555", color: "#ccc",
            cursor: "pointer", padding: "4px 8px", borderRadius: "3px",
          }}
        >
          Close
        </button>
      </div>

      {/* Entity Info */}
      <div style={{ marginBottom: "12px" }}>
        <div style={{ color: "#888", marginBottom: "4px" }}>Entity</div>
        <div>{node.label || node.id}</div>
      </div>

      <div style={{ marginBottom: "12px" }}>
        <div style={{ color: "#888", marginBottom: "4px" }}>Type</div>
        <div>{node.type || inferType(node.id)}</div>
      </div>

      {/* Risk Score */}
      <div style={{ marginBottom: "12px" }}>
        <div style={{ color: "#888", marginBottom: "4px" }}>Risk Score</div>
        <div style={{ color: riskColor, fontWeight: "bold" }}>
          {risk.toFixed(3)} — {riskLabel}
        </div>
      </div>

      {/* Cluster Size */}
      <div style={{ marginBottom: "12px" }}>
        <div style={{ color: "#888", marginBottom: "4px" }}>Cluster Size</div>
        <div>{clusterSize}</div>
      </div>

      {/* Velocity */}
      {node.velocity_score != null && (
        <div style={{ marginBottom: "12px" }}>
          <div style={{ color: "#888", marginBottom: "4px" }}>Velocity</div>
          <div>{node.velocity_score}</div>
        </div>
      )}

      {/* Connected Entities */}
      {cluster && cluster.connections && (
        <div style={{ marginBottom: "12px" }}>
          <div style={{ color: "#888", marginBottom: "8px" }}>
            Connected Entities ({cluster.connections.length})
          </div>
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            {cluster.connections.map((conn, i) => (
              <div key={i} style={{
                padding: "4px 6px",
                marginBottom: "2px",
                background: "rgba(255,255,255,0.05)",
                borderRadius: "3px",
              }}>
                {conn}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cluster Risk (from API) */}
      {cluster && cluster.network_risk != null && (
        <div style={{ marginBottom: "12px" }}>
          <div style={{ color: "#888", marginBottom: "4px" }}>Network Risk</div>
          <div>{cluster.network_risk}</div>
        </div>
      )}
    </div>
  );
}

function inferType(id) {
  if (!id) return "unknown";
  if (id.startsWith("tx_")) return "transaction";
  if (id.startsWith("device_")) return "device";
  if (id.startsWith("merchant_")) return "merchant";
  if (id.startsWith("email_")) return "email";
  return "unknown";
}

// --------------------------------------------------
// Main Component
// --------------------------------------------------

export default function ClusterGraph({ nodes = [], edges = [] }) {

  const fgRef = useRef();

  const [fraudRingMode, setFraudRingMode] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);

  const graphData = {
    nodes,
    links: edges
  };

  // --------------------------------------------------
  // Node Click → Investigation Panel
  // --------------------------------------------------

  const handleNodeClick = useCallback((node) => {

    setSelectedNode({ node, cluster: null });

    // Fetch full cluster data from API (non-blocking)
    const entityId = node.id;

    if (entityId) {
      getFraudCluster(entityId)
        .then((cluster) => {
          setSelectedNode((prev) =>
            prev && prev.node.id === entityId
              ? { ...prev, cluster }
              : prev
          );
        })
        .catch(() => {
          // API call failed — panel still shows node-level data
        });
    }
  }, []);

  return (
    <div style={{ height: "650px", width: "100%", position: "relative" }}>

      {/* Fraud Ring Mode Toggle */}
      <div style={{
        position: "absolute",
        top: "10px",
        left: "10px",
        zIndex: 5,
      }}>
        <button
          onClick={() => setFraudRingMode((m) => !m)}
          style={{
            background: fraudRingMode ? "#d32f2f" : "#333",
            color: "#fff",
            border: "1px solid #555",
            padding: "6px 12px",
            borderRadius: "4px",
            cursor: "pointer",
            fontFamily: "monospace",
            fontSize: "12px",
          }}
        >
          {fraudRingMode ? "Ring Mode ON" : "Ring Mode OFF"}
        </button>
      </div>

      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}

        nodeLabel={node => `${node.label || node.id}`}

        onNodeClick={handleNodeClick}

        nodeCanvasObject={(node, ctx, globalScale) => {

          const risk = node.risk_score || 0;
          const clusterSize = node.cluster_size || 1;

          // -----------------------------
          // Risk Color Mapping
          // -----------------------------

          let color = "#4CAF50"; // safe

          if (fraudRingMode) {

            // Gradient: green → yellow → orange → red
            if (risk > 0.8) color = "#ff0000";
            else if (risk > 0.6) color = "#ff5722";
            else if (risk > 0.4) color = "#ff9800";
            else if (risk > 0.2) color = "#ffc107";

          } else {

            if (risk > 0.8) color = "#ff0000";
            else if (risk > 0.5) color = "#ff9800";
            else if (risk > 0.2) color = "#ffc107";
          }

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
          // FRAUD RING PULSE (enhanced in ring mode)
          // -----------------------------

          const isRingNode = fraudRingMode && risk > 0.6 && clusterSize >= 3;

          if (risk > 0.8 || isRingNode) {

            const pulse = (Date.now() / 300) % 10;

            ctx.beginPath();
            ctx.arc(node.x, node.y, size + pulse, 0, 2 * Math.PI);
            ctx.strokeStyle = isRingNode
              ? "rgba(255, 50, 50, 0.6)"
              : "rgba(255,0,0,0.35)";
            ctx.lineWidth = isRingNode ? 3 : 2;
            ctx.stroke();
          }

          // -----------------------------
          // Selected Node Highlight
          // -----------------------------

          if (selectedNode && selectedNode.node.id === node.id) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI);
            ctx.strokeStyle = "#00bcd4";
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

          // -----------------------------
          // Cluster Density Tooltip (ring mode)
          // -----------------------------

          if (fraudRingMode && node.cluster_density != null) {
            const densityLabel = `d:${node.cluster_density.toFixed(2)}`;
            ctx.fillStyle = "#aaa";
            ctx.font = `${9 / globalScale}px Sans-Serif`;
            ctx.fillText(densityLabel, node.x + size + 2, node.y + size + 2 + fontSize);
          }
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

      {/* Investigation Side Panel */}
      {selectedNode && (
        <InvestigationPanel
          data={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}
