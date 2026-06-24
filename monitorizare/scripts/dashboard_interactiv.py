
import pandas as pd
import os
from dash import Dash, dcc, html, dash_table, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "log_culturi.csv")
REFRESH_INTERVAL_MS = 3000


def load_data():
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        return pd.DataFrame(columns=[
            "timestamp", "stage", "conf_stage", "disease", "conf_disease",
            "recommendation", "fps"
        ])
    df = pd.read_csv(CSV_PATH)
    for col in ["conf_stage", "conf_disease", "fps"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def make_figures(df):
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Fara date inca")
        return {k: empty_fig for k in [
            "Distributia stadiilor", "Distributia bolilor",
            "Procent boli detectate", "Evolutia scorului de incredere",
            "Heatmap: Stadiu x Boala"
        ]}

    stage_counts = df["stage"].value_counts().rename_axis(
        "stage").reset_index(name="count")
    disease_counts = df["disease"].value_counts().rename_axis(
        "disease").reset_index(name="count")

    fig_stage = px.bar(stage_counts, x="stage", y="count",
                       title="Distributia stadiilor", color="stage",
                       color_discrete_sequence=px.colors.qualitative.Pastel)

    fig_disease = px.bar(disease_counts, x="disease", y="count",
                         title="Distributia bolilor", color="disease",
                         color_discrete_sequence=px.colors.qualitative.Pastel)

    fig_pie = px.pie(df, names="disease", title="Procent boli detectate",
                     color="disease", color_discrete_sequence=px.colors.qualitative.Pastel)

    df_plot = df.reset_index(drop=True)
    fig_conf = go.Figure()
    fig_conf.add_trace(go.Scatter(y=df_plot["conf_stage"], mode="lines+markers",
                                  name="Confidence stadiu", line=dict(color="#66c2a5")))
    fig_conf.add_trace(go.Scatter(y=df_plot["conf_disease"], mode="lines+markers",
                                  name="Confidence boala", line=dict(color="#fc8d62")))
    fig_conf.update_layout(
        title="Evolutia scorurilor de incredere", yaxis_range=[0, 1])

    heatmap_data = pd.crosstab(df["stage"], df["disease"])
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values, x=heatmap_data.columns,
        y=heatmap_data.index, colorscale="YlGnBu"))
    fig_heatmap.update_layout(title="Heatmap: Stadiu x Boala")

    return {
        "Distributia stadiilor": fig_stage,
        "Distributia bolilor": fig_disease,
        "Procent boli detectate": fig_pie,
        "Evolutia scorului de incredere": fig_conf,
        "Heatmap: Stadiu x Boala": fig_heatmap
    }


app = Dash(__name__)


def wrap(fig, graph_id):
    return html.Div(dcc.Graph(id=graph_id, figure=fig),
                    style={"backgroundColor": "#ffffff", "padding": "20px",
                           "borderRadius": "12px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"})


