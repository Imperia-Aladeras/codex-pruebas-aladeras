import os, re, json, nbformat
import pandas as pd
from pathlib import Path

# === Configura aquí la carpeta con tus notebooks ===
NOTEBOOK_DIR = "notebooks"  # cambia si hace falta

# Patrones: amplía/ajusta según tus librerías
MODEL_PATTERNS = [
    r'\bAutoARIMA\b', r'\bARIMA\b', r'\bSARIMA\b', r'\bSARIMAX\b',
    r'\bETS\b', r'\bHolt(?:Winters)?\b', r'\bProphet\b',
    r'\bCroston\b', r'\bTSB\b', r'\bADIDA\b',
    r'\bXGBoost\b', r'\bLightGBM\b', r'\bRandomForest\b',
    r'\bLSTM\b', r'\bTFT\b', r'\bNBEATS?\b', r'\bNHITS?\b',
    r'\bNeuralForecast\b', r'\bstatsforecast\b'
]

METRIC_PATTERNS = [
    r'\bMAPE\b', r'\bsMAPE\b', r'\bMAE\b', r'\bRMSE\b', r'\bRMSLE\b',
    r'\bMASE\b', r'\bMdAPE\b', r'\bpinball\b', r'\bquantile\b'
]

PREP_PATTERNS = {
    'fechas_datetime': r'pd\.to_datetime|datetime\(',
    'relleno_nulos': r'\.fillna\(|SimpleImputer|KNNImputer',
    'outliers': r'ZScore|IQR|winsor|clip\(',
    'resampleo': r'\.resample\(|asfreq\(',
    'scaling': r'StandardScaler|MinMaxScaler|RobustScaler',
    'features_calendario': r'holiday|holidays|fourier|sin\(|cos\(',
}

VALIDATION_PATTERNS = {
    'backtesting': r'backtest|backtesting|TimeSeriesSplit|temporal\.cv',
    'horizonte': r'horizon|fh=|forecast_horizon|h=\s*\d+',
    'cv': r'CrossVal|TimeSeriesSplit|cv=',
}

DEMAND_TYPE_HINTS = {
    'intermitente': r'Croston|TSB|intermittent|zero-inflated|sparse',
    'continua': r'ARIMA|ETS|Prophet|XGBoost|LightGBM|LSTM|TFT|NBEATS|NHITS'
}

def extract_text_from_notebook(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    texts = []
    for cell in nb.cells:
        if cell.cell_type in ('code', 'markdown'):
            texts.append(cell.source)
    return "\n".join(texts)

def find_all(patterns, text):
    found = set()
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            found.add(re.findall(p, text, flags=re.IGNORECASE)[0])
    return sorted(found)

def find_keys(dct, text):
    hits = []
    for k, p in dct.items():
        if re.search(p, text, flags=re.IGNORECASE):
            hits.append(k)
    return hits

def guess_objective(text):
    # heurística simple por títulos/palabras clave
    for line in text.splitlines():
        if len(line) > 8 and ('#' in line or '##' in line or 'Objetivo' in line or 'Goal' in line):
            return line.strip('# ').strip()[:120]
    return 'Exploración / Experimento'

def detect_data_info(text):
    # heurísticas muy simples para dar pistas
    source = []
    if re.search(r'\.csv\'|\.csv\"|read_csv', text): source.append('CSV')
    if re.search(r'read_parquet|\.parquet', text): source.append('Parquet')
    if re.search(r'sql|read_sql|to_sql', text, re.I): source.append('SQL')
    if re.search(r'Excel|read_excel|\.xlsx', text, re.I): source.append('Excel')
    gran = '¿Diario/Semanal/Mensual?' if re.search(r'resample|asfreq', text, re.I) else 'No detectada'
    return ', '.join(source) or 'No detectada', gran

def demand_types(text):
    hits = find_keys(DEMAND_TYPE_HINTS, text)
    return ', '.join(sorted(set(hits))) or 'No detectado'

def main():
    rows = []
    md_lines = ["# Resumen de notebooks\n"]

    for p in sorted(Path(NOTEBOOK_DIR).glob("*.ipynb")):
        try:
            txt = extract_text_from_notebook(p)
            models = find_all(MODEL_PATTERNS, txt)
            metrics = find_all(METRIC_PATTERNS, txt)
            prep = find_keys(PREP_PATTERNS, txt)
            val = find_keys(VALIDATION_PATTERNS, txt)
            objetivo = guess_objective(txt)
            datos_fuente, granularidad = detect_data_info(txt)
            tipos = demand_types(txt)

            row = {
                "notebook": p.name,
                "objetivo": objetivo,
                "datos_fuente": datos_fuente,
                "granularidad": granularidad,
                "preprocesado": ', '.join(prep) or 'No detectado',
                "modelos": ', '.join(models) or 'No detectado',
                "tipos_demanda": tipos,
                "validacion": ', '.join(val) or 'No detectado',
                "metricas": ', '.join(metrics) or 'No detectado'
            }
            rows.append(row)

            md_lines += [
                f"## {p.name}",
                f"- **Objetivo:** {objetivo}",
                f"- **Datos:** {datos_fuente} · **Granularidad:** {granularidad}",
                f"- **Preprocesado:** {row['preprocesado']}",
                f"- **Modelos:** {row['modelos']}",
                f"- **Tipos de demanda:** {row['tipos_demanda']}",
                f"- **Validación:** {row['validacion']}",
                f"- **Métricas:** {row['metricas']}",
                ""
            ]
        except Exception as e:
            md_lines += [f"## {p.name}", f"- Error leyendo: {e}", ""]

    df = pd.DataFrame(rows)
    out_csv = "notebook_audit.csv"
    out_md = "notebook_summary.md"
    df.to_csv(out_csv, index=False)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"[OK] Guardado CSV: {out_csv}")
    print(f"[OK] Guardado Markdown: {out_md}")
    if rows:
        print("\nVista previa:")
        print(df.head(min(5, len(df))).to_string(index=False))

if __name__ == "__main__":
    main()
