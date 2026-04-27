# Story 5.2: Gerar e Compartilhar PDF

Status: done

## Story

Como Responsável ou Motorista,
quero gerar um PDF do checklist completo e compartilhá-lo,
para que o documento possa ser enviado ou arquivado fora do sistema.

## Acceptance Criteria

1. Endpoint `GET /api/v1/checklists/{id}/pdf` retorna arquivo PDF com `Content-Type: application/pdf`. Requer autenticação (ambos perfis).
2. PDF contém todas as seções: dados gerais, itens verificados com status, nível de combustível, mapa de avarias (se entrega), assinaturas (imagens renderizadas), observações.
3. Se checklist está devolvido (`status === "devolvido"`), PDF inclui ambas seções (entrega + devolução).
4. Geração bem-sucedida retorna 200 com header `Content-Disposition: attachment; filename="checklist-{id}.pdf"`.
5. Tentativa de gerar PDF de checklist não salvo (`is_locked === false`) retorna 400 com MSG-019.
6. Frontend exibe botão "Gerar PDF" somente quando checklist está salvo (`is_locked === true`).
7. Botões "Gerar PDF" e "Imprimir" ficam desabilitados enquanto checklist não foi salvo — tooltip com MSG-019.
8. Clique no botão baixa o PDF via blob response e exibe MSG-025: "PDF gerado com sucesso."
9. Erros do backend exibidos ao usuário.
10. Testes: endpoint retorna PDF válido, endpoint rejeita checklist não salvo, botão aparece/desaparece conforme estado, download funciona.

## Tasks / Subtasks

- [x] **T1 — Backend: dependências (AC: 1)**
  - [x] T1.1: Adicionar `weasyprint` e `jinja2` ao `backend/requirements.txt`
  - [x] T1.2: Verificar que `weasyprint` instala corretamente (requer `libcairo2`, `libpango-1.0-0`, `libgdk-pixbuf2.0-0` no sistema — instalar via `apt` se necessário)

- [x] **T2 — Backend: template HTML/CSS do PDF (AC: 2, 3)**
  - [x] T2.1: Criar diretório `backend/app/templates/pdf/`
  - [x] T2.2: Criar `backend/app/templates/pdf/checklist.html` — template Jinja2 com todas as seções
  - [x] T2.3: Criar `backend/app/templates/pdf/checklist.css` — estilos para impressão/PDF

- [x] **T3 — Backend: pdf_service.py (AC: 2, 3, 4)**
  - [x] T3.1: Criar `backend/app/services/pdf_service.py` com função `generate_checklist_pdf(checklist: Checklist) -> bytes`
  - [x] T3.2: Usar `jinja2.Environment(loader=FileSystemLoader(...))` para carregar template
  - [x] T3.3: Renderizar HTML com dados do checklist e converter com `weasyprint.HTML(string=html).write_pdf()`
  - [x] T3.4: Retornar bytes do PDF

- [x] **T4 — Backend: routes/pdf.py + registro (AC: 1, 4, 5)**
  - [x] T4.1: Criar `backend/app/api/routes/pdf.py` com rota `GET /checklists/{id}/pdf`
  - [x] T4.2: Guard: se `not checklist.is_locked`, raise `ChecklistError(400, "MSG-019", "As opções de compartilhamento e impressão estarão disponíveis após o salvamento do checklist.")`
  - [x] T4.3: Retornar `Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": ...})`
  - [x] T4.4: Registrar router em `backend/app/main.py`: `from app.api.routes import pdf` + `app.include_router(pdf.router, prefix="/api/v1")`

- [x] **T5 — Backend: testes (AC: 1, 4, 5, 10)**
  - [x] T5.1: `test_gerar_pdf_checklist_salvo_200`: GET pdf de `locked_checklist` → 200, `content-type: application/pdf`, body começa com `%PDF`
  - [x] T5.2: `test_gerar_pdf_checklist_nao_salvo_400`: GET pdf de checklist não locked → 400, detail "MSG-019"
  - [x] T5.3: `test_gerar_pdf_checklist_inexistente_404`: GET pdf com id inválido → 404
  - [x] T5.4: `test_gerar_pdf_sem_autenticacao_401`: GET pdf sem auth header → 401
  - [x] T5.5: `test_gerar_pdf_motorista_pode_acessar_200`: GET pdf com auth de motorista → 200 (ambos perfis têm acesso)

