import plotly.graph_objects as go
from anomaly import analyze

df= analyze(3)
fig= go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["km"], mode="lines+markers", name="Odometer"))
flagged = df[df["is_rollback"] | df["is_flatline"] | df["is_jump"]]

fig.add_trace(go.Scatter(x=flagged["date"], y=flagged["km"], mode="markers", name="Anomaly", marker=dict(color="red", size=14, symbol="x")))

fig.show()