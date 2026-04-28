"""Gera PDFs dos artefatos de release do CTRVE seguindo o template visual do TJCE."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend", "venv", "lib",
    "python3.12", "site-packages"))

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT = BASE / "pdf"
OUTPUT.mkdir(exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# CSS BASE — compartilhado por todos os documentos
# ──────────────────────────────────────────────────────────────────────────────
BASE_CSS = CSS(string="""
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap');

    @page {
        size: A4;
        margin: 2cm 2cm 2.5cm 2cm;

        @top-left { content: ""; }
        @top-center { content: ""; }
        @top-right { content: ""; }

        @bottom-right {
            content: counter(page);
            font-family: Arial, sans-serif;
            font-size: 9pt;
            color: #444;
        }
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
        font-family: Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.5;
        color: #1a1a1a;
    }

    /* ── CABEÇALHO INSTITUCIONAL ─────────────────────────────────────── */
    .page-header {
        width: 100%;
        border: 1px solid #999;
        margin-bottom: 1.5cm;
        display: flex;
        align-items: stretch;
    }
    .page-header .logo-left {
        width: 3cm;
        min-height: 2.2cm;
        border-right: 1px solid #999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px;
    }
    .page-header .logo-left .tjce-emblem {
        width: 50px;
        height: 50px;
        background: #003366;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20pt;
        font-weight: bold;
    }
    .page-header .center-text {
        flex: 1;
        text-align: center;
        padding: 8px 4px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .page-header .center-text p {
        font-size: 8pt;
        font-weight: bold;
        line-height: 1.6;
        color: #1a1a1a;
    }
    .page-header .logo-right {
        width: 3cm;
        border-left: 1px solid #999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px;
        font-size: 14pt;
        font-weight: bold;
        color: #003366;
    }

    /* ── CAPA ─────────────────────────────────────────────────────────── */
    .cover-title {
        text-align: center;
        margin-top: 3cm;
        margin-bottom: 2cm;
        font-size: 26pt;
        font-weight: bold;
        color: #1a1a1a;
    }
    .cover-subtitle {
        text-align: center;
        font-size: 13pt;
        color: #444;
        margin-bottom: 2cm;
    }
    .cover-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1cm;
    }
    .cover-table td {
        border: 1px solid #999;
        padding: 14px 16px;
        font-size: 10pt;
        vertical-align: middle;
    }
    .cover-table td:first-child {
        font-weight: bold;
        width: 35%;
        background: #f7f7f7;
    }

    /* ── TIPOGRAFIA ───────────────────────────────────────────────────── */
    h1 {
        font-size: 16pt;
        font-weight: bold;
        margin-top: 1.2cm;
        margin-bottom: 0.4cm;
        color: #003366;
        border-bottom: 2px solid #003366;
        padding-bottom: 4px;
    }
    h2 {
        font-size: 12pt;
        font-weight: bold;
        margin-top: 0.8cm;
        margin-bottom: 0.3cm;
        color: #1a1a1a;
    }
    h3 {
        font-size: 10pt;
        font-weight: bold;
        margin-top: 0.5cm;
        margin-bottom: 0.2cm;
        color: #1a1a1a;
    }

    p { margin-bottom: 0.3cm; }

    ul, ol {
        margin-left: 0.8cm;
        margin-bottom: 0.3cm;
    }
    li { margin-bottom: 2px; }

    code {
        font-family: "Courier New", monospace;
        font-size: 8.5pt;
        background: #f0f0f0;
        padding: 1px 4px;
        border-radius: 2px;
    }

    pre {
        background: #f4f4f4;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 10px 12px;
        margin-bottom: 0.4cm;
        font-family: "Courier New", monospace;
        font-size: 8pt;
        white-space: pre-wrap;
        word-break: break-all;
    }

    /* ── TABELAS ──────────────────────────────────────────────────────── */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 0.5cm;
        font-size: 9.5pt;
    }
    th {
        background: #003366;
        color: white;
        padding: 8px 10px;
        text-align: left;
        font-weight: bold;
        font-size: 9pt;
    }
    td {
        border: 1px solid #ccc;
        padding: 8px 10px;
        vertical-align: top;
    }
    tr:nth-child(even) td { background: #f7f9ff; }
    tr:first-child th { border-top: none; }

    /* ── QUEBRA DE PÁGINA ─────────────────────────────────────────────── */
    .page-break { page-break-after: always; }
    .avoid-break { page-break-inside: avoid; }

    /* ── ESTILO PML — SEÇÃO 5 (ATIVIDADE/RESPONSÁVEL) ────────────────── */
    .atividade-table td:first-child { width: 75%; }
    .atividade-table td:last-child  { width: 25%; font-weight: bold; }

    /* ── ESTILO MANUAL ────────────────────────────────────────────────── */
    .note {
        background: #fffbe6;
        border-left: 4px solid #f59e0b;
        padding: 8px 12px;
        margin-bottom: 0.4cm;
        border-radius: 2px;
        font-size: 9.5pt;
    }
    .tip {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 8px 12px;
        margin-bottom: 0.4cm;
        border-radius: 2px;
        font-size: 9.5pt;
    }
    .warn {
        background: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 8px 12px;
        margin-bottom: 0.4cm;
        border-radius: 2px;
        font-size: 9.5pt;
    }

    hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 0.6cm 0;
    }
