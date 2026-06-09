import React from "react";
import "@/styles/ComboBoxCliente.css";

interface ComboBoxClienteProps {
  clientes: string[];
  valor: string;
  onChange: (valor: string) => void;
  label?: string;
  disabled?: boolean;
}

export const ComboBoxCliente: React.FC<ComboBoxClienteProps> = ({
  clientes,
  valor,
  onChange,
  label = "IP / DOMÍNIO:",
  disabled = false,
}) => {
  return (
    <div>
      <label htmlFor="cliente-select" className="cliente-label">
        {label}
      </label>
      <select
        id="cliente-select"
        value={valor}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="cliente-select"
      >
        <option value="">-- TODOS --</option>
        {clientes.map((cliente) => (
          <option key={cliente} value={cliente}>
            {cliente}
          </option>
        ))}
      </select>
    </div>
  );
};
