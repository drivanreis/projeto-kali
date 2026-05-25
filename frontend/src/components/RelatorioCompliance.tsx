import React from 'react'
import { Vulnerabilidade, RelatorioItem } from '@/types'

interface RelatorioComplianceProps {
  vulnerabilidades: Vulnerabilidade[]
  onFechar: () => void
}

const traduzirVulnerabilidade = (vuln: Vulnerabilidade): RelatorioItem => {
  const traducoes: Record<string, RelatorioItem> = {
    'Injeção SQL': {
      vulnerabilidade: vuln,
      impactoFinanceiro:
        'Acesso não autorizado a banco de dados com vazamento de dados de clientes, resultando em multas LGPD (até 2% do faturamento anual), perda de confiança e custo de notificação aos afetados.',
      gravidadeExecutiva: 'RISCO CRÍTICO PARA CONTINUIDADE DO NEGÓCIO',
      planoMitigacao:
        'Implementar validação de entrada, usar prepared statements, atualizar frameworks web, realizar testes de penetração trimestrais.',
      custoEstimado: 'Alto',
    },
    'Cross-Site Scripting (XSS)': {
      vulnerabilidade: vuln,
      impactoFinanceiro:
        'Furto de sessões de usuários, redirecionamento para phishing, malware distribuído via plataforma. Custo de remediação + perda de reputação.',
      gravidadeExecutiva: 'RISCO ALTO PARA A MARCA',
      planoMitigacao:
        'Sanitizar todas as entradas do usuário, implementar CSP headers, atualizar dependências front-end, realizar code reviews de segurança.',
      custoEstimado: 'Médio',
    },
    'Autenticação Fraca': {
      vulnerabilidade: vuln,
      impactoFinanceiro:
        'Comprometimento de contas de usuários administrativos, acesso indevido a dados sensíveis, fraude interna e externa.',
      gravidadeExecutiva: 'RISCO CRÍTICO PARA COMPLIANCE',
      planoMitigacao:
        'Implementar MFA em todos os acessos, usar JWT/OAuth2, implementar rate limiting, logs de auditoria contínuos.',
      custoEstimado: 'Médio',
    },
    'Certificado SSL Inválido': {
      vulnerabilidade: vuln,
      impactoFinanceiro:
        'Interceptação de comunicação, roubo de credenciais em trânsito, exposição a ataques man-in-the-middle.',
      gravidadeExecutiva: 'RISCO CRÍTICO PARA SEGURANÇA EM TRÂNSITO',
      planoMitigacao:
        'Renovar certificados SSL/TLS, implementar certificate pinning, monitorar validade com alertas automáticos.',
      custoEstimado: 'Baixo',
    },
    'Porta Aberta Desnecessária': {
      vulnerabilidade: vuln,
      impactoFinanceiro:
        'Superfície de ataque expandida, acesso potencial a serviços internos, descoberta de versões de software.',
      gravidadeExecutiva: 'RISCO MÉDIO PARA SUPERFÍCIE DE ATAQUE',
      planoMitigacao:
        'Auditar portas abertas, implementar firewall com whitelist, usar VPN para acesso administrativo.',
      custoEstimado: 'Baixo',
    },
    'Configuração Insegura': {
      vulnerabilidade: vuln,
      impactoFinanceiro:
        'Acesso indevido a funcionalidades administrativas, exposição de chaves API, vazamento de segredos de aplicação.',
      gravidadeExecutiva: 'RISCO ALTO PARA INTEGRIDADE DO SISTEMA',
      planoMitigacao:
        'Revisar configurações de segurança, usar gerenciador de segredos, implementar hardening de SO/aplicação.',
      custoEstimado: 'Médio',
    },
  }

  return (
    traducoes[vuln.titulo] || {
      vulnerabilidade: vuln,
      impactoFinanceiro:
        'Exposição de negócio a riscos operacionais, financeiros e legais não documentados.',
      gravidadeExecutiva: 'RISCO NÃO CATALOGADO - REVISAR IMEDIATAMENTE',
      planoMitigacao: 'Consultar especialista de segurança para avaliação de risco completa.',
      custoEstimado: 'Alto',
    }
  )
}