- [x] **T6 — Frontend: botão PDF + download (AC: 6, 7, 8, 9)**
  - [x] T6.1: Adicionar botão "Gerar PDF" em `ChecklistView.tsx` — visível quando `checklist.is_locked`
  - [x] T6.2: Botão disabled durante download com loading state
  - [x] T6.3: Handler `onDownloadPdf`: chamar `apiClient.get(`/v1/checklists/${id}/pdf`, { responseType: "blob" })`, criar blob URL, trigger download via `<a>` temporário
  - [x] T6.4: Exibir `window.alert("PDF gerado com sucesso.")` (MSG-025) após download
  - [x] T6.5: Exibir erro se request falhar (blob → text → JSON para extrair detail)

- [x] **T7 — Frontend: testes (AC: 6, 7, 10)**
  - [x] T7.1: Botão "Gerar PDF" visível quando checklist está locked
  - [x] T7.2: Botão "Gerar PDF" não visível quando checklist não está locked (preenchendo entrega)
  - [x] T7.3: Clique no botão chama endpoint correto com responseType blob
  - [x] T7.4: Erro do backend exibido ao usuário

### Review Findings

#### Decision Needed

- [x] [Review][Decision] Verificação de ownership no endpoint de PDF — **decisão: intencional**, recurso compartilhado entre perfis; sem controle IDOR por design nesta story.
- [x] [Review][Decision] AC6 vs AC7: botão oculto vs desabilitado — **decisão: AC6 correto**, botão oculto quando não salvo; AC7 era aspiracional e foi descartado.
- [x] [Review][Decision] Botão "Imprimir" ausente — **decisão: fora do escopo desta story**, intencionalmente omitido; implementar em story dedicada se necessário.

#### Patches

- [x] [Review][Patch] SSRF via campo de assinatura — validação de formato `data:image/...;base64` adicionada em `pdf.py` antes de `write_pdf()`. [backend/app/api/routes/pdf.py]
- [x] [Review][Patch] CSS HTML-escapado por `autoescape=True` — corrigido com `{{ css | safe }}`. [backend/app/templates/pdf/checklist.html]
- [x] [Review][Patch] Frontend exibe código MSG-019 — corrigido para `json.message || json.detail`. [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] Object URL e link DOM vazam — `link.remove()` e `revokeObjectURL` movidos para bloco `finally`. [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] CSS lido do disco a cada geração — movido para escopo de módulo (`_CSS_CONTENT`). [backend/app/services/pdf_service.py]
- [x] [Review][Patch] `test_gerar_pdf_motorista_pode_acessar_200` sem `Content-Disposition` — assert adicionado. [backend/tests/api/test_pdf.py]
- [x] [Review][Patch] Sem teste AC-3 — fixture `devolvido_locked` e `test_gerar_pdf_checklist_devolvido_200` adicionados. [backend/tests/api/test_pdf.py]
- [x] [Review][Patch] T7.3 sem `revokeObjectURL` — `expect(revokeObjectURL).toHaveBeenCalledWith("blob:mock-url")` adicionado. [frontend/src/features/checklist/__tests__/ChecklistView.test.tsx]

#### Deferred

- [x] [Review][Defer] Jinja2 3.1.2 CVE-2024-34064 (filtro xmlattr, não usado aqui) [backend/requirements.txt] — deferred, pre-existing
- [x] [Review][Defer] WeasyPrint deps de sistema (libcairo, libpango, etc.) não documentadas em Dockerfile/setup [backend/requirements.txt] — deferred, pre-existing
- [x] [Review][Defer] `window.alert` para MSG-025 — padrão pré-existente da spec de story 5.1 [frontend/src/features/checklist/ChecklistView.tsx] — deferred, pre-existing
- [x] [Review][Defer] `write_pdf()` síncrono bloqueia thread do FastAPI — WeasyPrint é CPU/I/O intensivo; usar `run_in_executor` em story de performance quando concorrência for necessária. [backend/app/services/pdf_service.py] — deferred
- [x] [Review][Defer] Endpoint sem `response_model`/`responses` no decorador — OpenAPI descreve resposta como JSON em vez de `application/pdf`. [backend/app/api/routes/pdf.py] — deferred
- [x] [Review][Defer] Datas no PDF em UTC sem indicação de fuso — `data_entrega.strftime` renderiza UTC; usuário BR vê horário -3h; parametrizar timezone quando localização for necessária. [backend/app/templates/pdf/checklist.html] — deferred
- [x] [Review][Defer] Padrão `item is mapping` espalhado pelo template — normalizar `itens`/`itens_devolucao`/`avarias` para dicts simples no serviço antes de passar ao Jinja2. [backend/app/services/pdf_service.py] — deferred

