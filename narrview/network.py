from email.generator import Generator
from msilib.schema import Error
import os
import difflib
from platform import node
from turtle import pos, width
import pandas as pd
import networkx as nx
from pathy import importlib
import plotly.graph_objects as go
from IPython.display import display
from dataclasses import dataclass
from itertools import permutations
from typing import List


@dataclass
class Edge:
    speaker: str
    addressee: str
    text: str
    weight: int


def format_string_list(str_list: list) -> str:
    out_str = '<br>'
    for s in str_list:
        out_str += s[:50]
        if len(s) > 50:
            out_str += '[...]'
        out_str += '<br>'

    return out_str


def get_edges(
        corpus: str = 'Novellas',
        text: str = '1810-kohlhaas',
        network_annotations: str = 'character_speech',
        start_point: float = 0,
        end_point: int = 1.0):

    speech_data = pd.read_json(
        f'Annotations{corpus}/{text}_embedded_narrations.json')

    # filter by start and end point
    max_end_point = max(speech_data.end_point)
    start_point_filter = start_point * max_end_point
    end_point_filter = end_point * max_end_point
    speech_data = speech_data[
        (speech_data.start_point >= start_point_filter) &
        (speech_data.start_point <= end_point_filter)
    ]

    # filter by annotation type
    if network_annotations == 'character_speech':
        if corpus == 'Dramas':
            raise ValueError(
                'For the dramas only networks based on embedded narrations are possible.')
        else:
            speech_data = speech_data[
                speech_data.tag.isin(
                    [
                        'direct_speech',
                        'indirect_speech',
                        'narrated_character_speech'
                    ]
                )
            ].copy()
    elif network_annotations == 'embedded_narrations':
        speech_data = speech_data[
            speech_data.tag.isin(
                [
                    'secondary_narration',
                    'tertiary_narration',
                ]
            )
        ].copy()
    else:
        raise ValueError(
            "You didn't choose a valid annotation type.\
            Choose either 'character_speech' or 'embedded_narrations' as network_annotations"
        )

    # create edge dict for edge weights
    edge_dict = {}
    for _, row in speech_data[:-1].iterrows():
        speakers = row['prop:speaker']
        addressees = row['prop:addressee']
        for speaker in speakers:
            for addressee in addressees:
                edge_id = f'{speaker}->{addressee}'  # create edge identifier
                if edge_id in edge_dict:
                    edge_dict[edge_id]['weight'] += 1
                    edge_dict[edge_id]['text'].append(row['annotation'])
                    edge_dict[edge_id]['start_point'].append(
                        row['start_point'])
                else:
                    edge_dict[edge_id] = {
                        'weight': 1,
                        'text': [row['annotation']],
                        'start_point': [row['start_point']]
                    }

    # yield edges as Edge objects
    for edge in edge_dict:
        speaker, addressee = edge.split('->')       # split by edge identifier
        yield Edge(
            speaker=speaker,
            addressee=addressee,
            text=format_string_list(edge_dict[edge]['text']),
            weight=edge_dict[edge]['weight'],

        )


def create_network_from_edges(edges: List[Edge]) -> nx.DiGraph:
    di_graph = nx.DiGraph()
    di_graph.add_weighted_edges_from(
        [
            (edge.speaker, edge.addressee, edge.weight)
            for edge in edges
        ]
    )
    return di_graph


def speaker_point(p1_x, p1_y, p2_x, p2_y, distance: float = 0.1):
    return ((1 - distance) * p1_x + distance * p2_x), ((1 - distance) * p1_y + distance * p2_y)


def speaker_addressee_str(edge) -> str:
    return f"{edge.speaker} → {edge.addressee}"


def format_network_stats(stats_df: pd.DataFrame, character: str) -> str:
    stats_html_string = f'{character.upper().replace("_", " ")}<br>'
    for key in dict(stats_df.loc[character]):
        stats_html_string += '<b>' + key.upper() + '</b>' + ' = '
        stats_html_string += str(dict(stats_df.loc[character])[key]) + '<br>'
    return stats_html_string


