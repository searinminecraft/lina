import json

def addonid_toname(x: str):
    with open('data/addons.json', 'r') as f:
        data = json.load(f)

    x = x.removeprefix('addon_')

    match x:
        case 'abyss': return 'Abyss'
        case 'alien_signal': return 'Alien Signal'
        case 'ancient_colosseum_labrynth': return 'Ancient Colosseum Labrynth'
        case 'arena_candela_city': return 'Candela City'
        case 'battleisland': return 'Battle Island'
        case 'black_forest': return 'Black Forest'
        case 'candela_city': return 'Candela City'
        case 'cave': return 'Cave X'
        case 'cocoa_temple': return 'Cocoa Temple'
        case 'cornfield_crossing': return 'Cornfield Crossing'
        case 'endcutscene': return 'What the fuck?'
        case 'featunlock': return 'lina is the best!!'
        case 'fortmagma': return 'Fort Magma'
        case 'gplose': return 'You lost? Too bad.'
        case 'gpwin': return 'Huh?'
        case 'gran_paradiso_island': return 'Gran Paradiso Island'
        case 'hacienda': return 'Hacienda'
        case 'hole_drop': return 'Hole Drop'
        case 'icy_soccer_field': return 'Icy Soccer Field'
        case 'introcutscene': return 'Intro Cutscene'
        case 'introcutscene2': return 'Intro Cutscene (Part 2)'
        case 'lasdunasarena': return 'Las Dunas Arena'
        case 'lighthouse': return 'Around the Lighthouse'
        case 'mines': return 'Old Mine'
        case 'minigolf': return 'Minigolf'
        case 'oasis': return 'Oasis'
        case 'olivermath': return 'Oliver\'s Math Class'
        case 'overworld': return 'Overworld'
        case 'pumpkin_park': return 'Pumpkin Park'
        case 'ravenbridge_mansion': return 'Ravenbridge Mansion'
        case 'sandtrack': return 'Shifting Sands'
        case 'scotland': return 'Nessie\'s Pond'
        case 'snowmountain': return 'Northern Resort'
        case 'snowtuxpeak': return 'Snow Peak'
        case 'soccer_field': return 'Soccer Field'
        case 'stadium': return 'The Stadium'
        case 'stk_enterprise': return 'STK Enterprise'
        case 'temple': return 'Temple'
        case 'tutorial': return 'Tutorial'
        case 'volcano_island': return 'Volcan Island'
        case 'xr591': return 'XR591'
        case 'zengarden': return 'Zen Garden'
        case _: pass

    try:
        return data[x]['name']
    except KeyError:
        if x == '':
            return 'None'
        else:
            return f'Unknown track (ID: `{x}`)'
