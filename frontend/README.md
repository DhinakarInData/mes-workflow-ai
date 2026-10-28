# MES Workflow Studio

The frontend accepts a plain-language manufacturing process and displays the
generated MES/FDS workflow as a React Flow diagram. The bundled sample graph
remains available through **Restore sample diagram**.

## Local development

Run the FastAPI backend in one terminal:

```sh
cd backend
uvicorn main:app --reload --port 8000
```

Start the frontend in a second terminal:

```sh
cd frontend
npm install
npm run dev
```

The Vite development server proxies `/workflow` requests to
`http://127.0.0.1:8000`. Override that target with `VITE_API_PROXY_TARGET`.

For a separately hosted API, set `VITE_API_BASE_URL` to the API origin when
building the frontend, and set `FRONTEND_ORIGINS` on the backend to a
comma-separated allowlist of frontend origins.
