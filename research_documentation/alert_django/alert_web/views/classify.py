"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from alert_web.models import (
    Survey, SurveyQuestion, Response, QuestionResponse
)
from alert_web.utility import constants
from alert_web.utility.plots import get_plots
from alert_web.utility.survey import (
    get_next_survey_objects, save_answers, generate_recommendations_for_survey
)

from alert_celery.tasks import add_more_survey_objects
from alert_celery.utility import add_more_objects_to_survey_in_progress


@login_required
def classify(request):
    """Handles the request to process inputs and render classify page

    Parameters
    request:
        django.shortcuts.request (a page to be rendered)

    Returns
    -------
    render:
        django.shortcuts.render (rendered template)
    """

    next_action = None

    if request.method != 'POST':
        start_index = 0

        active_response = Response.objects.filter(
            user=request.user,
            status=Response.ACTIVE,
        ).first()

        if active_response:
            start_index = QuestionResponse.objects.filter(response=active_response).count()

        latest_survey = Survey.objects.filter(active=True).order_by('-creation_date').first()

        if active_response and latest_survey != active_response.survey:  # unfinished old survey found
            # show the intermediate page
            request.session['survey_id'] = active_response.survey.id
            next_action = 'Outdated'
            return render(
                request,
                'classify/intermediate.html',
                {
                    'next_action': next_action,
                    'latest_survey': latest_survey,
                    # once posted from intermediate page the start index would be updated automatically, so it is
                    # required to get it reduced
                    'start_index': start_index - constants.SURVEY_QUESTIONS_PER_PAGE,
                }
            )

        try:
            # setting the survey to the latest
            request.session['survey_id'] = latest_survey.id
            survey = latest_survey
        except AttributeError:
            # No survey exists yet. We'll let an admin deal with it!
            # We just inform the user that there is no current survey to work on.
            return render(
                request,
                'classify/no-survey-yet.html',
                {
                    'user': request.user,
                }
            )

        try:
            response = Response.objects.get(
                user=request.user,
                survey=survey,
            )
        except Response.DoesNotExist:
            response = None
    else:
        start_index = request.POST.get('start_index')
        survey = Survey.objects.get(id=request.session['survey_id'])
        # create a new response if it is not there
        response, created = Response.objects.get_or_create(
            user=request.user,
            survey=survey,
        )

        next_action = request.POST.get('next_action', None)

        if not next_action:  # have come from original_page
            from_page = 'original'
            next_action = request.POST.get('action_type', None)
            if not next_action:  # no action_type present, means back
                next_action = 'Back'
        else:
            from_page = 'intermediate'

        if next_action == 'Back':
            start_index = max(int(start_index) - constants.SURVEY_QUESTIONS_PER_PAGE, 0)
        else:
            # checking out for available latest surveys
            if from_page != 'intermediate':  # do not check it if coming from intermediate page
                # saving the answers for the questions
                save_answers(request, response)

                latest_survey = Survey.objects.filter(active=True).order_by('-creation_date').first()

                # checking if this is the last page
                if next_action == 'Finish':
                    # setting the survey as finished
                    response.status = Response.FINISHED
                    response.save()

                    # redirecting to thank you page
                    return render(
                        request,
                        'classify/completed.html',
                        {
                            'user': request.user,
                            'latest_survey': latest_survey
                            if request.session['survey_id'] != latest_survey.id else None,
                            'current_survey': Survey.objects.get(id=request.session['survey_id']),
                        }
                    )

                if latest_survey.id != request.session['survey_id']:
                    # bring up the intermediate page
                    return render(
                        request,
                        'classify/intermediate.html',
                        {
                            'next_action': next_action,
                            'latest_survey': latest_survey,
                            'start_index': start_index,
                        }
                    )
            else:  # it has come from intermediate page

                # redirect to the classify page if latest is required
                if request.POST.get('submit', None) == 'Latest':
                    # mark the current survey as finished
                    response.status = Response.FINISHED
                    response.save()
                    return redirect(reverse('classify'))

            # update the start index
            start_index = int(start_index) + constants.SURVEY_QUESTIONS_PER_PAGE

        if next_action == 'More!':
            generate_recommendations_for_survey(survey)

    # setting the text for the forward button
    submit_text = 'Save and Next'
    total = SurveyQuestion.objects.filter(survey=survey).count()

    if start_index + constants.SURVEY_QUESTIONS_PER_PAGE >= total:
        submit_text = 'More!'

    plots = get_plots(request)

    progress = int((start_index / total) * 100)

    # this will automatically fires more action recommendation as user approaches to the end of a survey
    if next_action != 'Back' and start_index >= total - \
            int(constants.NUMBER_OF_ACTON_RECOMMENDATION * constants.TRIGGER_MORE_QUESTION_WHEN_REMAINING_PERCENTAGE) \
            and not add_more_objects_to_survey_in_progress(survey):
        add_more_survey_objects.delay(survey_id=survey.id, username=request.user.username)

    survey_objects = get_next_survey_objects(
        survey_id=request.session['survey_id'],
        start_index=start_index,
        response=response,
    )

    return render(
        request,
        'classify/classify.html',
        {
            'rows': survey_objects,
            'plots': plots,
            'start_index': start_index,
            'submit_text': submit_text,
            'first_page': True if start_index == 0 else False,
            'labelled': start_index,
            'total': total - start_index,
            'progress': progress,
            'remaining': 100 - progress,
        }
    )