""")

# ──────────────────────────────────────────────────────────────────────────────
# CABEÇALHO INSTITUCIONAL — aparece em todas as páginas
# ──────────────────────────────────────────────────────────────────────────────
HEADER = """
<div class="page-header avoid-break">
    <div class="logo-left">
        <div class="tjce-emblem">J</div>
    </div>
    <div class="center-text">
        <p>PODER JUDICIÁRIO<br>
           TRIBUNAL DE JUSTIÇA DO ESTADO DO CEARÁ<br>
           SECRETARIA DE TECNOLOGIA DA INFORMAÇÃO<br>
           DEPARTAMENTO DE INFORMÁTICA<br>
           DIVISÃO DE PRODUÇÃO</p>
    </div>
    <div class="logo-right">CTRVE</div>
</div>
"""

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def md_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )


def render_simple(title: str, md_content: str) -> str:
    body = md_to_html(md_content)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8">
<title>{title}</title>
</head><body>
{HEADER}
<h1>{title}</h1>
{body}
</body></html>"""


def generate_pdf(html: str, out_path: Path, css=BASE_CSS):
    HTML(string=html, base_url=str(BASE)).write_pdf(str(out_path), stylesheets=[css])
    kb = out_path.stat().st_size // 1024
    print(f"  ✓  {out_path.name}  ({kb} KB)")


# ──────────────────────────────────────────────────────────────────────────────
# 1. PML — template TJCE completo
# ──────────────────────────────────────────────────────────────────────────────
def build_pml_html() -> str:
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><title>PML — CTRVE v1.0.0</title>
</head><body>

{HEADER}

<div class="cover-title">Plano de Implantação</div>
<div class="cover-subtitle">CTRVE — Checklist de Transporte de Veículos</div>

<table class="cover-table">
  <tr><td>Sistema</td><td>CTRVE — Checklist de Transporte de Veículos</td></tr>
  <tr><td>Versão:</td><td>1.0.0</td></tr>
  <tr><td>Solicitante:</td><td>Rodrigo Barbosa</td></tr>
  <tr><td>Data da Solicitação:</td><td>28/04/2026</td></tr>
</table>

<div class="page-break"></div>
{HEADER}

<h1>1. Controle de Versões</h1>
<table>
  <tr><th>Data</th><th>Versão</th><th>Descrição</th><th>Autor</th></tr>
  <tr><td>28/04/2026</td><td>01</td><td>Criação do documento</td><td>Rodrigo Barbosa</td></tr>
</table>

<h1>2. Autorizadores</h1>
<table>
  <tr><th>Grupo</th><th style="width:80px;text-align:center">Marcado</th></tr>
  <tr><td>Sistemas Administrativos</td><td style="text-align:center;font-weight:bold">X</td></tr>
  <tr><td>Sistemas Judiciais de 1º Grau</td><td></td></tr>
  <tr><td>Sistemas Judiciais de 2º Grau</td><td></td></tr>
  <tr><td>Portais Intranet / Internet</td><td></td></tr>
  <tr><td>Infraestrutura</td><td style="text-align:center;font-weight:bold">X</td></tr>
</table>

<h1>3. Hardware e softwares básicos necessários</h1>
<ul>
  <li>Servidor Linux com Python 3.12+</li>
  <li>PostgreSQL 14+ acessível pelo servidor de aplicação</li>
  <li>Nginx configurado como proxy reverso</li>
  <li>Certificado SSL para o domínio de produção (obrigatório para cookies <code>secure</code>)</li>
  <li>WeasyPrint e dependências de sistema: <code>libpango</code>, <code>libcairo</code>, <code>libgdk-pixbuf</code></li>
  <li>Node.js 22+ — necessário apenas para build do frontend</li>
</ul>

<div class="page-break"></div>
{HEADER}

