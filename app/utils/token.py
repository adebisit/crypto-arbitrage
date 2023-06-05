from enum import Enum


class TokenTier(Enum):
    TIER_1 = (1, 100)
    TIER_2 = (101, 500)
    TIER_3 = (501, 1000)
    TIER_4 = (1001, None)

    @classmethod
    def from_amount(cls, amount):
        for tier in cls:
            lower_bound, upper_bound = tier.value
            if upper_bound is None:
                if amount >= lower_bound:
                    return tier
            elif lower_bound <= amount <= upper_bound:
                return tier
        return None
    
    def __str__(self):
        return self.name.replace('_', ' ')


class TokenPricing:
    PRICES = {
        TokenTier.TIER_1: 1.0,
        TokenTier.TIER_2: 0.9,
        TokenTier.TIER_3: 0.8,
        TokenTier.TIER_4: 0.7,
    }

    @classmethod
    def get_price(cls, tier):
        return cls.PRICES.get(tier)
