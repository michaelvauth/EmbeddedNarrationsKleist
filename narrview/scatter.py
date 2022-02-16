import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


plays = [
    '1802-schroffenstein', '1806-krug', '1806-amphitryon', '1807-penthesilea',
    '1808-kaethchen', '1808-hermannsschlacht', '1810-homburg'
]
stories = [
    '1807-erdbeben', '1810-kohlhaas', '1811-zweikampf', '1808-marquise',
    '1811-verlobung', '1811-findling', '1810-caecilie'
]


def format_annotation_text(text: str) -> str:
    """Creates HTML string for the annotation text in the scatter plot.

    Args:
        text (str): The annotation string.

    Returns:
        str: The html string.
    """
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
    """Splits a specified property column in annotation dataframes in multiple rows if multiple property values exists.

    Args:
        df (pd.DataFrame): Annotation DataFrame.
        prop (str, optional): [description]. Defaults to 'prop:character_speech'.

    Returns:
        pd.DataFrame: Modiefied DataFrame.
    """
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
        color_column: str = 'prop:speech_representation',) -> None:
    """Plots annotation for the given corpus.

    Args:
        corpus (str, optional): Which corpus to plot. Defaults to 'Novellas'.
        tags (list, optional): A list of all tags to be included in the scatter plot. 'direct_speech', 'indirect_speech',
        'narrated_character_speech', 'secondary_narration' or 'tertiary_narration'. Defaults to ['secondary_narration'].
        color_column (str, optional): Either 'tag', 'prop:informativeness', 'prop:falsification_status'
        or 'prop:relation_narrator-event_time'. Defaults to 'prop:speech_representation'.
    """
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


def get_text_part(annotation_df: pd.DataFrame, sp: float = 0, ep: float = 1) -> pd. DataFrame:
    max_end_point = max(annotation_df.end_point)
    abs_start_point = sp * max_end_point
    abs_end_point = ep * max_end_point
    return annotation_df[
        (annotation_df.start_point >= abs_start_point) &
        (annotation_df.end_point <= abs_end_point)
    ].copy()


def single_text_scatter(
        text: str = '1807-penthesilea',
        tags: list = ['secondary_narration'],
        y_column: str = 'prop:speaker',
        color_column: str = 'prop:relation_narrator-event_time',
        start_point: float = 0,
        end_point: float = 1.0) -> go.Figure:
    """Plot the annotation of a single text as a plotly scatter plot.

    Args:
        subcorpus (str, optional): 'Novellas' or 'Dramas'. Defaults to 'Dramas'.
        text (str, optional): In case you choosed 'Novellas' as corpus: "1807-erdbeben", "1808-marquise", "1810-caecilie", "1810-kohlhaas", "1811-findling", "1811-verlobung", "1811-zweikampf"
            In case you chooses 'Dramas' as corpus: "1802-schroffenstein", "1806-amphitryon", "1806-krug", "1807-penthesilea", "1808-hermannsschlacht", "1808-kaethchen", "1810-homburg". Defaults to '1807-penthesilea'.
        tags (list, optional): A list of all tags to be included in the scatter plot. 'direct_speech', 'indirect_speech',
            'narrated_character_speech', 'secondary_narration' or 'tertiary_narration'. Defaults to ['secondary_narration'].
        y_column (str, optional): Eather the annotations tag or a specified property: 'prop:speaker', 'prop:addressee', 'tag', 'prop:character_speech', 'prop:informativeness', 'prop:falsification_status', 'prop:relation_narrator-event_time'.
            Defaults to 'prop:speaker'.
        color_column (str, optional): Either 'tag', 'prop:informativeness', 'prop:falsification_status'
            or 'prop:relation_narrator-event_time'. Defaults to 'prop:relation_narrator-event_time'.

    Returns:
        [type]: [description]
    """
    if text in stories:
        sum_df = pd.read_json(
            f'AnnotationsNovellas/{text}_embedded_narrations.json')
    elif text in plays:
        sum_df = pd.read_json(
            f'AnnotationsDramas/{text}_embedded_narrations.json')
    else:
        raise ValueError(f'"{text}" is no valid title!')

    sum_df = get_text_part(annotation_df=sum_df, sp=start_point, ep=end_point)

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

    height = (len(sum_df[y_column].unique()) * 30) + 300
    # if len(sum_df[y_column].unique()) > 10 else 1000
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
    )
    fig.update_layout(
        template="simple_white",
        width=1000,
        height=height
    )
    return fig
