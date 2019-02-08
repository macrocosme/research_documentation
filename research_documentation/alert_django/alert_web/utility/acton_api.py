from acton import acton
import acton.proto
import acton.database
"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from acton.acton import label
from acton.proto.wrappers import Recommendations

from django.conf import settings
from pandas import read_csv, DataFrame, concat
from alert_web.models import (
    Galaxy, Response, QuestionResponse, QuestionOption
)
from alert_web.utility import constants
from alert_web.utility.utils import check_path
from django.db.models import Q

from os.path import isfile

CSV_PATH = check_path(settings.MEDIA_ROOT + 'csv/')
PROTOBUF_PATH = check_path(settings.MEDIA_ROOT + 'database_protobufs/')
CSV_FRI = CSV_PATH + 'fr_i.csv'
CSV_FRII = CSV_PATH + 'fr_ii.csv'
CSV_COMBINED = CSV_PATH + 'combined.csv'
CSV_COMBINED_LATEST = CSV_PATH + 'combined_latest.csv'
FEATURE_COLS = ['fint', 'fpeak', 'rms', 'maj', 'min', 'pa',
                'nn2', 'nn2_angle', 'nn2_fint', 'nn2_fpeak', 'nn2_rms', 'nn2_maj', 'nn2_min',
                'nn3', 'nn3_angle', 'nn3_fint', 'nn3_fpeak', 'nn3_rms', 'nn3_maj', 'nn3_min',
                'nn4', 'nn4_angle', 'nn4_fint', 'nn4_fpeak', 'nn4_rms', 'nn4_maj', 'nn4_min',
                'nn5', 'nn5_angle', 'nn5_fint', 'nn5_fpeak', 'nn5_rms', 'nn5_maj', 'nn5_min',
                'nn6', 'nn6_angle', 'nn6_fint', 'nn6_fpeak', 'nn6_rms', 'nn6_maj', 'nn6_min',
                'nn7', 'nn7_angle', 'nn7_fint', 'nn7_fpeak', 'nn7_rms', 'nn7_maj', 'nn7_min']


def predict_and_combine(
        labels_1: acton.proto.wrappers.LabelPool,
        labels_2: acton.proto.wrappers.LabelPool,
        predictor: str,
        output_file: str,
        csv_file=CSV_COMBINED) -> acton.proto.wrappers.Predictions:
    """Train a predictor and predict labels.

    Parameters
    ----------
    labels_1
        IDs of labelled instances.
    labels_2
        IDs of labelled instances.
    predictor
        Name of predictor to make predictions.
    output_file
        Filename of the protobuf file (.pb)
    csv_file
        The supplied CSV file

    Returns
    -------
        Combined predictors as a prediction protobuf
    """
    from acton.acton import validate_predictor
    import acton.predictors
    import logging
    import numpy as np

    validate_predictor(predictor)

    # First predictor
    with labels_1.DB() as db_1:
        ids_1 = db_1.get_known_instance_ids()
        train_ids_1 = labels_1.ids

        predictor_1 = acton.predictors.PREDICTORS[predictor](db=db_1, n_jobs=-1)

        logging.debug('Training predictor with IDs: {}'.format(train_ids_1))
        predictor_1.fit(train_ids_1)

        predictions_1, _variances_1 = predictor_1.reference_predict(ids_1)

    # Second predictor
    with labels_2.DB() as db_2:
        ids_2 = db_2.get_known_instance_ids()
        train_ids_2 = labels_2.ids

        predictor_2 = acton.predictors.PREDICTORS[predictor](db=db_2, n_jobs=-1)

        logging.debug('Training predictor with IDs: {}'.format(train_ids_2))
        predictor_2.fit(train_ids_2)

        predictions_2, _variances_2 = predictor_2.reference_predict(ids_2)

    # Make predictions from combined predictors
    with acton.database.ASCIIReader(csv_file, feature_cols=FEATURE_COLS, label_col='my_label') as db:
        proto = acton.proto.wrappers.Predictions.make(
            ids_1 + ids_2,
            train_ids_1 + train_ids_2,
            np.append(predictions_1, predictions_2, axis=0).transpose([1, 0, 2]),  # T x N x C -> N x T x C
            predictor=predictor,
            db=db)

    # Bytestring describing this run.
    metadata = '{}'.format(predictor).encode('ascii')
    writer = acton.proto.io.write_protos(PROTOBUF_PATH + output_file, metadata=metadata)
    next(writer)  # Prime the coroutine.
    writer.send(proto.proto)

    return proto


def generate_csvs_from_model():
    """Generate two CSV files based on django's ObjectsCatalog model

    One csv file for FR-I/B objects, and one for FR-II/B objects.
    """
    result_fri = Galaxy.objects.filter(~Q(my_label='II')).values()
    result_fri = result_fri.order_by('?')
    df1 = DataFrame(list(result_fri))
    df1.to_csv(CSV_FRI, index_label='idx', sep=',')
    index_incr = len(df1)

    result_frii = Galaxy.objects.filter(~Q(my_label='I')).values()
    result_frii = result_frii.order_by('?')
    df2 = DataFrame(list(result_frii))
    df2.index += index_incr
    df2.to_csv(CSV_FRII, index_label='idx', sep=',')

    concat([df1, df2]).to_csv(CSV_COMBINED, index_label='idx', sep=',')


