import plotly
from plotly.graph_objs import *
import pandas as pd

class TriPrism:
# 三角柱プロットするクラス
    def __init__(self, fig: plotly.graph_objs.Figure, zmax: float = 1.0, 
                 polymer_name: str = None, solvent_name: str = None, 
                 non_solvent_name: str = None, z_name: str = None):
        self.fig = fig
        self.zmax = zmax
        self.polymer_name = "Polymer" if polymer_name == None else polymer_name
        self.solvent_name = "Solvent" if solvent_name == None else solvent_name
        self.non_solvent_name = "Non-Solvent" if non_solvent_name == None else non_solvent_name
        self.z_name = "Z" if z_name == None else z_name
        self.__createOutlines()
        self.__arrangeLayout()

    def __createOutlines(self):
        """_summary_
           三角柱を三枚の長方形で構築する
        """
        xs = [0.0, 1.0, 1.0, 0.0, 0.0]
        ys = [0.0, 0.0, 0.0, 0.0, 0.0]
        zs = [0.0, 0.0, self.zmax, self.zmax, 0.0]
        self.xface = Scatter3d(x=xs, y=ys, z=zs, mode='lines',
                           line=dict(width=1, color='black'), showlegend=False)
        xs = [0.0, 0.0, 0.0, 0.0, 0.0]
        ys = [0.0, 1.0, 1.0, 0.0, 0.0]
        zs = [0.0, 0.0, self.zmax, self.zmax, 0.0]
        self.yface = Scatter3d(x=xs, y=ys, z=zs, mode='lines',
                           line=dict(width=1, color='black'), showlegend=False)
        xs = [1.0, 0.0, 0.0, 1.0, 1.0]
        ys = [0.0, 1.0, 1.0, 0.0, 0.0]
        zs = [0.0, 0.0, self.zmax, self.zmax, 0.0]
        self.xyface = Scatter3d(x=xs, y=ys, z=zs, mode='lines',
                           line=dict(width=1, color='black'), showlegend=False)

        self.fig.add_trace(self.xface)
        self.fig.add_trace(self.yface)
        self.fig.add_trace(self.xyface)

    def __arrangeLayout(self):
        """レイアウトを整える
        """
        self.fig.update_layout(
            # scene_xaxis_showticklabels=False,
            # scene_yaxis_showticklabels=False,
            # scene_zaxis_showticklabels=False,
            # showlegend=False,
            margin=dict(l=0, r=0, b=0, t=0),
            scene=Scene(
                aspectmode='cube',
                xaxis=dict(XAxis(title=''),showbackground=False, zerolinecolor="rgba(0,0,0,0)"),
                yaxis=dict(YAxis(title=''),showbackground=False, zerolinecolor="rgba(0,0,0,0)"),
                zaxis=dict(ZAxis(title=''),showbackground=False, zerolinecolor="rgba(0,0,0,0)"),
            )
        )

        x = [1.15, -0.1, -0.15, -0.15]
        y = [-0.1, -0.1, -0.1, 1.1]
        z = [-0.1, -0.1, self.zmax, -0.1]

        axlabel = Scatter3d(x=x, y=y, z=z, mode='text',
                            text = [self.non_solvent_name, self.solvent_name, self.z_name, self.polymer_name],
                            textfont_size=15, )
        self.fig.add_trace(axlabel)

    def scatter(self, polymer, non_solvent, z, name: str = "", color: str = "red", size: int = 4):
        scat = Scatter3d(x=non_solvent, y=polymer, z=z, mode='markers',
                         marker=dict(size=size, color=color), name = name)
        self.fig.add_trace(scat)

    def saveHTML(self, filepath: str = "./graph.html"):
        plotly.offline.plot(self.fig, filename=filepath, auto_open=False)

if __name__ == "__main__":
    data = pd.DataFrame([[0.1, 0.2, 0.7],
                         [0.05, 0.25, 0.7],
                         [0.15, 0.45, 0.4]], columns=["poly", "sol", "nsol"])
    # figオブジェクトの初期化
    fig = plotly.graph_objs.Figure()
    tp = TriPrism(fig)
    tp.scatter(data["poly"], data["nsol"], pd.Series([0 for i in range(len(data["sol"]))]))

    tp.saveHTML()