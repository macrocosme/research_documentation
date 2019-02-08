"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

import re
from bokeh import events

from bokeh.embed import components
from bokeh.models import BoxZoomTool, ResetTool, CustomJS, WheelZoomTool, PanTool, LassoSelectTool, ColumnDataSource, \
    Patch
from bokeh.plotting import figure

from alert_web.models import (
    Survey, SurveyQuestion, SurveyElement,
    Question, QuestionOption, QuestionResponse, QuestionDrawnResponse,
    ImageStore, Galaxy
)
from alert_web.utility import constants
from alert_web.forms.survey.question import Question as Sq
from alert_web.utility.constants import display_image_size
from alert_web.utility.acton_api import (
    initialise_labels_for_two_predictors, predict_and_combine, get_recommendations,
    get_recommendations_from_file, get_user_labels_for_two_predictors, CSV_COMBINED_LATEST
)
from alert_web.utility.first_images import construct_image_url
from alert_web.utility.tgss_images import construct_tgss_url


class ClassifyObject:
    """Class to classify an object (e.g. galaxy)
    """
    questions = []
    divs = []
    scripts = []
    visited = False

    def __init__(self, questions, divs, scripts, visited):
        self.questions = questions
        self.divs = divs
        self.scripts = scripts
        self.visited = visited


def get_bokeh_image(url):
    """Image to be rendered with bokeh and it is not selectable using lasso tool

    Parameters
    ----------
    url: url of the image
    """
    tools = [
        BoxZoomTool(),
        WheelZoomTool(),
        PanTool(),
        ResetTool(),
    ]

    # constructing bokeh figure
    plot = figure(
        x_range=(0, 1),
        y_range=(0, 1),
        width=display_image_size,
        height=display_image_size,
        logo=None,
        tools=tools,
    )

    # adding image to the figure
    plot.image_url(
        url=[url], x=0, y=0, w=1, h=1, anchor="bottom_left",
    )

    plot.axis.visible = False
    plot.background_fill_color = "#000000"
    plot.background_fill_alpha = 0.8
    plot.grid.grid_line_color = None

    script, div = components(plot)
    return script, div


def get_bokeh_image_selectable(url, field_name, pre_filled=None):
    """Get images to be rendered with bokeh

    Parameters
    ----------
    url: url of the image
    field_name: javscript field name where the number of drawn objects would be shown
    pre_filled: coordinates of any previously selected objects
    """
    if not pre_filled:
        x = []
        y = []
    else:
        x = pre_filled['x']
        y = pre_filled['y']

    # callback for LassoSelectTool
    source = ColumnDataSource(data=dict(x=x, y=y))
    callback = CustomJS(args=dict(source=source), code="""
        // get data source from Callback args
        var data = source.data;
        
        // getting the geometry from cb_data parameter of Callback
        var geometry = cb_data['geometry'];
        
        // pushing Selected portions x, y coordinates for drawing border
        for (i=0; i < geometry.x.length; i++) {
            data['x'].push(geometry.x[i]);
            data['y'].push(geometry.y[i]);
        }
        
        // pushing NaN to separate the selected polygon from others
        // this will also be used for detecting how many polygons have been drawn
        data['x'].push(NaN);
        data['y'].push(NaN);
        
        // count number of selections
        var count = 0
        for (i=0; i < data['x'].length; i++) {
            if (isNaN(data['x'][i])) {
                count++;
            }
        }
        
        document.getElementById('field_name_span').innerHTML = count;
        document.getElementById('field_name_data_x').value = data['x'].join(',');
        document.getElementById('field_name_data_y').value = data['y'].join(',');
        
        if (count > 0) {
            document.getElementById('field_name_zero-button').classList.remove('visible');
        }
        
        // emit update of data source
        source.change.emit();
        """.replace('field_name', field_name))

    callback_reset = CustomJS(args=dict(source=source), code="""
        // get data source from Callback args
        var data = source.data;
        
        // getting the double clicked/tapped coordinates
        var clicked_position = cb_obj;
        
        // clearing the lasso select areas on double click/tap on the figure
        var to_change = false;
        if (clicked_position.x >= 0 && clicked_position.x <= 1 && clicked_position.y >= 0 && clicked_position.y <= 1) {
            data['x'] = [];
            data['y'] = [];
            to_change = true;
        }
             
        if (to_change) {
            document.getElementById('field_name_span').innerHTML = 'None';
            document.getElementById('field_name_data_x').value = '';
            document.getElementById('field_name_data_y').value = '';
            document.getElementById('field_name_zero-button').classList.add('visible');
        }
        
        // emit update of data source
        source.change.emit();
        """.replace('field_name', field_name))

    # polygon to reflect selected area via LassoSelectTool
    polygon = Patch(
        x='x',
        y='y',
        fill_alpha=0.0,
        fill_color='#009933',
        line_width=1,
        line_alpha=1.0,
        line_color='#044A7E',
    )

    lasso_select = LassoSelectTool(callback=callback, select_every_mousemove=False)
    box_zoom = BoxZoomTool()
    pan = PanTool()
    wheel_zoom = WheelZoomTool()
    reset = ResetTool()

    tools = [
        box_zoom,
        lasso_select,
        wheel_zoom,
        pan,
        reset,
    ]

    # constructing bokeh figure
    plot = figure(
        x_range=(0, 1),
        y_range=(0, 1),
        width=display_image_size,
        height=display_image_size,
        logo=None,
        tools=tools,
        active_drag=lasso_select,
    )

    # adding image to the figure
    plot.image_url(
        url=[url], x=0, y=0, w=1, h=1, anchor="bottom_left",
    )

    # adding polygon to the figure
    plot.add_glyph(source, polygon, selection_glyph=polygon, nonselection_glyph=polygon)
    # adding reset lasso selected areas on double click/tap
    plot.js_on_event(events.DoubleTap, callback_reset)

    plot.axis.visible = False
    plot.background_fill_color = "#000000"
    plot.background_fill_alpha = 0.8
    plot.grid.grid_line_color = None

    script, div = components(plot)
    return script, div


