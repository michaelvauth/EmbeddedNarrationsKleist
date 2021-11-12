import os
import pandas as pd
import plotly.express as px


def format_annotation_text(text: str) -> str:
    while '  ' in text:
        text = text.replace('  ', ' ')

    text_list = text.split(' ')
    output_string = "<I><br>"
    for item in range(0, 60, 10):
        output_string += ' '.join(text_list[item: item + 10]) + '<br>'

    if len(text_list) > 60:
        output_string += '[...]'

    output_string += "</I>"

    return output_string


def split_by_prop(df: pd.DataFrame, prop: str = 'prop:character_speech') -> pd.DataFrame:
    output_list = []
    for _, row in df.iterrows():
        row_dict = dict(row)
        for item in row[prop]:
            row_dict[prop] = item
            output_list.append(row_dict)

    return pd.DataFrame(output_list)


def subcorpus_scatter(
        corpus: str = 'Novellas',
        tags: list = ['secondary_narration'],
        color_column: str = 'prop:speech_representation',):

    sum_df = pd.DataFrame()
    for file in os.listdir(f'Annotations{corpus}/'):
        loaded_df = pd.read_json(f'Annotations{corpus}/{file}')
        sum_df = sum_df.append(
            loaded_df[loaded_df['tag'].isin(tags)],
            ignore_index=True
        )

    sum_df['size'] = sum_df['end_point'] - sum_df['start_point']
    sum_df['Annotation'] = [format_annotation_text(
        an) for an in sum_df['annotation']]
    if 'prop:' in color_column:
        sum_df = split_by_prop(
            df=sum_df,
            prop=color_column
        )

    title_tags = [f'<{tag}>' for tag in tags]
    fig = px.scatter(
        sum_df,
        y='document',
        x='start_point',
        color=color_column,
        size='size',
        hover_data=['Annotation'],
        title=f'{", ".join(title_tags)} in Kleist\'s {corpus}',
        marginal_x='histogram',
        marginal_y='histogram'
    )

    return fig


def single_text_scatter(
        subcorpus: str = 'Dramas',
        text: str = '1807-penthesilea',
        tags: list = ['secondary_narration'],
        y_column: str = 'prop:speaker',
        color_column: str = 'prop:relation_narrator-event_time'):

    sum_df = pd.read_json(
        f'Annotations{subcorpus}/{text}_embedded_narrations.json')
    sum_df['size'] = sum_df['end_point'] - sum_df['start_point']
    sum_df['Annotation'] = [format_annotation_text(
        an) for an in sum_df['annotation']]

    if 'prop:' in color_column:
        sum_df = split_by_prop(
            df=sum_df,
            prop=color_column
        )

    if 'prop:' in y_column:
        sum_df = split_by_prop(
            df=sum_df,
            prop=y_column
        )

    title_tags = [f'<{tag}>' for tag in tags]
    height = len(sum_df[y_column].unique()) * \
        30 if len(sum_df[y_column].unique()) > 10 else 500
    fig = px.scatter(
        sum_df,
        y=y_column,
        x='start_point',
        color=color_column,
        size='size',
        hover_data=['Annotation'],
        title=f'{", ".join(tags)} in Kleist\'s {text.upper()}',
        marginal_x='histogram',
        marginal_y='histogram',
        height=height
    )

    return fig
