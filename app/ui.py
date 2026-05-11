import json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.database import get_connection


router = APIRouter()


DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Evidence Assistant</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --surface: #ffffff;
      --text: #172026;
      --muted: #5f6b76;
      --line: #d9dee5;
      --accent: #0f766e;
      --accent-dark: #0b5f59;
      --danger: #b42318;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      --sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      font-size: 15px;
      line-height: 1.45;
    }

    header {
      border-bottom: 1px solid var(--line);
      background: var(--surface);
    }

    .wrap {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 0;
    }

    h1 {
      margin: 0;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0;
    }

    .status {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    main {
      padding: 22px 0 36px;
    }

    section {
      margin-top: 24px;
    }

    h2 {
      margin: 0 0 10px;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0;
    }

    form {
      display: grid;
      grid-template-columns: minmax(160px, 260px) 1fr auto;
      gap: 10px;
      align-items: stretch;
      padding: 14px;
      border: 1px solid var(--line);
      background: var(--surface);
    }

    input,
    textarea,
    button {
      font: inherit;
    }

    input,
    textarea {
      width: 100%;
      border: 1px solid var(--line);
      background: #fff;
      color: var(--text);
      padding: 10px 11px;
      border-radius: 4px;
    }

    textarea {
      min-height: 44px;
      max-height: 160px;
      resize: vertical;
    }

    button {
      border: 0;
      background: var(--accent);
      color: #fff;
      padding: 0 16px;
      border-radius: 4px;
      font-weight: 700;
      cursor: pointer;
      min-width: 120px;
    }

    button:hover {
      background: var(--accent-dark);
    }

    button:disabled {
      cursor: wait;
      opacity: 0.65;
    }

    .message {
      margin-top: 8px;
      min-height: 20px;
      color: var(--muted);
      font-size: 13px;
    }

    .message.error {
      color: var(--danger);
    }

    .table-shell {
      overflow-x: auto;
      border: 1px solid var(--line);
      background: var(--surface);
    }

    table {
      width: 100%;
      min-width: 760px;
      border-collapse: collapse;
      table-layout: fixed;
    }

    th,
    td {
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      text-align: left;
    }

    th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      background: #fbfcfd;
    }

    tr:last-child td {
      border-bottom: 0;
    }

    .mono {
      font-family: var(--mono);
      font-size: 12px;
      word-break: break-all;
    }

    .preview {
      color: var(--muted);
      word-break: break-word;
    }

    .num {
      text-align: right;
      white-space: nowrap;
    }

    .empty {
      color: var(--muted);
      padding: 14px;
      border: 1px solid var(--line);
      background: var(--surface);
    }

    @media (max-width: 760px) {
      .topbar {
        align-items: flex-start;
        flex-direction: column;
      }

      form {
        grid-template-columns: 1fr;
      }

      button {
        min-height: 42px;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <h1>AI Evidence Assistant</h1>
      <div class="status" id="status">Loading tables...</div>
    </div>
  </header>

  <main class="wrap">
    <section>
      <h2>Add Document</h2>
      <form id="document-form">
        <input id="title" name="title" placeholder="Title" autocomplete="off" required>
        <textarea id="text" name="text" placeholder="Paste document text" required></textarea>
        <button id="submit-button" type="submit">Add</button>
      </form>
      <div class="message" id="message"></div>
    </section>

    <section>
      <h2>Documents</h2>
      <div id="documents"></div>
    </section>

    <section>
      <h2>Chunks</h2>
      <div id="chunks"></div>
    </section>

    <section>
      <h2>Embeddings</h2>
      <div id="embeddings"></div>
    </section>
  </main>

  <script>
    const statusEl = document.getElementById("status");
    const messageEl = document.getElementById("message");
    const formEl = document.getElementById("document-form");
    const submitButton = document.getElementById("submit-button");

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function tableOrEmpty(rows, headers, renderRow) {
      if (!rows.length) {
        return '<div class="empty">No rows yet.</div>';
      }

      const head = headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("");
      const body = rows.map(renderRow).join("");
      return `<div class="table-shell"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
    }

    async function loadData() {
      const response = await fetch("/ui/data");
      if (!response.ok) {
        throw new Error("Could not load UI data");
      }
      const data = await response.json();

      document.getElementById("documents").innerHTML = tableOrEmpty(
        data.documents,
        ["ID", "Title", "Words", "Chars", "Chunks", "Preview"],
        (row) => `
          <tr>
            <td class="mono">${escapeHtml(row.id)}</td>
            <td>${escapeHtml(row.title)}</td>
            <td class="num">${escapeHtml(row.word_count)}</td>
            <td class="num">${escapeHtml(row.char_count)}</td>
            <td class="num">${escapeHtml(row.chunk_count)}</td>
            <td class="preview">${escapeHtml(row.text_preview)}</td>
          </tr>
        `
      );

      document.getElementById("chunks").innerHTML = tableOrEmpty(
        data.chunks,
        ["Chunk ID", "Document", "Index", "Words", "Chars", "Text"],
        (row) => `
          <tr>
            <td class="mono">${escapeHtml(row.id)}</td>
            <td>${escapeHtml(row.document_title)}</td>
            <td class="num">${escapeHtml(row.chunk_index)}</td>
            <td class="num">${escapeHtml(row.word_count)}</td>
            <td class="num">${escapeHtml(row.char_count)}</td>
            <td class="preview">${escapeHtml(row.text_preview)}</td>
          </tr>
        `
      );

      document.getElementById("embeddings").innerHTML = tableOrEmpty(
        data.embeddings,
        ["Chunk ID", "Document", "Index", "Model", "Dims", "Preview"],
        (row) => `
          <tr>
            <td class="mono">${escapeHtml(row.chunk_id)}</td>
            <td>${escapeHtml(row.document_title)}</td>
            <td class="num">${escapeHtml(row.chunk_index)}</td>
            <td class="mono">${escapeHtml(row.model_name)}</td>
            <td class="num">${escapeHtml(row.dimensions)}</td>
            <td class="mono">${escapeHtml(row.embedding_preview.join(", "))}</td>
          </tr>
        `
      );

      statusEl.textContent = `${data.documents.length} documents, ${data.chunks.length} chunks, ${data.embeddings.length} embeddings`;
    }

    formEl.addEventListener("submit", async (event) => {
      event.preventDefault();
      messageEl.className = "message";
      messageEl.textContent = "Saving document...";
      submitButton.disabled = true;

      const payload = {
        title: document.getElementById("title").value,
        text: document.getElementById("text").value,
      };

      try {
        const response = await fetch("/documents", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || "Request failed");
        }

        formEl.reset();
        messageEl.textContent = "Document saved.";
        await loadData();
      } catch (error) {
        messageEl.className = "message error";
        messageEl.textContent = `Could not save document. ${error.message}`;
      } finally {
        submitButton.disabled = false;
      }
    });

    loadData().catch(() => {
      statusEl.textContent = "Could not load tables";
    });
  </script>
</body>
</html>
"""


def _preview(text: str, limit: int = 160) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


@router.get("/ui", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)


@router.get("/ui/data")
def dashboard_data():
    with get_connection() as conn:
        document_rows = conn.execute(
            """
            SELECT d.id, d.title, d.text, d.char_count, d.word_count, COUNT(c.id)
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id, d.title, d.text, d.char_count, d.word_count
            ORDER BY d.rowid DESC
            """
        ).fetchall()

        chunk_rows = conn.execute(
            """
            SELECT c.id, c.document_id, d.title, c.chunk_index, c.text, c.char_count, c.word_count
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY d.rowid DESC, c.chunk_index
            """
        ).fetchall()

        embedding_rows = conn.execute(
            """
            SELECT e.chunk_id, e.embedding, e.model_name, e.dimensions, c.document_id, c.chunk_index, d.title
            FROM chunk_embeddings e
            JOIN chunks c ON c.id = e.chunk_id
            JOIN documents d ON d.id = c.document_id
            ORDER BY d.rowid DESC, c.chunk_index
            """
        ).fetchall()

    documents = [
        {
            "id": row[0],
            "title": row[1],
            "text_preview": _preview(row[2]),
            "char_count": row[3],
            "word_count": row[4],
            "chunk_count": row[5],
        }
        for row in document_rows
    ]

    chunks = [
        {
            "id": row[0],
            "document_id": row[1],
            "document_title": row[2],
            "chunk_index": row[3],
            "text_preview": _preview(row[4]),
            "char_count": row[5],
            "word_count": row[6],
        }
        for row in chunk_rows
    ]

    embeddings = []
    for row in embedding_rows:
        embedding = json.loads(row[1])
        embeddings.append(
            {
                "chunk_id": row[0],
                "embedding_preview": [round(value, 4) for value in embedding[:5]],
                "model_name": row[2],
                "dimensions": row[3],
                "document_id": row[4],
                "chunk_index": row[5],
                "document_title": row[6],
            }
        )

    return {
        "documents": documents,
        "chunks": chunks,
        "embeddings": embeddings,
    }