def initialise_labels_for_two_predictors(
        n_train: int = 100):
    """Initialise a survey with initial labels using acton.acton.label

    Parameters
    ----------
    n_train: int
        number of initial labels to use (training set?)

    Returns
    -------
    labels_fr_i : protobuf
        Label protobuf for FR-I/B set
    labels_fr_ii : protobuf
        Label protobuf for FR-II/B set
    """

    # Check if csv files exist, else generate them.
    if not (isfile(CSV_COMBINED) and isfile(CSV_FRI) and isfile(CSV_FRII)):
        generate_csvs_from_model()

    # Initial labels.
    recommendation_indices = list(range(n_train))
    with acton.database.ASCIIReader(
            CSV_FRI,
            feature_cols=FEATURE_COLS,
            label_col='my_label') as db:
        recommendations_fr_i = Recommendations.make(
            recommended_ids=recommendation_indices,
            labelled_ids=[],
            recommender='None',
            db=db)

    with acton.database.ASCIIReader(
            CSV_FRII,
            feature_cols=FEATURE_COLS,
            label_col='my_label') as db:
        recommendations_fr_ii = Recommendations.make(
            recommended_ids=recommendation_indices,
            labelled_ids=[],
            recommender='None',
            db=db)

    labels_fr_i = label(recommendations_fr_i)
    labels_fr_ii = label(recommendations_fr_ii)

    return labels_fr_i, labels_fr_ii


def get_user_labels_for_two_predictors():
    """Generate a new predictor from user labels from preview_survey
    """
    question_responses = QuestionResponse.objects.filter(
        response=Response.objects.get(
            status=Response.FINISHED,
        )
    )

    # Gather all user labels to train a new predictor
    ids_fri = []
    ids_frii = []

    if not (isfile(CSV_COMBINED_LATEST)):
        df_all = read_csv(CSV_COMBINED)
    else:
        df_all = read_csv(CSV_COMBINED_LATEST)

    df_fri = read_csv(CSV_FRI)
    df_frii = read_csv(CSV_FRII)

    for response in question_responses:
        label = QuestionOption.objects.get(option=response.answer).option_label

        new_id = len(df_all)
        new_item = df_all.loc[df_all['first'] == response.survey_question.survey_element.galaxy.first].iloc[0]
        new_item['my_label'] = label
        new_item['idx'] = new_id

        df_all = df_all.append(new_item)

        if label == 'I':
            ids_fri.append(new_id)
            df_fri = df_fri.append(new_item)
        if label == 'II':
            ids_frii.append(new_id)
            df_frii = df_frii.append(new_item)
        if label == 'B':
            ids_fri.append(new_id)
            ids_frii.append(new_id)
            df_frii = df_frii.append(new_item)
            df_fri = df_fri.append(new_item)

        response.response.status = Response.PROCESSED
        response.response.save()

    df_all.to_csv(CSV_COMBINED_LATEST, index=False)  # index=False as we already have `idx`
    df_fri.to_csv(CSV_FRI, index=False)  # index=False as we already have `idx`
    df_frii.to_csv(CSV_FRII, index=False)  # index=False as we already have `idx`

    with acton.database.ASCIIReader(CSV_COMBINED_LATEST, feature_cols=FEATURE_COLS, label_col='my_label') as db:
        labels_fr_i = acton.proto.wrappers.LabelPool.make(ids=set(ids_fri), db=db)
        labels_fr_ii = acton.proto.wrappers.LabelPool.make(ids=set(ids_frii), db=db)

    return labels_fr_i, labels_fr_ii


def get_recommendations_from_file(
        filename: str,
        recommender: str = 'RandomRecommender',
        n_recommendations: int = constants.NUMBER_OF_ACTON_RECOMMENDATION):
    """Get recommendation based on a prediction protobuf file

    Parameters
    -----------
    filename : str
        filename of protobuf file (.pb) with path
    recommender: type of recommender
    n_recommendations : int
        Number of recommendations to be generated
    """
    from acton.proto.acton_pb2 import Predictions
    from acton.acton import recommend

    predictions = acton.proto.wrappers.Predictions(
        next(acton.proto.io.read_protos(PROTOBUF_PATH + filename, Predictions))
    )
    recom = recommend(predictions, recommender, n_recommendations=n_recommendations)

    return recom, read_csv(CSV_FRI), read_csv(CSV_FRII)


def get_recommendations(
        predictions: acton.proto.wrappers.Predictions,
        recommender: str = 'RandomRecommender',
        n_recommendations: int = constants.NUMBER_OF_ACTON_RECOMMENDATION):
    """Get recommendation based on a prediction protobuf

    Parameters
    ----------
    predictions : acton.proto.wrappers.Predictions

    recommender: type of recommender

    n_recommendations : int

    Returns
    -------
    recom : recommendation object
        recommendations protobuf
    read_csv(CSV_FRI) : pandas.DataFrame
        FR-I catalog
    read_csv(CSV_FRII) : pandas.DataFrame
        FR-II catalog
    """
    from acton.acton import recommend
    recom = recommend(predictions, recommender, n_recommendations=n_recommendations)

    return recom, read_csv(CSV_FRI), read_csv(CSV_FRII)
