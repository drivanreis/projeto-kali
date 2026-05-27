import React from "react";
import "@/styles/ComboBoxAlvo.css";

interface ComboBoxAlvoProps {
  alvos: string[];
  valor: string;
  onChange: (valor: string) => void;
  label?: string;
  disabled?: boolean;
}

export const ComboBoxAlvo: React.FC<ComboBoxAlvoProps> = ({
  alvos,
  valor,
  onChange,
  label = "IP / DOMÍNIO:",
  disabled = false,
}) => {
  return (
    <div>
      <label htmlFor="alvo-select" className="alvo-label">
        {label}
      </label>
      <select
        id="alvo-select"
        value={valor}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="alvo-select"
      >
        <option value="">-- TODOS --</option>
        {alvos.map((alvo) => (
          <option key={alvo} value={alvo}>
            {alvo}
          </option>
        ))}
      </select>
    </div>
  );
};