## Dev Notes

### O que já existe (NÃO criar de novo)

| Item | Localização | Status |
|------|-------------|--------|
| `get_checklist_by_id()` | `checklist_service.py:26-35` | Pronto — reutilizar para buscar dados |
| `ChecklistError` exception + handler | `checklist_service.py:12-23`, `main.py:68-73` | Pronto — reutilizar para erros |
| `get_current_user` dependency | `core/deps.py:15-35` | Pronto — usar para auth (ambos perfis) |
| `apiClient` com interceptor | `lib/apiClient.ts` | Pronto |
| `isAxiosError` export | `lib/apiClient.ts:17` | Pronto |
| `locked_checklist` fixture | `conftest.py:117-137` | Pronto — reutilizar nos testes |
| `auth_headers` / `motorista_headers` fixtures | `conftest.py:77-171` | Pronto |
| `Checklist` model com todos os campos | `models/checklist.py` | Pronto |
| `ChecklistResponse` schema | `schemas/checklist.py:116-142` | Pronto |
| `Button` component (shadcn) | `components/ui/button.tsx` | Pronto |
| `EntregaReadOnly` / `DevolucaoReadOnly` | `ChecklistView.tsx:25-145` | Pronto |
| `_VALID_SIGNATURE` / `_ITEM_NAMES` | `conftest.py:6-14` | Pronto — reutilizar nos testes |

### O que falta (escopo desta story)

1. **WeasyPrint + Jinja2** nas dependências Python
2. **Template HTML/CSS** para o PDF em `backend/app/templates/pdf/`
3. **`pdf_service.py`** com geração HTML→PDF
4. **`routes/pdf.py`** com endpoint GET + guard de is_locked
5. **Registro do router** em `main.py`
6. **Botão "Gerar PDF"** no frontend com download handler
7. **Testes**: backend (5 testes) + frontend (4 testes)

### Dependências de sistema para WeasyPrint

WeasyPrint requer bibliotecas C. No Ubuntu/WSL2:

```bash
sudo apt install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

Se WeasyPrint não conseguir instalar/rodar, alternativa aceitável: **xhtml2pdf** (puro Python, sem deps de sistema). Mas WeasyPrint é a decisão arquitetural — tentar primeiro.

### Padrão de referência — pdf_service.py

```python
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.models.checklist import Checklist

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "pdf"

env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def generate_checklist_pdf(checklist: Checklist) -> bytes:
    template = env.get_template("checklist.html")
    html_content = template.render(
        checklist=checklist,
        itens=checklist.itens or [],
        itens_devolucao=checklist.itens_devolucao or [],
        avarias=checklist.avarias or [],
        is_devolvido=checklist.status.value == "devolvido",
    )
    return HTML(string=html_content).write_pdf()
```

### Padrão de referência — routes/pdf.py

```python
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.services.checklist_service import ChecklistError, get_checklist_by_id
from app.services.pdf_service import generate_checklist_pdf

router = APIRouter(prefix="/checklists", tags=["pdf"])


@router.get("/{checklist_id}/pdf")
def download_pdf(
    checklist_id: int,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(get_current_user)],
):
    checklist = get_checklist_by_id(session, checklist_id)
    if not checklist.is_locked:
        raise ChecklistError(
            status_code=400,
            detail="MSG-019",
            message="As opções de compartilhamento e impressão estarão disponíveis após o salvamento do checklist.",
            fields=[],
        )
    pdf_bytes = generate_checklist_pdf(checklist)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="checklist-{checklist_id}.pdf"',
        },
    )
