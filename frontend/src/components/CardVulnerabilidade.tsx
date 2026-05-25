import React from 'react'
import { Vulnerabilidade, CRITICIDADE_LABELS, CRITICIDADE_CLASSES } from '@/types'

interface CardVulnerabilidadeProps {
  vulnerabilidade: Vulnerabilidade
  selecionada: boolean
  onSelect: (id: number) => void
}

export const CardVulnerabilidade: React.FC<CardVulnerabilidadeProps> = ({
  vulnerabilidade,
  selecionada,
  onSelect,
}) => {
  const criticidadeClass = CRITICIDADE_CLASSES[vulnerabilidade.criticidade]
  const criticidadeLabel = CRITICIDADE_LABELS[vulnerabilidade.criticidade]

  return (
    <div className="border border-green-500 p-3 mb-2 bg-black">
      <div className="flex items-start gap-2">
        <input
          type="checkbox"
          className="selecionar-item mt-1 w-4 h-4 cursor-pointer accent-green-500"
          data-id={vulnerabilidade.id}
          checked={selecionada}
          onChange={() => onSelect(vulnerabilidade.id)}
          aria-label={`Selecionar vulnerabilidade: ${vulnerabilidade.titulo}`}
        />
        <div className="flex-1">
          <div
            className={`${criticidadeClass} mb-1 font-mono text-sm font-bold text-green-400`}
          >
            [{criticidadeLabel}] {vulnerabilidade.titulo}
          </div>
          <div className="text-gray-400 text-xs mt-1 font-mono">
            {vulnerabilidade.descricao || 'Sem descrição'}
            <br />
            <strong className="text-green-400">Correção:</strong>{' '}
            {vulnerabilidade.correcao || 'Não documentada'}
          </div>
          <div className="text-gray-500 text-xs mt-2 font-mono">
            {vulnerabilidade.timestamp
              ? new Date(vulnerabilidade.timestamp).toLocaleString('pt-BR')
              : ''}
          </div>
        </div>
      </div>
    </div>
  )
}
