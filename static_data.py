color_mapping = {
    'opak blau (obla)': '#0000FF',
    'opak gelb (ogel)': '#FFFF00',
    'opak grün (ogru)': '#00FF00',
    'opak hellblau (ohbl)': '#ADD8E6',
    'opak inkarnat (oink)': '#FFC0CB',
    'opak rot (orot)': '#FF0000',
    'opak türkis (otue)': '#40E0D0',
    'opak weiß (owei)': '#FFFFFF',
    '(semi)transparent dunkelblau (tdbl)': '#00008B',
    'transparent blau (tbla)': '#0000FF',
    'transparent braun (tbra)': '#A52A2A',
    'transparent grün (tgru)': '#00FF00',
    'transparent hellgrün (thgr)': '#90EE90',
    'transparent dunkelgrün (tdgr)': '#006400',
    'transparent schwarz (tsch)': '#000000',
    'transparent türkis (ttue)': '#40E0D0'
}

color_columns = [
    'opak blau (obla)', 'opak gelb (ogel)', 'opak grün (ogru)', 
    'opak hellblau (ohbl)', 'opak inkarnat (oink)', 'opak rot (orot)', 
    'opak türkis (otue)', 'opak weiß (owei)', '(semi)transparent dunkelblau (tdbl)', 
    'transparent blau (tbla)', 'transparent braun (tbra)', 'transparent grün (tgru)', 
    'transparent hellgrün (thgr)', 'transparent dunkelgrün (tdgr)', 
    'transparent schwarz (tsch)', 'transparent türkis (ttue)'
]

damage_columns = [
    'Anhaftungen:', 'Anhaftungen: Beschreibung', 'Eingriff:', 'Eingriff: Beschreibung', 'Eingriff: Inventarnummer',
    'Fehlstellen:', 'Fehlstellen: Beschreibung', 'Haftungsverlust:', 'Haftungsverlust: Beschreibung', 'Kratzer:', 
    'Kratzer: Beschreibung', 'kristalline Ausblühungen:', 'kristalline Ausblühungen: Beschreibung', 'Riss/Bruch:', 
    'Riss/Bruch: Beschreibung', 'Riss/Bruch: Häufigkeit', 'Sonstiges Zustand:', 'Trübung der Oberfläche:', 
    'Trübung der Oberfläche: Beschreibung'
]

table_columns = [
    "ObjectID", "ObjectNumber", "ObjectName", "Dated",
    "DateBegin", "DateEnd", "Medium", "Dimensions",
    "Description", "Notes", "ShortText8", "Bestandteil"
]

unique_categories = {
    'opak blau (obla)': 'Opak Blau',
    'opak gelb (ogel)': 'Opak Gelb',
    'opak grün (ogru)': 'Opak Grün',
    'opak hellblau (ohbl)': 'Opak Hellblau',
    'opak inkarnat (oink)': 'Opak Inkarnat',
    'opak rot (orot)': 'Opak Rot',
    'opak türkis (otue)': 'Opak Türkis',
    'opak weiß (owei)': 'Opak Weiß',
    '(semi)transparent dunkelblau (tdbl)': 'Transparent Dunkelblau',
    'transparent blau (tbla)': 'Transparent Blau',
    'transparent braun (tbra)': 'Transparent Braun',
    'transparent grün (tgru)': 'Transparent Grün',
    'transparent hellgrün (thgr)': 'Transparent Hellgrün',
    'transparent dunkelgrün (tdgr)': 'Transparent Dunkelgrün',
    'transparent schwarz (tsch)': 'Transparent Schwarz',
    'transparent türkis (ttue)': 'Transparent Türkis'
}


