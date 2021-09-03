import string

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Questionnaire
from django.shortcuts import get_object_or_404



@login_required
def questionnaire_list(request):
	"""
	"""
	context = {
		"questionnaires": Questionnaire.objects.filter(is_published=True),
	}
	return render(request, 'questionnaire/list.html', context)



def serialize_question(question, section_no, question_no, is_child=False):
	if is_child:
		question_no = string.ascii_lowercase[question_no]

	sno = f"{section_no}.{question_no}"
	return {
		"sno": sno,
		"text": question.text,
		"input_type": f"question/{question.input_type}.html",
		"instruction": question.instruction,
		"name": question.name,
		"options": question.options,
	}

@login_required
def questionnaire_detail(request, pk):
	"""
	"""
	questionnaire = get_object_or_404(Questionnaire, pk=pk)
	data = []

	sections = questionnaire.section_set.all()

	for idx, section in enumerate(sections):
		subdata = {}
		section_no = idx + 1
		questions = section.question_set.filter(parent__isnull=True)

		serialized_quesions = []
		for qidx, question in enumerate(questions):
			question_no = qidx + 1
			ques_details = serialize_question(question, section_no, question_no)
			child_questions = []
			for cidx, child in enumerate(list(section.question_set.filter(parent=question))):
				child_questions.append(serialize_question(child, ques_details["sno"], cidx, True))

			ques_details["children"] = child_questions
			serialized_quesions.append(ques_details)

		data.append({
			"label": f"Section - {idx+1} {section.label}",
			"questions": serialized_quesions
		})


	context = {
		"questionnaires": Questionnaire.objects.filter(is_published=True),
		"sections": data
	}
	return render(request, 'questionnaire/questionnaire_form.html', context)
