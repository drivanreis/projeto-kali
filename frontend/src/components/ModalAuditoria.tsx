import React, { useState, useMemo } from 'react'
import { useApp } from '@/context/AppContext'
import { CardVulnerabilidade } from './CardVulnerabilidade'

interface ModalAuditoriaProps {
  isOpen: boolean
  onClose: () => void
  onGerarLaudo: (vulnIds: number[]) => void
}

export const ModalAuditoria: React.FC<ModalAuditoriaProps> = ({
  isOpen,
  onClose,
  onGerarLaudo,
}) => {
  const {
    vulnerabilidades,
    alvos,
    attackTypes,
    filtroAlvo,
    filtroAtaque,
    setFiltroAlvo,
    setFiltroAtaque,
    carregarFiltros,
  } = useApp()
  const [selecionadas, setSelecionadas] = useState<Set<number>>(new Set())

  const vulnerabilidadesFiltradas = useMemo(() => {
    return vulnerabilidades.filter((v) => {
      const matchAlvo = !filtroAlvo || v.alvo_ip === filtroAlvo
      const matchAtaque = !filtroAtaque || v.attack_type === filtroAtaque
      return matchAlvo && matchAtaque
    })
  }, [vulnerabilidades, filtroAlvo, filtroAtaque])

  const handleSelectVuln = (id: number): void => {
    setSelecionadas((prev) => {
      const novo = new Set(prev)
      if (novo.has(id)) {
        novo.delete(id)
      } else {
        novo.add(id)
      }
      return novo
    })
  }

  const handleGerarLaudo = (): void => {
    if (selecionadas.size === 0) {
      alert('Por favor, selecione pelo menos uma vulnerabilidade')
      return
    }
    onGerarLaudo(Array.from(selecionadas))
  }

  React.useEffect(() => {
    if (isOpen) {
      void carregarFiltros()
    }
  }, [isOpen, carregarFiltros])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-black border-2 border-green-500 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header fixo */}
        <div className="border-b border-green-500 p-4 bg-black flex-shrink-0">
          <div className="flex justify-between items-center mb-3">
            <div className="text-green-400 font-mono font-bold text-lg">
              [ AUDITORIA DE VULNERABILIDADES ]
            </div>
            <button
              onClick={onClose}
              className="text-green-400 hover:text-red-400 font-mono font-bold text-xl"
            >
              ✕
            </button>
          </div>

          {/* Filtros */}
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="text-green-400 font-mono text-xs block mb-1">
                IP / DOMÍNIO:
              </label>
              <select
                id="filtro-ip"
                value={filtroAlvo}
                onChange={(e) => setFiltroAlvo(e.target.value)}
                className="w-full bg-black border border-green-500 text-green-400 font-mono text-xs p-2 focus:outline-none"
              >
                <option value="">-- TODOS --</option>
                {alvos.map((alvo) => (
                  <option key={alvo} value={alvo}>
                    {alvo}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-green-400 font-mono text-xs block mb-1">
                TIPO DE ATAQUE:
              </label>
              <select
                id="filtro-ataque"
                value={filtroAtaque}
                onChange={(e) => setFiltroAtaque(e.target.value)}
                className="w-full bg-black border border-green-500 text-green-400 font-mono text-xs p-2 focus:outline-none"
              >
                <option value="">-- TODOS --</option>
                {attackTypes.map((tipo) => (
                  <option key={tipo} value={tipo}>
                    {tipo}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="text-gray-400 font-mono text-xs">
            Total: {vulnerabilidadesFiltradas.length} | Selecionadas:{' '}
            {selecionadas.size}
          </div>
        </div>

        {/* Lista de vulnerabilidades (scrollável) */}
        <div className="modal-list flex-1 overflow-y-auto p-4">
          {vulnerabilidadesFiltradas.length === 0 ? (
            <div className="text-gray-500 text-center font-mono text-xs py-8">
              Nenhuma vulnerabilidade encontrada com os filtros selecionados
            </div>
          ) : (
            vulnerabilidadesFiltradas.map((vuln) => (
              <CardVulnerabilidade
                key={vuln.id}
                vulnerabilidade={vuln}
                selecionada={selecionadas.has(vuln.id)}
                onSelect={handleSelectVuln}
              />
            ))
          )}
        </div>

        {/* Footer fixo */}
        <div className="border-t border-green-500 p-4 bg-black flex-shrink-0 flex gap-2">
          <button
            onClick={handleGerarLaudo}
            className="flex-1 bg-green-900 hover:bg-green-700 text-green-400 font-mono text-xs py-2 px-3 border border-green-500 transition-colors"
          >
            [ GERAR LAUDO ]
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-red-900 hover:bg-red-700 text-red-400 font-mono text-xs py-2 px-3 border border-red-500 transition-colors"
          >
            [ FECHAR ]
          </button>
        </div>
      </div>
    </div>
  )
}
