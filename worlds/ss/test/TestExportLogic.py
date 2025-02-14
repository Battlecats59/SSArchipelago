# This is terrible code that should probably never make it into the AP project

from test.bases import WorldTestBase


class BaseRequirement:
    def __str__(self):
        raise NotImplementedError()

    def __and__(self, other):
        if isinstance(other, BaseRequirement):
            return AndRequirement([self, other])
        elif other is True:
            return self
        elif other is False:
            return False
        else:
            raise ValueError()

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        if isinstance(other, BaseRequirement):
            return OrRequirement([self, other])
        elif other is True:
            return True
        elif other is False:
            return self
        else:
            raise ValueError()

    def __ror__(self, other):
        return self & other

    def __invert__(self):
        return NotRequirement(self)


class NotRequirement(BaseRequirement):
    def __init__(self, term):
        self.term = term

    def __str__(self):
        return f"not({self.term})"


class AndRequirement(BaseRequirement):
    def __init__(self, terms):
        self.terms = terms

    def __str__(self):
        return f"({' and '.join(str(t) for t in self.terms)})"


class OrRequirement(BaseRequirement):
    def __init__(self, terms):
        self.terms = terms

    def __str__(self):
        return f"({' or '.join(str(t) for t in self.terms)})"


class ItemCountRequirement(BaseRequirement):
    def __init__(self, item, count):
        self.item = item
        self.count = count

    def __str__(self):
        return f"count({self.item}, {self.count})"


class CanReachRegionRequirement(BaseRequirement):
    def __init__(self, region):
        self.region = region

    def __str__(self):
        return f"can_reach({self.region})"


class BaseOption(BaseRequirement):
    def __init__(self, option):
        self.option = option

    def __str__(self):
        return f"option({self.option})"

    def __eq__(self, other):
        return EqOption(self.option, other)

    def __ne__(self, other):
        return NeOption(self.option, other)

    def __lt__(self, other):
        return LtOption(self.option, other)


class EqOption(BaseRequirement):
    def __init__(self, option, value):
        self.option = option
        self.value = value

    def __str__(self):
        return f"option_eq({self.option}, {self.value})"


class NeOption(BaseRequirement):
    def __init__(self, option, value):
        self.option = option
        self.value = value

    def __str__(self):
        return f"option_ne({self.option}, {self.value})"


class LtOption(BaseRequirement):
    def __init__(self, option, value):
        self.option = option
        self.value = value

    def __str__(self):
        return f"option_lt({self.option}, {self.value})"


def mock_has(self, item, _player, count=1):
    return ItemCountRequirement(item, count)


def mock_can_reach_region(self, spot, _player):
    return CanReachRegionRequirement(spot)


class MockOptions:
    def __getattr__(self, name):
        return BaseOption(name)


class SSTestBase(WorldTestBase):
    game = "Skyward Sword"
    player: int = 1


class TestHackyExportLogic(SSTestBase):
    options = {
        "required_dungeon_count": 6,
        "treasuresanity_in_silent_realms": True,
        "trial_treasure_amount": 10,
        "empty_unrequired_dungeons": False,
    }

    def test_export_logic(self):
        state = self.multiworld.state
        state.__class__.has = mock_has
        state.__class__.can_reach_region = mock_can_reach_region
        for location in self.multiworld.get_locations(self.player):
            self.multiworld.worlds[self.player].options = MockOptions()
            print(location.name, "->", str(location.access_rule(state)))
