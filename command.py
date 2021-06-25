import json
from discord_slash.model import *


class Command:
    def __init__(self, name, description, choices=[]):
        if (len(name) > 32):
            self.name = name[:32]
        else:
            self.name = name
        if (len(description) > 100):
            self.description = description[:100]
        else:
            self.description = description
        # self.options = [OptionData("Search", "Search specific commands", choices=choices, type=3)]
        self.options = [{"name": "search", "description": "Search specific commands", "choices": [], "type": 3}]

    def addChoice(self, name):
        if (len(name) > 100):
            nameUse = name[:100]
        else:
            nameUse = name
        self.options[0]["choices"].append(
            {
                "name": nameUse,
                "value": nameUse
            })
        print(self.options[0]["choices"])

        # def toJson(self, dump=True):
        #     optionsJson = []
        #     for o in self.options:
        #         optionsJson.append(o.toJson(dump=False))
        #         retvar = {"name": self.name,
        #                   "description": self.description,
        #                   "options": optionsJson
        #                   }
        #     if (dump):
        #         return json.dumps(retvar)
        #     return retvar
        #
        # def optionsJson(self):
        #     optionsJson = []
        #     for o in self.options:
        #         optionsJson.append(o.toJson(dump=False))
        #     return optionsJson

        # def __str__(self):
        #     return self.toJson()


class CommandOption(json.JSONEncoder):
    def __init__(self, name, description, type=1, required=False, choices=[], options=[]):
        if (len(name) > 32):
            self.name = name[:32]
        else:
            self.name = name
        self.type = type
        if (len(description) > 100):
            self.description = description[:100]
        else:
            self.description = description
        self.required = required
        self.choices = choices
        self.options = options

    def toJson(self, dump=True):
        optionsJson = []
        for o in self.options:
            optionsJson.append(o.toJson())
        retvar = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "choices": self.choices,
            "options": optionsJson
        }
        if (dump):
            return json.dumps(retvar)
        return retvar

    def __str__(self):
        return self.toJson()


class OptionEncoder(json.JSONEncoder):
    def default(self, o: CommandOption):
        return o.toJson(dump=False)


class CommandEncoder(json.JSONEncoder):
    def default(self, o: Command):
        return o.toJson()