<h1>4. Servidores Afetados</h1>
<table>
  <tr><th>Nome do Serviço / Sistema</th><th>IC Relacionado</th><th>Impacto Previsto</th></tr>
  <tr>
    <td>CTRVE — Backend (FastAPI)</td>
    <td>Novo serviço</td>
    <td>Nenhum impacto em sistemas existentes. Implantação inicial.</td>
  </tr>
  <tr>
    <td>CTRVE — Frontend (React)</td>
    <td>Novo serviço</td>
    <td>Nenhum impacto em sistemas existentes.</td>
  </tr>
  <tr>
    <td>PostgreSQL</td>
    <td>Banco compartilhado ou dedicado</td>
    <td>Criação do banco <code>ctrve</code>. Sem impacto nos demais bancos.</td>
  </tr>
</table>

<h1>5. Detalhamento da Implantação</h1>
<table class="atividade-table">
  <tr><th>ATIVIDADE</th><th>RESPONSÁVEL</th></tr>
  <tr>
    <td>
      <strong>Pré-requisitos</strong><br>
      <ul>
        <li>Provisionar banco de dados PostgreSQL chamado <code>ctrve</code> com usuário dedicado</li>
        <li>Configurar DNS para o domínio de produção (ex.: <code>ctrve.tjce.jus.br</code>)</li>
        <li>Emitir e instalar certificado SSL para o domínio</li>
        <li>Configurar proxy reverso Nginx: <code>/api</code> → backend (porta 8000), <code>/</code> → frontend estático</li>
        <li>Instalar dependências do WeasyPrint: <code>libpango</code>, <code>libcairo</code>, <code>libgdk-pixbuf</code></li>
        <li>Configurar variáveis de ambiente de produção (ver Seção 6)</li>
      </ul>
    </td>
    <td>Infraestrutura</td>
  </tr>
  <tr>
    <td>
      <strong>Passo 1 — Deploy do Backend</strong><br>
      <ul>
        <li>Clonar repositório na tag <code>v1.0.0</code> (commit <code>01e3017</code>)</li>
        <li>Instalar dependências: <code>pip install -r backend/requirements.txt</code></li>
        <li>Inicializar banco: <code>python -c "from app.database import create_db_and_tables; create_db_and_tables()"</code></li>
        <li>Iniciar servidor: <code>uvicorn app.main:app --host 0.0.0.0 --port 8000</code></li>
        <li>Verificar saúde: <code>curl https://ctrve.tjce.jus.br/api/health</code></li>
      </ul>
    </td>
    <td>Aplicação</td>
  </tr>
  <tr>
    <td>
      <strong>Passo 2 — Deploy do Frontend</strong><br>
      <ul>
        <li>Executar build: <code>cd frontend &amp;&amp; npm ci &amp;&amp; npm run build</code></li>
        <li>Copiar <code>frontend/dist/</code> para o diretório raiz do Nginx</li>
        <li>Verificar acesso à URL principal no navegador</li>
      </ul>
    </td>
    <td>Aplicação</td>
  </tr>
  <tr>
    <td>
      <strong>Passo 3 — Validação Pós-Implantação</strong><br>
      <ul>
        <li>Criar usuário Responsável inicial via <code>POST /api/v1/users</code></li>
        <li>Realizar login e verificar acesso ao dashboard</li>
        <li>Criar checklist de teste, salvar entrega e realizar devolução</li>
        <li>Gerar PDF do checklist e verificar conteúdo</li>
        <li>Verificar logs — sem erros críticos nas primeiras 30 minutos</li>
      </ul>
    </td>
    <td>Aplicação / Negócio</td>
  </tr>
</table>

<div class="page-break"></div>
{HEADER}

<h1>6. Detalhamento da configuração dos recursos adicionais</h1>
<p>Variáveis de ambiente obrigatórias no servidor de produção:</p>
<table>
  <tr><th>Variável</th><th>Descrição</th><th>Ação</th></tr>
  <tr><td><code>SECRET_KEY</code></td><td>Chave de assinatura JWT</td><td>Gerar com <code>openssl rand -hex 32</code>. Nunca usar o valor padrão.</td></tr>
  <tr><td><code>DATABASE_URL</code></td><td>String de conexão PostgreSQL</td><td><code>postgresql+psycopg2://usuario:senha@host:5432/ctrve</code></td></tr>
  <tr><td><code>CORS_ORIGINS</code></td><td>Origens CORS permitidas</td><td><code>["https://ctrve.tjce.jus.br"]</code></td></tr>
  <tr><td><code>DEBUG</code></td><td>Modo debug</td><td>Definir como <code>false</code> em produção</td></tr>
  <tr><td><code>ACCESS_TOKEN_EXPIRE_MINUTES</code></td><td>Expiração do access token</td><td>Padrão: <code>30</code></td></tr>
  <tr><td><code>REFRESH_TOKEN_EXPIRE_DAYS</code></td><td>Expiração do refresh token</td><td>Padrão: <code>7</code></td></tr>
</table>

<h1>7. Dependências</h1>
<p>O sistema CTRVE não possui integrações com sistemas externos do TJCE nesta versão (sem integração com SEI, LDAP/AD ou sistema de frota). Operação independente.</p>

