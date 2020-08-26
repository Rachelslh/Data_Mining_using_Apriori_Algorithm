import dash
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__)
ctx = dash.callback_context
grocery = []
purchased = []
suggested = {}
R = []
indexC = []
components = []


def loadData():
    global grocery, R, indexC
    temp = pd.read_html('grocery.html')
    grocery = pd.DataFrame.to_dict(temp[0].iloc[:, 1:])
    grocery = list(grocery['grocery'].values())

    temp = pd.read_html('rules.html')
    D = pd.DataFrame.to_dict(temp[0].iloc[:, 1:])

    for k1, k2 in D.keys():
        if k1[0] == '(':
            k1 = k1[1:len(k1) - 1].split(', ')
            T1 = (s for s in k1 if s != '')
            T1 = tuple(T1)
        else:
            T1 = tuple(k1)

        if k2[0] == '(':
            k2 = k2[1:len(k2) - 1].split(', ')
            T2 = [s for s in k2 if s != '']
        else:
            T2 = [k2]

        indexC.append(T1)
        R.append(T2)

    print(R)


def init():
    global grocery, components
    li = []

    if len(grocery) == 0:
        loadData()
        for i in range(len(grocery)):
            components.append(html.Button('Ajouter Au Panier', id=str(i), n_clicks=0))
    for i in range(len(grocery)):
        li.append(html.Tr([html.Td(grocery[i]), html.Td(components[i])]))

    return li


def generateRows():
    global components
    li = []

    for k in suggested.keys():
        li.append(html.Tr([html.Td(suggested[k]),
                           html.Td(components[int(k)])]))

    return li


app.layout = html.Div(
    children=[
        html.H1(children='Supermarché'),
        html.Table(
            [
                html.Td(
                    html.Table([html.Thead([html.Tr(html.Th('Aliments Disponibles', scope='col', colSpan=2))]),
                                html.Tbody(init())], id='table1', className='half columns')),
                html.Td(
                    html.Table([], id='table2', className='half columns'))
            ]
        ),

    ])


@app.callback(
    [Output('table1', 'children'),
     Output('table2', 'children')],
    [Input(str(i), 'n_clicks') for i in range(len(components))]
)
def buy(*args):
    global purchased, ctx, suggested, indexC, components
    if not ctx.triggered:
        raise PreventUpdate
    else:
        i = int(ctx.triggered[0]['prop_id'].split('.')[0])
        if grocery[i] not in purchased:
            purchased.append(grocery[i])
            print(purchased)
            components[i] = html.Label('Ajouté', id=str(i))
            sug = []
            purchasedSet = set(purchased)
            suggestedSet = set(suggested)
            for el in indexC:
                k = R[indexC.index(el)]
                k = set(k)
                if set(el).issubset(purchasedSet) and not k.issubset(suggestedSet):
                    l = (k - set(sug))
                    l = [x for x in l if x not in purchased]
                    sug.extend(l)

            for el in sug:
                suggested[str(grocery.index(el))] = el
            print(suggested)

            return html.Table([html.Thead([html.Tr(html.Th('Aliments Disponibles', scope='col', colSpan=2))]),
                               html.Tbody(init())], id='table1', className='half columns'), \
                   html.Table([html.Thead([html.Tr(html.Th('Aliments Suggérés', scope='col', colSpan=2))]),
                               html.Tbody(generateRows())])

    raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
