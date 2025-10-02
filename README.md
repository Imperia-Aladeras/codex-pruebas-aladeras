# codex-pruebas-aladeras

Proyecto de **forecast de demanda** (continua e intermitente) con notebooks y utilidades para auditar, comparar y estructurar el trabajo.

## Estructura
- `notebooks/` → experimentos y EDA (.ipynb)
- `src/` → funciones reutilizables (preprocesado, modelos, evaluación)
- `reports/` → resultados, métricas y gráficos
- `data/` → datos locales (no subir datos brutos al repo)
- `audit_notebooks.py` → script que crea `notebook_audit.csv` y `notebook_summary.md`

## Cómo usar (todo desde GitHub)
1. **Subir o mover notebooks**  
   - Entra a `notebooks/` → **Add file → Upload files** (o edita un .ipynb y renómbralo a `notebooks/tu_nb.ipynb`).
2. **Editar código**  
   - Crea/edita archivos en `src/` desde **Add file → Create new file**.
3. **Trabajar con ramas y PRs**  
   - En el selector de rama, crea `feature/…`, haz tus cambios y luego **Compare & pull request** → **Merge**.

## Auditoría de notebooks
Genera un inventario automático de modelos, métricas y pasos de preprocesado.

- **Opción A: GitHub Actions (sin instalar nada)**  
  Si el workflow `Audit Notebooks` está configurado:
  - Cada push en `notebooks/` ejecuta `audit_notebooks.py`.
  - Se actualizan `notebook_audit.csv` y `notebook_summary.md` en el repo.

- **Opción B: Codespaces (rápido)**
  1) **Code → Create codespace on main**  
  2) En la terminal del Codespace:
     ```bash
     python audit_notebooks.py
     ```
  3) Los archivos generados aparecerán en la raíz del repo (haz commit desde el Codespace).

> Requisitos del script (si lo ejecutas): `pandas`, `nbformat` (inclúyelos en `requirements.txt`).

## Buenas prácticas
- Mantén datos grandes **fuera** del repo (`data/` está en `.gitignore`).
- Usa ramas por funcionalidad (`feature/...`) + Pull Requests.
- Migra funciones estables desde notebooks a `src/` para reutilizarlas.