def store_survey_elements(survey, recom, df_fri, df_frii):
    """Match returned recommentations ids with ObjectCatalog entries

    Parameters
    ----------
    survey: alert_web.models.Survey
    recom: acton.proto.wrappers.Recommendations
    df_fri: pandas.DataFrame
    df_frii: pandas.DataFrame
    """
    #
    for recommendation_id in recom.recommendations:
        try:
            first = df_fri.loc[df_fri['idx'] == recommendation_id, 'first'].item()
        except ValueError:
            first = df_frii.loc[df_frii['idx'] == recommendation_id, 'first'].item()

        # Gather the one question we will use here.
        try:
            galaxy = Galaxy.objects.get(first=first)
        except Galaxy.MultipleObjectsReturned:
            galaxy = Galaxy.objects.filter(first=first)[0]

        question = Question.objects.all()[0]

        # Create survey element
        survey_element, created = SurveyElement.objects.get_or_create(
            galaxy=galaxy,
            question=question,
        )

        # Create survey question for this survey element
        SurveyQuestion.objects.create(survey_element=survey_element, survey=survey)

        save_image(galaxy)


def save_image(galaxy):
    """Check if images are available, if not download and store.

    Parameters
    ----------
    galaxy: alert_web.models.Galaxy
    """
    for database_type in [ImageStore.FIRST, ImageStore.TGSS]:
        try:
            ImageStore.objects.get(galaxy=galaxy, database_type=database_type)
        except ImageStore.DoesNotExist:
            url = construct_tgss_url(ra=galaxy.ra, dec=galaxy.dec) \
                if database_type == ImageStore.TGSS \
                else construct_image_url(ra=galaxy.ra, dec=galaxy.dec, fits=1)

            ImageStore.objects.create(
                galaxy=galaxy,
                database_type=database_type,
                actual_url=url,
            )


def generate_recommendations_for_survey(survey):
    """Generate recommendations for a specific survey

    Parameters
    -----------
    survey: alert_web.models.Survey
    """
    recom, df_fri, df_frii = get_recommendations_from_file('predictions_survey_%d.pb' % survey.id)

    store_survey_elements(survey, recom, df_fri, df_frii)


def generate_new_survey():
    """
    Generate a new survey
    """

    previous_survey = Survey.objects.filter(active=True).order_by('-creation_date').first()

    # Create a survey
    survey = Survey()
    survey.save()

    # Get FR-I/B FR-II/B labels and train a predictor
    if not previous_survey:
        labels_fr_i, labels_fr_ii = initialise_labels_for_two_predictors()
        pred = predict_and_combine(labels_1=labels_fr_i,
                                   labels_2=labels_fr_ii,
                                   predictor='LogisticRegression',
                                   output_file='predictions_survey_%d.pb' % survey.id)
    else:
        labels_fr_i, labels_fr_ii = get_user_labels_for_two_predictors()
        pred = predict_and_combine(labels_1=labels_fr_i,
                                   labels_2=labels_fr_ii,
                                   predictor='LogisticRegression',
                                   output_file='predictions_survey_%d.pb' % survey.id,
                                   csv_file=CSV_COMBINED_LATEST)

    # Get recommendations from predictor
    recom, df_fri, df_frii = get_recommendations(pred)

    # Store predictions as survey elements
    store_survey_elements(survey, recom, df_fri, df_frii)

    # Set new survey as active
    survey.active = True
    survey.save()

    return survey


