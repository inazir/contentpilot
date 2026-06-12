import React from "react";

export default function Divider({ label }) {
  if (label) {
    return (
      <div className="divider divider--labeled">
        <span className="divider__label">{label}</span>
      </div>
    );
  }
  return <hr className="divider" />;
}
