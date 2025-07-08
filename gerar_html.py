import plotly.express as px

fig = px.line(x=[1, 2, 3], y=[10, 20, 30], title="Exemplo de Gráfico")

fig.write_html("docs/grafico.html")