settings_columns = {
    'Claw setting': [
        '1. Perldrahtring: Äquatorlinie', '1. Perldrahtring: Drahtdurchmesser',
        '2. Perldrahtring: Äquatorlinie', '2. Perldrahtring: Drahtdurchmesser',
        '3. Perldrahtring: Äquatorlinie', '3. Perldrahtring: Drahtdurchmesser',
        'Granalien mit Perldrahtringen: Durchmesser', 'Granalien: Abstand zwischen Granalien',
        'Granalien: Anzahl', 'Granalien: Anzahl zwischen Krallen', 'Granalien: Durchmesser',
        'Herstellungsprozess: Besonderheiten', 'Krallen: Anzahl', 'Krallen: Breite',
        'Krallen: Länge (ab Schaft)', 'Krallen: Sonstiges', 'Löttechnik: Sonstiges',
        'Öffnung in Grundplatte', 'Öffnung: entspricht Fassungsform', 'Öffnung: Sonstiges',
        'Perldraht: Sonstiges', 'Röhrchen: Abstand zwischen Röhrchen', 'Röhrchen: Anzahl',
        'Röhrchen: Blechstärke', 'Röhrchen: Durchmesser', 'Röhrchen: Höhe', 'Röhrchen: Sonstiges',
        'Schlaufen: Sonstiges', 'Technischer Aufbau: Sonstiges'
    ],
    'Setting with three pearls': [
        '1. Perldrahtring: Äquatorlinie', '1. Perldrahtring: Drahtdurchmesser',
        '2. Perldrahtring: Äquatorlinie', '2. Perldrahtring: Drahtdurchmesser',
        'bügelförmige Klammern: Durchmesser', 'bügelförmige Klammern: Querschnitt',
        'bügelförmige Klammern: Sonstiges', 'Herstellungsprozess: Besonderheiten',
        'Loch: auf Rückseite umsäumt mit Perldraht', 'Loch: Durchmesser', 'Loch: Sonstiges',
        'Loch: umsäumt mit Perldraht', 'Löttechnik: Sonstiges', 'Montageröhrchen',
        'Montageröhrchen: Sonstiges', 'Montageröhrchen: steckt in Loch', 'Perldraht: Sonstiges',
        'Röhrchen: Anzahl', 'Röhrchen: Blechstärke', 'Röhrchen: Durchmesser', 'Röhrchen: Höhe',
        'Röhrchen: Sonstiges', 'Splinte: Durchmesser', 'Splinte: Querschnitt', 'Splinte: Sonstiges',
        'Splintkopf: Kugelpyramide', 'Splintkopf: Kugelpyramide: Durchmesser', 'Splintkopf: Kugelpyramide: Sonstiges',
        'Technischer Aufbau: Sonstiges'
    ],
    'Bezel setting': [
        'Form', 'Herstellungsprozess: Besonderheiten', 'Löttechnik: Sonstiges',
        'Perldraht: Äquatorlinie', 'Perldraht: Beschreibung', 'Perldraht: Drahtdurchmesser',
        'Stein/Perle hinterlegt', 'Stein/Perle hinterlegt: Beschreibung', 'Technischer Aufbau: Sonstiges',
        'Zarge in Bohrung von Stein/Perle gedrückt', 'Zargenblech: Fuge', 'Zargenblech: Höhe', 'Zargenblech: Stärke'
    ],
    'Prong setting': [
        '1. Perldrahtring: Äquatorlinie', '1. Perldrahtring: Drahtdurchmesser',
        '2. Perldrahtring: Äquatorlinie', '2. Perldrahtring: Drahtdurchmesser', 'Form',
        'Herstellungsprozess: Besonderheiten', 'Krappen: Anzahl', 'Krappen: aus Röhrchen',
        'Krappen: ein Band auf 2. Perldrahtring', 'Krappen: gekreuzte Bänder auf 2. Perldrahtring',
        'Krappen: Querschnitt', 'Krappen: Sonstiges', 'Löttechnik: Sonstiges', 'Öffnung in Grundplatte',
        'Öffnung: entspricht Fassungsform', 'Öffnung: Sonstiges', 'Perldraht: Sonstiges',
        'Röhrchen: Abstand zwischen Röhrchen', 'Röhrchen: Anzahl', 'Röhrchen: Blechstärke',
        'Röhrchen: Durchmesser', 'Röhrchen: Höhe', 'Röhrchen: Sonstiges', 'Technischer Aufbau: Sonstiges'
    ],
    'Setting on the central cross': [
        '1. Perldraht an Zarge: Durchmesser', '2. Perldraht an Zarge: Durchmesser', '3. Perldrahtring',
        '3. Perldrahtring: Äquatorlinie', '3. Perldrahtring: Drahtdurchmesser', '3. Perldrahtring: Sonstiges',
        'Arkadenfiligran: Filigrandraht: Beschreibung', 'Arkadenfiligran: Kapitelle: Drahtdurchmesser',
        'Arkadenfiligran: Kapitelle: Querschnitt', 'Arkadenfiligran: Sonstiges', 'Einsteckstifte: Durchmesser',
        'Einsteckstifte: Montage', 'Einsteckstifte: Sonstiges', 'Fassungszarge: Höhe (ab 2. Perldraht)',
        'Fassungszarge: Sonstiges', 'Form', 'Granalien: Abstand zwischen Granalien', 'Granalien: Anzahl',
        'Granalien: Durchmesser', 'Herstellungsprozess: Besonderheiten', 'Krallen: Anzahl', 'Krallen: Breite',
        'Krallen: Länge (ab Schaft)', 'Krallen: Sonstiges', 'Löttechnik: Sonstiges', 'Montagehalterung Stein/Perle',
        'Perldrähte an Zarge: Äquatorlinie', 'Perldrähte an Zarge: Sonstiges', 'runde Durchbrüche: Anzahl',
        'runde Durchbrüche: Filigrandrahtumsäumung: Beschreibung', 'runde Durchbrüche: Innendurchmesser',
        'runde Durchbrüche: Sonstiges', 'Technischer Aufbau: Sonstiges', 'Zarge: Fuge', 'Zarge: Stärke'
    ],
    'Pearl setting': [
        '1. Einsteckstift: aus Röhrchen', '1. Perldrahtring: Äquatorlinie', '1. Perldrahtring: Drahtdurchmesser',
        '2. Einsteckstift auf 1. Perldrahtring', '2. Einsteckstift: aus Röhrchen', '2. Perldrahtring: Äquatorlinie',
        '2. Perldrahtring: Drahtdurchmesser', 'Einsteckstift am 2. Perldrahtring', 'Einsteckstift: Durchmesser',
        'Einsteckstift: Sonstiges', 'Herstellungsprozess: Besonderheiten', 'Löttechnik: Sonstiges',
        'Öffnung in Grundplatte', 'Öffnung: entspricht Fassungsform', 'Öffnung: Sonstiges', 'Perldraht: Sonstiges',
        'Röhrchen: Abstand zwischen Röhrchen', 'Röhrchen: Anzahl', 'Röhrchen: Blechstärke', 'Röhrchen: Durchmesser',
        'Röhrchen: Höhe', 'Röhrchen: Sonstiges', 'Technischer Aufbau: Sonstiges'
    ]
}