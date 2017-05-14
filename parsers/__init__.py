from parsers.skillparser import SkillParser
from parsers.leaderskillparser import LeaderSkillParser
from parsers.extraskillparser import ExtraSkillParser
from parsers.feskillparser import FeSkillParser
from parsers.evoparser import EvoParser
from parsers.itemparser import ItemParser
from parsers.aiparser import AiParser
from parsers.missionparser import MissionParser
from parsers.unitparser import UnitParser


PARSER_DICT = {
    "skill": SkillParser().__class__,
    "leader skill": LeaderSkillParser().__class__,
    "extra skill": ExtraSkillParser().__class__,
    'fe skill': FeSkillParser().__class__,
    'evo': EvoParser().__class__,
    'item': ItemParser().__class__,
    'ai': AiParser().__class__,
    'mission': MissionParser().__class__,
    'unit': UnitParser().__class__
}