def get_node_data(
        pos_dict: dict,
        speaker_size_dict: dict,
        node_factor: int,
        node_alpha: int,
        stats: pd.DataFrame):
    speakers = list(speaker_size_dict)
    x_positions = [pos_dict[speaker][0] for speaker in speakers]
    y_positions = [pos_dict[speaker][1] for speaker in speakers]
    marker_sizes = [speaker_size_dict[speaker] *
                    node_factor + node_alpha for speaker in speakers]
    node_label = [speaker.upper().replace('_', ' ')
                  for speaker in speakers]
    hover_text = [
        format_network_stats(
            stats_df=stats,
            character=speaker)
        for speaker in speakers
    ]

    return {
        'x_pos': x_positions,
        'y_pos': y_positions,
        'marker_size': marker_sizes,
        'node_label': node_label,
        'hover_text': hover_text
    }


class Network:
    def __init__(
            self,
            corpus: str = 'Novellas',
            text: str = '1810-kohlhaas',
            network_annotations: str = 'character_speech',
            start_point: float = 0,
            end_point: int = 1.0,
            network_layout: callable = nx.drawing.layout.kamada_kawai_layout):
        """Network class to create a networkx graph from annotations.

        Args:
            corpus (str, optional): 'Novellas' or 'Dramas'. Defaults to 'Novellas'.
            text (str, optional): The texts short titles as they can be found in both corpus folders. Defaults to '1810-kohlhaas'.
            network_annotations (str, optional): 'character_speech' or 'embedded_narrations'. Defaults to 'character_speech'.
            start_point (float, optional): Which text parts should be included. Defaults  to 0.
            end_point (int, optional): Which text parts should be included. Defaults to 1.0.
            network_layout (callable, optional): A [networkx layout function](https://networkx.org/documentation/stable/reference/drawing.html). Defaults to nx.drawing.layout.kamada_kawai_layout.
        """

        self.text = text
        self.edges = list(
            get_edges(
                corpus=corpus,
                text=text,
                network_annotations=network_annotations,
                start_point=start_point,
                end_point=end_point
            )
        )
        self.network_graph = create_network_from_edges(
            edges=self.edges)

        self.pos = network_layout(self.network_graph, weight=None)

    def stats(self) -> pd.DataFrame:
        bc = nx.betweenness_centrality(self.network_graph, normalized=True)
        bc_weighted = nx.betweenness_centrality(
            self.network_graph, normalized=True, weight='weight')
        pr = nx.pagerank(self.network_graph)
        pr_weighted = nx.pagerank(self.network_graph, weight='weight')
        degree = self.network_graph.degree()
        indegree = self.network_graph.in_degree()
        weighted_indegree = self.network_graph.in_degree(weight='weight')
        outdegree = self.network_graph.out_degree()
        weighted_outdegree = self.network_graph.out_degree(weight='weight')

        network_df = pd.DataFrame(
            {
                'degree': dict(degree),
                'indegree': dict(indegree),
                'weighted_indegree': dict(weighted_indegree),
                'outdegree': dict(outdegree),
                'weighted_outdegree': dict(weighted_outdegree),
                'betweenness': dict(bc),
                'betweenness_weighted': dict(bc_weighted),
                'pagerank': dict(pr),
                'pagerank_weighted': dict(pr_weighted),
            }
        )

        network_df = network_df[network_df.degree > 0]
        return network_df.sort_values(by='betweenness', ascending=False).fillna(value=0)

    def plot(
            self,
            node_size: str = 'betweenness',
            node_factor: float = 100.0,
            node_alpha: int = 3,
            plot_stats: bool = True,
            print_title: bool = False):
        """Plots network as plotly graph.

        Args:
            node_size (str, optional): Which network metric to use as node size. Defaults to 'betweenness'.
            node_factor (float, optional): Customize the node size. Defaults to 100.0.
            node_alpha (int, optional): Minimal node size. Defaults to 3.
            plot_stats (bool, optional): Whether to plot the stats as `pandas.DataFrame`. Defaults to True.
            print_title (bool, optional): Whether to plot the title of the plottet Text. Defaults to False.
        """

        def norm_col(value: float, values: pd.Series) -> float:
            return value / sum(values)

        plot_edges = self.edges
        stats = self.stats()
        speaker_size = dict(
            stats[node_size].apply(
                norm_col,
                args=(stats[node_size],)
            )
        )

        fig = go.Figure()
        legend_groups = []
        edge_weight_sum = sum([edge.weight for edge in plot_edges])
        for edge in plot_edges:
            lg = speaker_addressee_str(edge)
            speaker_coordinates = speaker_point(
                p1_x=self.pos[edge.addressee][0],
                p1_y=self.pos[edge.addressee][1],
                p2_x=self.pos[edge.speaker][0],
                p2_y=self.pos[edge.speaker][1],
                distance=0.03
            )
            addressee_coordinates = speaker_point(
                p1_x=self.pos[edge.addressee][0],
                p1_y=self.pos[edge.addressee][1],
                p2_x=self.pos[edge.speaker][0],
                p2_y=self.pos[edge.speaker][1],
                distance=0.97
            )
            # plot edges
            fig.add_annotation(
                x=speaker_coordinates[0],  # arrows' head
                y=speaker_coordinates[1],  # arrows' head
                ax=addressee_coordinates[0],  # arrows' tail
                ay=addressee_coordinates[1],  # arrows' tail
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                text='',  # if you want only the arrow
                showarrow=True,
                arrowhead=4,
                arrowsize=0.6,
                arrowwidth=edge.weight / edge_weight_sum * 100 + 1,
                arrowcolor='grey',
                opacity=0.3
            )
            legend_groups.append(lg)

            # plot hovertext per edge
            hover_pos = speaker_point(
                p1_x=self.pos[edge.speaker][0],
                p1_y=self.pos[edge.speaker][1],
                p2_x=self.pos[edge.addressee][0],
                p2_y=self.pos[edge.addressee][1]
            )
            if len(edge.text) > 500:
                edge.text = edge.text[:500] + '<br>[...]'
            fig.add_trace(
                go.Scatter(
                    x=[hover_pos[0]],
                    y=[hover_pos[1]],
                    mode='markers',
                    marker_symbol='cross-thin',
                    name=lg,
                    text=f"<b>{lg}</b>:<br>{edge.text}",
                    marker=dict(
                        color='grey',
                        opacity=0.4,
                        size=edge.weight / edge_weight_sum * 100 + 1
                    ),
                    showlegend=False,
                    hoverinfo='text'
                )
            )

        # plot nodes
        node_data = get_node_data(
            pos_dict=self.pos,
            speaker_size_dict=speaker_size,
            node_factor=node_factor,
            node_alpha=node_alpha,
            stats=stats
        )
        fig.add_trace(
            go.Scatter(
                x=node_data['x_pos'],
                y=node_data['y_pos'],
                marker={
                    'size': node_data['marker_size'],
                    'color': 'black',
                    'opacity': 0.65
                },
                text=node_data['hover_text'],
                textposition='top center',
                mode='markers',
                showlegend=False,
                hoverinfo='text',
                textfont_size=node_data['marker_size']
            )
        )
        fig.add_trace(
            go.Scatter(
                x=node_data['x_pos'],
                y=node_data['y_pos'],
                opacity=1,
                marker={
                    'size': node_data['marker_size'],
                    'color': 'black',
                    'opacity': 0.65
                },
                text=node_data['node_label'],
                textposition='top center',
                mode='text',
                showlegend=False,
                hoverinfo='text',
                textfont_size=node_data['marker_size']
            )
        )

        fig.update_layout(
            template="simple_white",
            xaxis={'ticks': '', 'showticklabels': False,
                   'showgrid': False, 'visible': False},
            yaxis={'ticks': '', 'showticklabels': False,
                   'showgrid': False, 'visible': False},
            height=600,
            width=1000,
            title=f'NETWORK GRAPH FOR {self.text}' if print_title else None
        )

        fig.show()

        if plot_stats:
            display(stats.head(5))


if __name__ == '__main__':
    pass
