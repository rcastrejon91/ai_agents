def amplify_spell(spell_fn):
    def wrapper(target):
        result = spell_fn(target)
        return result + " ✨ Spell amplified by WraithForge Core."
    return wrapper