<h1>8. Backup</h1>
<h2>8.1 Itens para backup</h2>
<ul><li>Banco de dados <code>ctrve</code> (PostgreSQL)</li></ul>

<h2>8.2 Periodicidade</h2>
<ul>
  <li><strong>Backup completo:</strong> 1x por semana (fins de semana ou horário de menor uso)</li>
  <li><strong>Backup incremental/diferencial:</strong> diário, à noite, registrando mudanças desde o último backup</li>
</ul>

<h2>8.3 Retenção</h2>
<ul>
  <li><strong>Incrementais:</strong> 15 dias</li>
  <li><strong>Semanais (completos):</strong> 4 a 6 semanas</li>
</ul>

<h1>9. Monitoramento</h1>
<p>Logs da aplicação via saída padrão do processo uvicorn. Sem ferramenta de APM configurada nesta versão inicial. Recomenda-se integração futura com a solução de observabilidade adotada pela STI/TJCE.</p>

<h1>10. Contatos para Suporte</h1>
<table>
  <tr><th>NOME</th><th>FUNÇÃO</th></tr>
  <tr>
    <td>Rodrigo Barbosa</td>
    <td>Responsável pelo desenvolvimento — suporte a erros de aplicação</td>
  </tr>
  <tr>
    <td>Equipe de Infraestrutura TJCE</td>
    <td>Responsável pelo ambiente, rede e configuração do servidor</td>
  </tr>
  <tr>
    <td>Gestor da Demanda</td>
    <td>Ficar ciente da execução e resultado da implantação</td>
  </tr>
</table>

</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# 2. CHANGELOG
# ──────────────────────────────────────────────────────────────────────────────
def build_changelog_html() -> str:
    content = (BASE / "CHANGELOG.md").read_text(encoding="utf-8")
    body = md_to_html(content)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><title>CHANGELOG — CTRVE v1.0.0</title>
</head><body>
{HEADER}
{body}
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# 3. DEPLOY CHECKLIST
# ──────────────────────────────────────────────────────────────────────────────
def build_deploy_html() -> str:
    content = (BASE / "deploy-checklist.md").read_text(encoding="utf-8")
    body = md_to_html(content)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><title>Deploy Checklist — CTRVE v1.0.0</title>
</head><body>
{HEADER}
{body}
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# 4. ROLLBACK PLAN
# ──────────────────────────────────────────────────────────────────────────────
def build_rollback_html() -> str:
    content = (BASE / "rollback-plan.md").read_text(encoding="utf-8")
    body = md_to_html(content)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><title>Rollback Plan — CTRVE v1.0.0</title>
</head><body>
{HEADER}
{body}
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# 5. APF (contagem detalhada + resumo num único PDF)
# ──────────────────────────────────────────────────────────────────────────────
def build_apf_html() -> str:
    resumo = (BASE / "apf" / "resumo-apf.md").read_text(encoding="utf-8")
    detalhe = (BASE / "apf" / "contagem-detalhada.md").read_text(encoding="utf-8")
    b_resumo = md_to_html(resumo)
    b_detalhe = md_to_html(detalhe)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><title>Contagem APF — CTRVE v1.0.0</title>
</head><body>
{HEADER}
{b_resumo}
<div class="page-break"></div>
{HEADER}
{b_detalhe}
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# 6. MANUAL DO USUÁRIO
# ──────────────────────────────────────────────────────────────────────────────
def build_manual_html() -> str:
    content = (BASE / "manual" / "manual-usuario.md").read_text(encoding="utf-8")
    body = md_to_html(content)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><title>Manual do Usuário — CTRVE v1.0.0</title>
</head><body>
{HEADER}
{body}
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nGerando PDFs em: {OUTPUT}\n")

    artifacts = [
        ("PML — Plano de Implantação",         build_pml_html(),      OUTPUT / "PML.pdf"),
        ("CHANGELOG",                           build_changelog_html(),OUTPUT / "CHANGELOG.pdf"),
        ("Deploy Checklist",                    build_deploy_html(),   OUTPUT / "deploy-checklist.pdf"),
        ("Rollback Plan",                       build_rollback_html(), OUTPUT / "rollback-plan.pdf"),
        ("Contagem APF",                        build_apf_html(),      OUTPUT / "apf.pdf"),
        ("Manual do Usuário",                   build_manual_html(),   OUTPUT / "manual-usuario.pdf"),
    ]

    for name, html, path in artifacts:
        print(f"  Gerando {name}...")
        try:
            generate_pdf(html, path)
        except Exception as e:
            print(f"  ✗  ERRO em {name}: {e}")

    print(f"\nConcluído. {len(artifacts)} PDFs gerados em {OUTPUT}/\n")
