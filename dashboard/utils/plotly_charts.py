import plotly.graph_objs as go

def create_chart(
    chart_type,
    x,
    y,
    title='',
    x_title='',
    y_title='',
    color='blue',
    show_title=True,
    show_xaxis=True,
    show_yaxis=True,
    show_legend=True,
    legend_position='top center',  
    mode=None,  
    trace_name='Data',
    secondary_y=False,
    fig=None,  
    **kwargs
):
    """
    Função genérica para criar gráficos Plotly.

    Parâmetros:
    - chart_type: Tipo do gráfico (ex: 'bar', 'scatter', 'pie', 'line', etc.)
    - x: Dados do eixo x
    - y: Dados do eixo y
    - title: Título do gráfico
    - x_title: Título do eixo x
    - y_title: Título do eixo y
    - color: Cor dos elementos do gráfico
    - show_title: Boolean para exibir ou ocultar o título
    - show_xaxis: Boolean para exibir ou ocultar o eixo x
    - show_yaxis: Boolean para exibir ou ocultar o eixo y
    - show_legend: Boolean para exibir ou ocultar a legenda
    - legend_position: Posição da legenda (ex: 'top right', 'top left', 'bottom right', 'bottom left', 'top center')
    - mode: Tipo de linha e marcador (para gráficos de linha)
    - trace_name: Nome do traço
    - secondary_y: Se há um eixo Y secundário
    - fig: Figura existente para combinar gráficos
    """
    
    # Criando o gráfico de acordo com o tipo
    if chart_type == 'bar':
        trace = go.Bar(
            x=x,
            y=y,
            name=trace_name,
            marker=dict(color=color),
            yaxis='y2' if secondary_y else 'y1'
        )
    elif chart_type == 'line':
        trace = go.Scatter(
            x=x,
            y=y,
            name=trace_name,
            mode=mode or 'lines',  # Garantir que o modo padrão seja 'lines'
            line=dict(color=color),
            yaxis='y2' if secondary_y else 'y1'
        )
    else:
        raise ValueError(f"Gráfico do tipo {chart_type} não suportado.")

    # Se uma figura existente for fornecida, adicionar o trace a ela
    if fig:
        fig.add_trace(trace)
    else:
        # Caso contrário, criar uma nova figura
        fig = go.Figure(data=[trace])

    # Definir a posição da legenda
    legend_x, legend_y = 1, 1  # Posição padrão: 'top right'
    legend_xanchor = 'auto'
    if legend_position == 'top left':
        legend_x, legend_y = 0, 1
    elif legend_position == 'bottom right':
        legend_x, legend_y = 1, 0
    elif legend_position == 'bottom left':
        legend_x, legend_y = 0, 0
    elif legend_position == 'top center':
        legend_x, legend_y = 0.5, 1.2
        legend_xanchor = 'center'

    # Layout do gráfico
    layout = go.Layout(
        title=title,
        xaxis=dict(title=x_title, showgrid=False, zeroline=False, showticklabels=show_xaxis),
        yaxis=dict(title=y_title, showgrid=False, zeroline=False, showticklabels=show_yaxis),
        yaxis2=dict(title=y_title, overlaying='y', side='right', showgrid=False, zeroline=False) if secondary_y else None,
        showlegend=show_legend,
        legend=dict(x=legend_x, y=legend_y, xanchor=legend_xanchor),
        margin=dict(t=120 if legend_position == 'top center' else 50),
        template="plotly",  
        **kwargs  
    )

    fig.update_layout(layout)

    return fig