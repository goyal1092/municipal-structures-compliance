from django.conf import settings



class ValidateQuestionResponse:

    @classmethod
    def run_validation(self, question, response):

        if not response:
            return { "is_valid": True, "msg": None, "response": response }

        response_type = None
        if "response_type" not in  question.options:
            response_type = settings.DEFAULT_INPUT_OPTIONS[question.input_type]["response_type"]
        else:
            response_type = question.options["response_type"]

        validation = self.validate_response_type(question.options["response_type"], response)
        if not validation["is_valid"]:
            return validation
        response = validation["response"]
        validations = []
        if "validations" in question.options:
            validations = question.options["validations"]

        if not validations:
            return { "is_valid" : True, "msg": None , "response": response}

        for validation, val in validations.items():
            func_name = f"validate_{validation}"
            validation_func = getattr(self, func_name, self.generic_message)
            result = validation_func(val, response)
            if not result["is_valid"]:
                return result

        return {
            "is_valid": True,
            "msg": None,
            "response": response
        }

    @classmethod
    def validate_response_type(self, response_type, response):

        is_valid = True
        if response_type == "int":
            try:
                response = int(response)
            except ValueError:
                is_valid = False

        if response_type == "float":
            try:
                response = float(response)
            except ValueError:
                is_valid = False

        return {
            "is_valid": is_valid,
            "msg": "Invalid response type for the question" if not is_valid else None,
            "response": response
        }


    @classmethod
    def validate_min(self, value, response):
        is_valid = True,
        message = None
        if response < value:
            is_valid = False
            message = f"Value should not be less than {value}"
        return {
            "is_valid": is_valid, "msg": message, "response": response
        }

    @classmethod
    def validate_max(self, value, response):
        is_valid = True,
        message = None
        if response > value:
            is_valid = False
            message = f"Value should not be less than {value}"
        return {
            "is_valid": is_valid, "msg": message, "response": response
        }

    @classmethod
    def generic_message(self, value, response):
        return { "is_valid" : True, "msg": None,  "response": response}