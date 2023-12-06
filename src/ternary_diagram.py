import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np

default_colors = ["#636EFA" ,"#EF553B" ,"#00CC96" ,"#AB63FA" ,"#FFA15A" ,"#19D3F3" ,"#FF6692" ,"#B6E880" ,"#FF97FF" ,"#FECB52"]
default_markers = ["circle", "square", "diamond", "triangle-up", "triangle-down", 
                    "triangle-left", "triangle-right", "pentagon", "hexagon", "diamond-tall"]

class Ternary:
    def __init__(self, polymer_name: str = "Polymer",
                solvent_name: str = "Solvent",
                non_solvent_name: str = "Non-Solvent"):
        self.polymer_name = polymer_name
        self.solvent_name = solvent_name
        self.non_solvent_name = non_solvent_name
        self.__initFigure()
        self.__arrangeAxis(polymer_name, solvent_name, non_solvent_name)

    def __initFigure(self):
        self.fig = go.Figure()

    def binodalLine(self, polymer, solvent, non_solvent, name: str = "", color: str = "red", style: str = "scatter", symbol: str = "circle"):
        if style == "lines":
            self.lines(polymer, solvent, non_solvent, name, color)
        elif  style == "lines+markers":
            self.scatterAndLine(polymer, solvent, non_solvent, name, color, symbol)
        else:
            self.scatter(polymer, solvent, non_solvent, name, color, symbol)

    def spinodalLine(self, polymer, solvent, non_solvent, name: str = "", color: str = "#54A24B", style: str = "scatter", symbol: str = "circle"):
        if style == "lines":
            self.lines(polymer, solvent, non_solvent, name, color)
        elif  style == "lines+markers":
            self.scatterAndLine(polymer, solvent, non_solvent, name, color, symbol)
        else:
            self.scatter(polymer, solvent, non_solvent, name, color, symbol)

    def tieLine(self, R_polymer, R_solvent, R_non_solvent,
                      L_polymer, L_solvent, L_non_solvent, color: str = "blue"):
        if type(R_polymer) == pd.Series:
            self.tieLine(R_polymer.values, R_solvent.values, R_non_solvent.values,
                         L_polymer.values, L_solvent.values, L_non_solvent.values, color)
        elif type(R_polymer) == np.ndarray or type(R_polymer) == list:
            for i in range(len(R_polymer)):
                self.lines(
                    [R_polymer[i], L_polymer[i]],
                    [R_solvent[i], L_solvent[i]],
                    [R_non_solvent[i], L_non_solvent[i]], None, color
                    )
        else:
            self.lines(
                [R_polymer, L_polymer],
                [R_solvent, L_solvent],
                [R_non_solvent, L_non_solvent], None, color
                )

    def scatter(self, polymer, solvent, non_solvent, name: str = "",
                color: str = "red", symbol: str = "circle", size: int = 10):
        # marker list
        # https://plotly.com/python/marker-style/
        # ["circle", "square", "diamond", "triangle-up", "triangle-down", 
        # "triangle-left", "triangle-right", "pentagon", "hexagon", "diamond-tall"]
        # color list
        # https://www.self-study-blog.com/dokugaku/python-plotly-color-sequence-scales/
        # [#636EFA ,#EF553B ,#00CC96 ,#AB63FA ,#FFA15A ,#19D3F3 ,#FF6692 ,#B6E880 ,#FF97FF ,#FECB52]
        trace = go.Scatterternary(
            a = polymer,
            b = solvent,
            c = non_solvent,
            mode = "markers",
            marker = {"size": size,
                      "color": color,
                      "symbol": symbol},
            showlegend=True,
            name=name,
        )
        self.fig.add_trace(trace)

    def scatterAndLine(self, polymer, solvent, non_solvent, name: str = "",
                color: str = "red", symbol: str = "circle", size: int = 10):
        trace = go.Scatterternary(
            a = polymer,
            b = solvent,
            c = non_solvent,
            mode = "lines+markers",
            marker = {"size": size,
                      "color": color,
                      "symbol": symbol},
            showlegend=True,
            name=name,
        )
        self.fig.add_trace(trace)

    def lines(self, polymer, solvent, non_solvent, name: str = "",
                color: str = "red", opacity: float = 1.):
        if name == None:
            showlegend = False
        else:
            showlegend = True
        trace = go.Scatterternary(
            a = polymer,
            b = solvent,
            c = non_solvent,
            mode = "lines",
            line= {"color": color},
            opacity=opacity,
            showlegend=showlegend,
            name=name,
        )
        self.fig.add_trace(trace)

    def __makeAxis(self, title, tickangle):
        return {
          'title': title,
          'titlefont': { 'size': 24 },
          'tickangle': tickangle,
          'tickfont': {'size': 20, 'family': 'Arial'},
          'tickcolor': 'rgba(0,0,0,0)',
          'ticklen': 5,
          'dtick':0.1,
        #   'color': 'black',
          'linecolor': 'gray',
          'showline': True,
          'showgrid': True,
          'gridcolor':'silver'
        }

    def __arrangeAxis(self, polymer_name: str, 
                    solvent_name: str, non_solvent_name: str):
        # https://plotly.com/python/reference/layout/ternary/
        self.fig.update_layout({
            'title': None,
            'ternary': {
                'aaxis': self.__makeAxis(polymer_name, 0),
                'baxis': self.__makeAxis(solvent_name, 0),
                'caxis': self.__makeAxis(non_solvent_name, 0),
                'bgcolor': 'rgba(0,0,0,0)',
            },
            # 'annotations': [{
            #     'showarrow': False,
            #     'text': "Ternary Diagram",
            #     'x': 0.5,
            #     'y': 1.2,
            #     'font': {'size': 25}
            # }],
        },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

    def saveHTML(self, filepath: str = "./graph.html"):
        plotly.offline.plot(self.fig, filename=filepath, auto_open=False)

    def saveStaticImage(self, filepath: str = "./graph.svg"):
        self.fig.write_image(filepath)

if __name__ == "__main__":
    data = pd.DataFrame([[0.1, 0.2, 0.7],
                         [0.05, 0.25, 0.7],
                         [0.15, 0.45, 0.4]], columns=["poly", "sol", "nsol"])
    data2 = pd.DataFrame([[0.5, 0.2, 0.3],
                         [0.2, 0.7, 0.1],
                         [0.15, 0.8, 0.05]], columns=["poly", "sol", "nsol"])

    tr = Ternary("EVOH", "DMSO", "H2O")
    tr.scatter(data["poly"], data["sol"], data["nsol"], "test")
    tr.scatterAndLine(data2["poly"], data2["sol"], data2["nsol"], "test2", "blue")
    tr.saveHTML()