export const RelatorioCompliance: React.FC<RelatorioComplianceProps> = ({
  vulnerabilidades,
  onFechar,
}) => {
  const relatorios = vulnerabilidades.map(traduzirVulnerabilidade)
  const datahora = new Date().toLocaleString('pt-BR')

  const handleImprimir = (): void => {
    window.print()
  }

  const handleBaixarHTML = (): void => {
    const html = document.querySelector('.relatorio-compliance-container')
    if (!html) return

    const conteudo = html.innerHTML
    const blob = new Blob(
      [
        `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório de Compliance - KALI-CORE</title>
<style>
body { font-family: 'Courier New', monospace; color: #333; margin: 40px; }
.header { border-bottom: 3px solid #000; padding-bottom: 20px; margin-bottom: 30px; }
.header h1 { margin: 0; font-size: 24px; }
.header p { margin: 5px 0; font-size: 12px; color: #666; }
.vulnerability { page-break-inside: avoid; border: 2px solid #000; padding: 20px; margin-bottom: 20px; }
.vulnerability h3 { margin-top: 0; color: #c00; }
.pillar { margin: 15px 0; }
.pillar-title { font-weight: bold; color: #000; text-transform: uppercase; }
.pillar-content { margin-left: 20px; color: #333; }
.critical { color: #c00; }
.high { color: #f80; }
.medium { color: #f0f; }
.low { color: #0a0; }
.footer { margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; font-size: 11px; color: #999; }
@media print { body { margin: 0; } .no-print { display: none; } }
</style>
</head>
<body>
${conteudo}
<div class="footer">
<p>Relatório gerado por KALI-CORE V3.0 | Sistema de Auditoria e Compliance</p>
</div>
</body>
</html>`,
      ],
      { type: 'text/html' }
    )

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `relatorio-compliance-${new Date().getTime()}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fixed inset-0 bg-white z-40 overflow-auto">
      <div className="relatorio-compliance-container p-12 max-w-4xl mx-auto">
        {/* Header */}
        <div className="border-b-2 border-black pb-6 mb-8">
          <h1 className="text-3xl font-bold mb-2 font-mono">
            RELATÓRIO DE VULNERABILIDADES E COMPLIANCE
          </h1>
          <h2 className="text-lg text-gray-600 font-mono mb-4">
            Sistema KALI-CORE V3.0
          </h2>
          <div className="text-sm text-gray-500 space-y-1 font-mono">
            <p>
              <strong>Data/Hora:</strong> {datahora}
            </p>
            <p>
              <strong>Total de Vulnerabilidades Analisadas:</strong>{' '}
              {vulnerabilidades.length}
            </p>
          </div>
        </div>

        {/* Vulnerabilidades */}
        <div className="space-y-8">
          {relatorios.map((relatorio, idx) => {
            const criticidadeClass = {
              critica: 'critical',
              alta: 'high',
              media: 'medium',
              baixa: 'low',
            }[relatorio.vulnerabilidade.criticidade]

            return (
              <div key={relatorio.vulnerabilidade.id} className="border-2 border-black p-6">
                <h3
                  className={`text-xl font-bold mb-1 font-mono ${criticidadeClass}`}
                >
                  [{idx + 1}] {relatorio.vulnerabilidade.titulo}
                </h3>
                <p className="text-sm text-gray-600 font-mono mb-4">
                  Criticidade: {relatorio.vulnerabilidade.criticidade.toUpperCase()}
                </p>

                <div className="space-y-4 text-sm font-mono">
                  <div>
                    <div className="font-bold text-black mb-1">
                      💰 IMPACTO FINANCEIRO / RISCO DE NEGÓCIO
                    </div>
                    <div className="ml-4 text-gray-700">
                      {relatorio.impactoFinanceiro}
                    </div>
                  </div>

                  <div>
                    <div className="font-bold text-red-600 mb-1">
                      ⚠️ GRAVIDADE EXECUTIVA
                    </div>
                    <div className="ml-4 text-gray-700">
                      {relatorio.gravidadeExecutiva}
                    </div>
                  </div>

                  <div>
                    <div className="font-bold text-black mb-1">
                      🔧 PLANO DE MITIGAÇÃO
                    </div>
                    <div className="ml-4 text-gray-700">
                      {relatorio.planoMitigacao}
                    </div>
                  </div>

                  <div>
                    <div className="font-bold text-black mb-1">
                      💵 CUSTO ESTIMADO DE CORREÇÃO
                    </div>
                    <div className="ml-4 text-gray-700">
                      {relatorio.custoEstimado} (Em recursos de TI e horas de trabalho)
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Rodapé */}
        <div className="mt-12 pt-6 border-t-2 border-black">
          <p className="text-xs text-gray-500 font-mono">
            Este relatório é confidencial e deve ser compartilhado apenas com
            stakeholders autorizados. A implementação dos planos de mitigação é
            recomendada com urgência para manter a postura de segurança adequada.
          </p>
        </div>
      </div>

      {/* Toolbar flutuante */}
      <div className="no-print fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4 flex gap-4 justify-center border-t border-gray-700">
        <button
          onClick={handleImprimir}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-mono text-sm"
        >
          [ IMPRIMIR ]
        </button>
        <button
          onClick={handleBaixarHTML}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded font-mono text-sm"
        >
          [ BAIXAR HTML ]
        </button>
        <button
          onClick={onFechar}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded font-mono text-sm"
        >
          [ FECHAR ]
        </button>
      </div>
    </div>
  )
}