```

### Padrão de referência — Template HTML do PDF

O template deve renderizar dados diretamente do model `Checklist`. Campos-chave:

| Campo do Model | Uso no PDF | Formato |
|----------------|------------|---------|
| `placa`, `unidade`, `subunidade`, `motorista`, `matricula_motorista`, `quilometragem_inicial` | Seção "Informações Gerais" | Texto |
| `itens` (JSON array) | Tabela de itens da entrega com ✓/✗ | `[{"nome": "...", "status": "ok"/"nao_ok"}]` |
| `nivel_combustivel` | Indicador de combustível | `"1/4"`, `"2/4"`, `"3/4"`, `"4/4"` |
| `data_entrega` | Data formatada | `datetime` → `dd/mm/aaaa HH:mm` |
| `avarias` (JSON array) | Mapa de avarias simplificado (tabela/lista) | `[{"x": 50, "y": 30, "vista": "topo", "tipo": "risco"}]` |
| `assinatura_responsavel`, `assinatura_motorista` | `<img src="{{ base64 }}">` | `data:image/png;base64,...` |
| `observacoes` | Texto livre | `string | None` |
| Mesmos campos com sufixo `_devolucao` | Seção "Devolução" (se devolvido) | Idem |

**Mapa de avarias no PDF**: Não precisa re-renderizar o SVG interativo. Duas abordagens aceitas:
1. **Tabela simples**: listar avarias como `Vista | Tipo | Coordenada (x%, y%)`
2. **SVG estático inline** no HTML com pontos plotados (mais fiel ao original mas mais complexo)

Recomendação: começar com tabela (T2), evoluir para SVG se necessário.

**Assinaturas no PDF**: renderizar como `<img>` com o base64 diretamente:
```html
{% if checklist.assinatura_responsavel %}
<img src="{{ checklist.assinatura_responsavel }}" alt="Assinatura do Responsável" style="max-width: 300px; height: auto;" />
{% endif %}
```

### Padrão de referência — Frontend download handler

```typescript
const onDownloadPdf = async () => {
  try {
    const response = await apiClient.get(`/v1/checklists/${id}/pdf`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `checklist-${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    window.alert("PDF gerado com sucesso.");
  } catch (error) {
    if (isAxiosError(error) && error.response?.data) {
      const text = await (error.response.data as Blob).text();
      try {
        const json = JSON.parse(text);
        window.alert(json.detail || "Erro ao gerar PDF.");
      } catch {
        window.alert("Erro ao gerar PDF. Tente novamente.");
      }
    } else {
      window.alert("Erro ao gerar PDF. Tente novamente.");
    }
  }
};
```

**NOTA**: Quando `responseType: "blob"` é usado, erros do backend também chegam como Blob. É necessário converter para texto e parsear JSON para extrair a mensagem de erro.

### Padrão de referência — Botão no ChecklistView

Adicionar botão **antes** dos cards de entrega/devolução read-only, na seção de informações gerais ou logo abaixo do título. O botão só aparece quando `checklist.is_locked`:

```tsx
{checklist.is_locked && (
  <Button
    type="button"
    variant="outline"
    onClick={onDownloadPdf}
    disabled={isDownloading}
  >
    {isDownloading ? "Gerando PDF..." : "Gerar PDF"}
  </Button>
)}
```

### Registro do router em main.py

Adicionar import e include_router seguindo o padrão existente:

```python
from app.api.routes import auth, checklists, pdf, users
# ...
app.include_router(pdf.router, prefix="/api/v1")
```

### Banco de dados

Sem alteração no modelo. Sem migração. Sem necessidade de deletar `ctrve.db`.

### Anti-padrões (PROIBIDO)

- Gerar PDF no frontend (jsPDF, html2pdf) — decisão arquitetural é WeasyPrint no backend
- Criar endpoint POST para gerar PDF — usar GET (idempotente, cacheable)
- Armazenar PDF no banco — gerar on-demand a cada request
- Criar novo schema Pydantic para resposta do PDF — retornar `Response` direto com bytes
- Usar `StreamingResponse` sem necessidade — o PDF é pequeno, `Response` com bytes é suficiente
- Instalar bibliotecas de PDF no frontend — PDF é gerado server-side
- Criar feature folder `features/pdf/` com componentes separados — para MVP, botão diretamente no `ChecklistView.tsx` é suficiente (arquitetura prevê o folder mas o escopo atual não justifica)
- Usar `fetch` direto — usar `apiClient` (padrão do projeto)

### Aprendizados de Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 5.2 |
|-------------|--------------|-----------------|
| `ChecklistError` para erros de negócio com `detail`+`message` | Todas as stories | Guard de is_locked usa mesmo padrão |
| `get_current_user` (sem role check) para ambos perfis | `deps.py` | Endpoint PDF aceita Responsável e Motorista |
| `isAxiosError` para type-guard | Story 5.1 | Erro no download handler |
| `window.alert` para mensagens de sucesso | Story 5.1 | MSG-025 |
| `queryKey: ["checklists", id]` | `ChecklistView.tsx:315` | Não precisa invalidar cache (GET não altera dados) |
| Router registration em `main.py` | `main.py:76-78` | Mesmo padrão para pdf router |
| `locked_checklist` fixture tem `is_locked=True`, `status=entregue` | `conftest.py:117-137` | Usar direto para testar PDF de entrega |
| Backend testes verificam `response.status_code` antes de asserts | Code review 4.2 | Aplicar em todos os testes |
| Erro blob → texto → JSON no frontend | Padrão novo | Necessário quando responseType é blob |

### Impacto em Testes Existentes

Nenhum. Esta story cria arquivos novos e adiciona um router. Nenhum arquivo existente é modificado exceto `main.py` (import + include_router) que não afeta testes existentes.

### Sequência de Implementação Recomendada

1. T1 (deps WeasyPrint) → verificar instalação com `python -c "from weasyprint import HTML"`
2. T2 (template HTML/CSS) → pode ser testado manualmente com dados mockados
3. T3 (pdf_service) → testar com `python -c "from app.services.pdf_service import generate_checklist_pdf"`
4. T4 (route + registro) → testar via curl ou TestClient
5. T5 (testes backend) → garantir que endpoint funciona end-to-end
6. T6 (frontend botão + download) → testar manualmente no browser
7. T7 (testes frontend) → validar tudo

### Project Structure Notes

**Arquivos novos nesta story:**
- `backend/app/templates/pdf/checklist.html` — template Jinja2
- `backend/app/templates/pdf/checklist.css` — estilos do PDF
- `backend/app/services/pdf_service.py` — geração HTML→PDF
- `backend/app/api/routes/pdf.py` — endpoint GET
- `backend/tests/api/test_pdf.py` — testes do endpoint

**Arquivos modificados:**
- `backend/requirements.txt` — adicionar weasyprint, jinja2
- `backend/app/main.py` — registrar pdf router

**Nenhum arquivo frontend novo** — botão adicionado diretamente em `ChecklistView.tsx`.

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-023 (geração PDF)
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-019 (botões desabilitados), MSG-025 (sucesso)
- User story: `_bmad-output/requirements/user-stories.md` — US-012
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — WeasyPrint, template HTML/CSS, endpoint GET, `features/pdf/`
- Epics: `_bmad-output/planning-artifacts/epics.md` — Story 5.2
- Story anterior: `_bmad-output/implementation-artifacts/5-1-salvar-checklist.md` — padrões de save, error handling, is_locked
- Deferred work: `_bmad-output/implementation-artifacts/deferred-work.md` — nenhum item diretamente aplicável a esta story

## Dev Agent Record

### Agent Model Used

claude-opus-4-6 — 2026-04-27

### Debug Log References

- Template Jinja2 usa `item is mapping` guard para lidar com dict vs object (itens/avarias podem vir como dict quando lidos de JSON no SQLite).
- `autoescape=True` no Jinja2 Environment para prevenir XSS. Assinaturas base64 renderizadas via `<img src>` não são afetadas pois não passam por escaping de atributos HTML.
- Erro blob no frontend: quando `responseType: "blob"`, erros axios retornam data como Blob. Necessário `await blob.text()` + `JSON.parse()` para extrair detail.

### Completion Notes List

- Backend: `pdf_service.py` gera PDF via Jinja2 + WeasyPrint. Template HTML inclui todas as seções: dados gerais, itens entrega/devolução, combustível, avarias (tabela), assinaturas (img base64), observações. CSS inline via variável para evitar problemas de path.
- Backend: `routes/pdf.py` com `GET /checklists/{id}/pdf` — guard de `is_locked`, retorna `Response` com `application/pdf` + `Content-Disposition: attachment`.
- Backend: Router registrado em `main.py`. WeasyPrint e Jinja2 adicionados ao `requirements.txt`.
- Frontend: Botão "Gerar PDF" em `ChecklistView.tsx` — visível apenas quando `checklist.is_locked`. Download via blob URL + `<a>` temporário. MSG-025 via `window.alert`. Erros do backend extraídos de blob response.
- 100 testes backend / 96 testes frontend passando. Sem regressões.

### Change Log

- 2026-04-27: Story 5.2 implementada — backend WeasyPrint + Jinja2 PDF, frontend download button, 9 novos testes (5 backend + 4 frontend).

### File List

- backend/requirements.txt (modificado)
- backend/app/main.py (modificado)
- backend/app/services/pdf_service.py (novo)
- backend/app/api/routes/pdf.py (novo)
- backend/app/templates/pdf/checklist.html (novo)
- backend/app/templates/pdf/checklist.css (novo)
- backend/tests/api/test_pdf.py (novo)
- frontend/src/features/checklist/ChecklistView.tsx (modificado)
- frontend/src/features/checklist/__tests__/ChecklistView.test.tsx (modificado)
