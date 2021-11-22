from django.conf import settings


def validate_question_response(question, value):

    input_type = question.input_type
    is_valid, msg, value = validate_response_type(
        input_type, value
    )
    validations = question.options.get("validations", None)
    if validations:
        for validation, val in validations.items():
            func_name = f'validate_{validation}'
            try:
                is_valid, msg = getattr(
                    ValidateQuestionResponse, func_name
                )(val, value)
            except AttributeError:
                continue

    if "choices" in question.options:
        is_valid, msg = getattr(
            ValidateQuestionResponse,
            "validate_choices"
        )(value, question.options["choices"], input_type)

    return is_valid, msg, value

def validate_response_type(input_type, value):
    if input_type not in settings.DEFAULT_INPUT_OPTIONS:
        return False, "Invalid question", value

    response_type = settings.DEFAULT_INPUT_OPTIONS[input_type].get(
        "response_type", "str"
    )
    if response_type == "int":
        try:
            value = int(value)
        except ValueError:
            return False, 'Invalid response type', value

    elif response_type == "list":
        if not isinstance(value, list):
            return False, 'Invalid response type', value
    else:
        value = str(value).strip()

    return True, '', value


class ValidateQuestionResponse:
    @classmethod
    def validate_min(self, value, response):
        if response < value:
            message = f'Value should not be less than {value}'
            return False, message

        return True, ''

    @classmethod
    def validate_max(self, value, response):
        if response > value:
            message = f'Value should not be less than {value}'
            return False, message
        return  True, ''

    @classmethod
    def validate_choices(self, response, choices, input_type):

        if input_type in ["radio", "dropdown"]:
            if response not in choices:
                return False, "Please select a valid choice"

        elif input_type == "checkbox":
            for r in response:
                if r not in choices:
                    return False, "Please select a valid choice"

        return  True, ''
    