def get_next_survey_objects(survey_id, start_index=0, response=None):
    """Returns the next set of questions

    Parameters
    ----------
    survey_id:
        Id of the survey
    start_index:
        index from where the questions will start
    response:
        response object of the database model

    Returns
    -------
    survey_objects:
        list of survey objects
    """
    survey = Survey.objects.get(id=survey_id)

    survey_questions = SurveyQuestion.objects.filter(survey=survey)[
                       start_index:start_index + constants.SURVEY_QUESTIONS_PER_PAGE]

    survey_objects = []

    for survey_question in survey_questions:
        visited = False
        galaxy = survey_question.survey_element.galaxy

        # get question choices
        options = QuestionOption.objects.filter(question=survey_question.survey_element.question)

        choices = []
        default_choice = None
        comments_initial = None
        for option in options:
            choices.append((option.option, option.option))
            if option.is_default_option:
                default_choice = option.option

        # overriding the default with provided answers if any
        try:
            question_response = QuestionResponse.objects.get(
                response=response,
                survey_question=survey_question,
            )
            default_choice = question_response.answer
            comments_initial = question_response.comments
            visited = True
        except QuestionResponse.DoesNotExist:
            pass

        # radio question
        q = Sq(
            name=constants.FORM_QUESTION_PREFIX + survey_question.id.__str__(),
            label=survey_question.survey_element.question.text,
            choices=tuple(choices),
            initial=default_choice,
            question_type=survey_question.survey_element.question.category,
        )

        # text question
        q_text = Sq(
            name=constants.FORM_QUESTION_PREFIX + survey_question.id.__str__() + '_comments',
            label='',
            question_type='text',
            placeholder='Enter extra comments here',
            initial=comments_initial,
        )

        # getting images for this survey question
        image_stores = ImageStore.objects.filter(galaxy=galaxy)
        divs = []
        scripts = []
        for index, image_store in enumerate(image_stores):
            try:
                question_drawn_response = QuestionDrawnResponse.objects.get(
                    response=response,
                    survey_question=survey_question,
                )
                x_coordinates = question_drawn_response.x_coordinates
                y_coordinates = question_drawn_response.y_coordinates
                pre_filled = dict(
                    x=x_coordinates.split(',') if x_coordinates.count('NaN') > 0 else [],
                    y=y_coordinates.split(',') if y_coordinates.count('NaN') > 0 else [],
                )
                number_of_objects = question_drawn_response.x_coordinates.count('NaN')
            except QuestionDrawnResponse.DoesNotExist:
                x_coordinates = ''
                y_coordinates = ''
                pre_filled = dict(
                    x=[],
                    y=[],
                )
                number_of_objects = 'None'

            if image_store.database_type == ImageStore.FIRST and 'no_image' not in image_store.image:
                field_name = constants.FORM_QUESTION_PREFIX + survey_question.id.__str__() \
                             + '_' + image_store.database_type.__str__()

                script, div = get_bokeh_image_selectable(
                    url='/' + image_store.image,
                    field_name=field_name,
                    pre_filled=pre_filled,
                )

                divs.append(
                    [
                        div,
                        galaxy,
                        field_name,
                        number_of_objects,
                        x_coordinates,
                        y_coordinates,
                    ]
                )

            else:
                script, div = get_bokeh_image(
                    url='/' + image_store.image
                )

                divs.append(
                    [
                        div,
                        galaxy,
                    ]
                )

            scripts.append(script)

        survey_objects.append(ClassifyObject(
            questions=[q, q_text, ],
            divs=divs,
            scripts=scripts,
            visited=visited,
        ))

    return survey_objects


def save_answers(request, response):
    """Save user's answers

    Parameters
    ----------
    request:
        POST request
    response:
        response object of the database model
    """
    # pattern for questions
    pattern_question = constants.FORM_QUESTION_PREFIX + '\d+$'
    # pattern for comments
    pattern_comments = constants.FORM_QUESTION_PREFIX + '\d+_comments$'
    # pattern for image selected areas
    pattern_selected_area = constants.FORM_QUESTION_PREFIX + '\d+_[a-zA-Z0-9_]+$'

    for key in request.POST:
        if re.match(pattern_question, key):
            answer = request.POST[key]
            survey_question = SurveyQuestion.objects.get(id=key.replace(constants.FORM_QUESTION_PREFIX, ''))

            QuestionResponse.objects.update_or_create(
                survey_question=survey_question,
                response=response,
                defaults={
                    'answer': answer,
                }
            )
        elif re.match(pattern_comments, key):  # this must be checked before the selected area, or will match there
            comments = request.POST[key]
            survey_question = SurveyQuestion.objects.get(
                id=key.replace(constants.FORM_QUESTION_PREFIX, '').split('_')[0])

            qr, created = QuestionResponse.objects.get_or_create(
                survey_question=survey_question,
                response=response,
            )
            qr.comments = comments
            qr.save()

        elif re.match(pattern_selected_area, key):
            # save answers for selected areas
            # finding id of the survey question
            split_content = key.replace(constants.FORM_QUESTION_PREFIX, '').split('_')
            survey_question_id = split_content[0]
            image_database_type = split_content[1]
            if image_database_type != ImageStore.FIRST:  # skip saving coordinates for other images
                continue

            coordinate = split_content[-1]

            survey_question = SurveyQuestion.objects.get(id=survey_question_id)
            # updating the answer
            if coordinate == 'x':
                QuestionDrawnResponse.objects.update_or_create(
                    survey_question=survey_question,
                    response=response,
                    defaults={
                        'x_coordinates': request.POST[key],
                    }
                )
            elif coordinate == 'y':
                QuestionDrawnResponse.objects.update_or_create(
                    survey_question=survey_question,
                    response=response,
                    defaults={
                        'y_coordinates': request.POST[key],
                    }
                )
