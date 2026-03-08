import React from "react";

export default function DeviceTable({ devices }) {

  if (!devices || devices.length === 0) {
    return <p>No device intelligence available</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Device</th>
          <th>Reuse Score</th>
          <th>Cluster Size</th>
        </tr>
      </thead>

      <tbody>
        {devices.map((d, i) => (
          <tr key={i}>
            <td>{d.device}</td>
            <td>{d.reuse_score}</td>
            <td>{d.cluster_size}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}