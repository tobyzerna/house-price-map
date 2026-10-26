import requests
import plotly.graph_objects as go
import plotly.io as pio

# notebook: embed the chart in the output. Plain script: open it in the browser
try:
    get_ipython()
    pio.renderers.default = "notebook_connected"
except NameError:
    pass

# median established house price in $'000, June 2026, from ABS Table 2
# (Median Price of Established House Transfers, Unstratified)
prices = {"Sydney": 1487.6, "Melbourne": 850.0, "Brisbane": 1155.0, "Adelaide": 975.0,
          "Perth": 1010.0, "Hobart": 750.0, "Darwin": 752.5, "Canberra": 1030.0}

# get coastline data from GitHub repo
coast_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/AUS.geo.json"
response = requests.get(coast_URL)
response.raise_for_status()
geojson = response.json()

# polygon and multipolygon geometries
geom = geojson["features"][0]["geometry"]
polygons = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
coast_lon, coast_lat = [], []
for polygon in polygons:
    ring = polygon[0]
    coast_lon += [pt[0] for pt in ring] + [None]
    coast_lat += [pt[1] for pt in ring] + [None]

# city centre coordinates and label positions
coords = {
    "Sydney":    (151.2093, -33.8688, "middle right"),
    "Melbourne": (144.9631, -37.8136, "bottom left"),
    "Brisbane":  (153.0251, -27.4698, "middle right"),
    "Adelaide":  (138.6007, -34.9285, "bottom left"),
    "Perth":     (115.8605, -31.9505, "middle left"),
    "Hobart":    (147.3272, -42.8821, "middle right"),
    "Darwin":    (130.8456, -12.4634, "middle right"),
    "Canberra":  (149.1300, -35.2809, "middle left"),
}

# colour scale from colorbrewer2.org, 6-class Reds
REDS_6 = ["#fee5d9", "#fcbba1", "#fc9272", "#fb6a4a", "#de2d26", "#a50f15"]
BREAKS = [800, 900, 1000, 1100, 1300]
# only one dollar sign per label, because two make Plotly treat the text as maths
LABELS = ["Under $800k", "$800k to 900k", "$900k to 1m",
          "$1m to 1.1m", "$1.1m to 1.3m", "Over $1.3m"]

def class_of(price):
    return sum(price >= b for b in BREAKS)

fig = go.Figure()

# coastline
fig.add_trace(go.Scatter(x=coast_lon, y=coast_lat, mode="lines", fill="toself",
                         fillcolor="#e5e7eb", line=dict(color="#94a3b8", width=1),
                         hoverinfo="skip", showlegend=False))

# one trace per price class, highest first, so clicking a legend entry
# hides or shows every city in that class
for k in range(5, -1, -1):
    members = [c for c in prices if class_of(prices[c]) == k]
    fig.add_trace(go.Scatter(
        x=[coords[c][0] for c in members] or [None],
        y=[coords[c][1] for c in members] or [None],
        mode="markers+text", name=LABELS[k],
        marker=dict(size=18, color=REDS_6[k], line=dict(width=1, color="#1f2937")),
        text=members or [None],
        textposition=[coords[c][2] for c in members] or ["middle right"],
        textfont=dict(size=11, color="#111827"),
        customdata=[[c, prices[c]] for c in members] or [[None, None]],
        hovertemplate="<b>%{customdata[0]}</b><br>Median house price: "
                      "$%{customdata[1]:,.1f}k<extra></extra>",
    ))

fig.update_xaxes(visible=False, range=[112, 160])
fig.update_yaxes(visible=False, range=[-45.5, -9], scaleanchor="x", scaleratio=1.35)
fig.update_layout(
    title=dict(text="Median House Price by Australian Capital City (June 2026)", x=0.5),
    legend=dict(title="Median house price", x=0, xanchor="left", y=0.3),
    margin=dict(l=10, r=10, t=60, b=10), height=650,
    plot_bgcolor="white", paper_bgcolor="white",
)

fig.show()