app.layout = html.Div(id="root", style={"fontFamily": "Arial, sans-serif"}, children=[
    dcc.Interval(id="refresh-interval",
                 interval=REFRESH_INTERVAL_MS, n_intervals=0),
    dcc.Store(id="figures-store"),

    html.Div([
        html.H1("Dashboard Interactiv Monitorizare Culturi",
                style={"color": "#333", "margin": "0", "fontWeight": "bold"}),
        html.Div([
            dcc.Dropdown(id="figure-select",
                         options=[{"label": k, "value": k} for k in [
                             "Distributia stadiilor", "Distributia bolilor",
                             "Procent boli detectate", "Evolutia scorului de incredere",
                             "Heatmap: Stadiu x Boala"]],
                         placeholder="Alege figura",
                         style={"width": "220px", "marginRight": "10px"}),
            dcc.Dropdown(id="download-type",
                         options=[{"label": f, "value": f}
                                  for f in ["csv", "png", "jpg", "pdf"]],
                         placeholder="Format",
                         style={"width": "120px", "marginRight": "10px"}),
            html.Button("Download", id="download-btn", n_clicks=0,
                        style={"padding": "10px 20px", "backgroundColor": "#66c2a5",
                               "color": "white", "borderRadius": "8px",
                               "border": "none", "cursor": "pointer"}),
            dcc.Download(id="download-data"),
        ], style={"display": "flex", "alignItems": "center"})
    ], style={"display": "flex", "justifyContent": "space-between",
              "alignItems": "center", "padding": "20px",
              "backgroundColor": "#f7f7f7", "borderRadius": "12px",
              "marginBottom": "25px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"}),

    html.Div(id="kpi-row", style={"display": "flex", "justifyContent": "space-between",
                                  "marginBottom": "40px"}),

    html.Div([
        html.Div([wrap(go.Figure(), "fig-stage")], style={"width": "50%"}),
        html.Div([wrap(go.Figure(), "fig-disease")], style={"width": "50%"}),
    ], style={"display": "flex", "gap": "20px"}),

    html.Div([
        html.Div([wrap(go.Figure(), "fig-pie")], style={"width": "50%"}),
        html.Div([wrap(go.Figure(), "fig-conf")], style={"width": "50%"}),
    ], style={"display": "flex", "gap": "20px", "marginTop": "30px"}),

    html.Div([wrap(go.Figure(), "fig-heatmap")], style={"marginTop": "30px"}),

    html.H2("Ultimele 15 rezultate", style={"marginTop": "40px"}),
    html.Div(id="table-container"),
])


@app.callback(
    Output("kpi-row", "children"),
    Output("fig-stage", "figure"),
    Output("fig-disease", "figure"),
    Output("fig-pie", "figure"),
    Output("fig-conf", "figure"),
    Output("fig-heatmap", "figure"),
    Output("table-container", "children"),
    Output("figures-store", "data"),
    Input("refresh-interval", "n_intervals"),
)
def refresh(_n):
    df = load_data()
    figs = make_figures(df)

    if df.empty:
        total_samples, most_common_stage = 0, "—"
        most_common_disease, avg_conf_disease = "—", 0.0
    else:
        total_samples = len(df)
        most_common_stage = df["stage"].value_counts().idxmax()
        most_common_disease = df["disease"].value_counts().idxmax()
        avg_conf_disease = df["conf_disease"].mean()

    def kpi_card(title, value, color):
        return html.Div([
            html.H3(title, style={"fontWeight": "bold", "fontSize": "20px"}),
            html.H2(value, style={"fontWeight": "normal", "fontSize": "18px"})
        ], style={"backgroundColor": color, "padding": "20px",
                  "borderRadius": "12px", "width": "22%"})

    kpi_row = [
        kpi_card("Total mesaje", total_samples, "#ffe6e6"),
        kpi_card("Stadiu frecvent", most_common_stage, "#e6f7ff"),
        kpi_card("Aparitie frecventa", most_common_disease, "#e6ffe6"),
        kpi_card("Confidence mediu (boala)",
                 f"{avg_conf_disease:.3f}", "#fff0e6"),
    ]

    table = html.P("Niciun rezultat primit inca.") if df.empty else dash_table.DataTable(
        df.tail(15).to_dict("records"),
        [{"name": i, "id": i} for i in df.columns],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "6px"},
        style_header={"backgroundColor": "#f0f0f0", "fontWeight": "bold"},
    )

    return (kpi_row,
            figs["Distributia stadiilor"], figs["Distributia bolilor"],
            figs["Procent boli detectate"], figs["Evolutia scorului de incredere"],
            figs["Heatmap: Stadiu x Boala"], table, {"updated": True})


@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    State("download-type", "value"),
    State("figure-select", "value"),
    prevent_initial_call=True
)
def download_file(_n, filetype, fig_name):
    df = load_data()
    if filetype == "csv":
        return dcc.send_data_frame(df.to_csv, "log_culturi.csv", index=False)
    if fig_name is None:
        return None
    fig = make_figures(df).get(fig_name)
    if fig and filetype in ["png", "jpg", "pdf"]:
        return dcc.send_bytes(fig.to_image(format=filetype), f"{fig_name}.{filetype}")


if __name__ == "__main__":
    app.run(debug=True)
