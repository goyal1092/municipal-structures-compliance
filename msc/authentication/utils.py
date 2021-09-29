from msc.authentication.models import Share



def get_sharers(questionnaire):
	return Share.objects.filter(
        target_object_id=questionnaire.id,
        target_content_type__model="questionnaire",
        sharer_content_type__model="organisation",
    ).values_list("sharer_object_id", flat=True)