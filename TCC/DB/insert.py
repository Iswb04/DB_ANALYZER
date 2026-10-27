from TCC.DB.create import criar_banco
from TCC.DB.itens import inserir_item

criar_banco()

dados = [
    # Notebooks 
    ("Notebook", 3700, "Dell", "Inspiron 15", 12),
    ("Notebook", 4500, "Lenovo", "ThinkPad E14", 8),
    ("Notebook", 5800, "Apple", "MacBook Air M1", 5),
    ("Notebook", 3200, "Acer", "Aspire 5", 15),
    ("Notebook", 4900, "Asus", "Vivobook 16", 7),

    # Mouses 
    ("Mouse", 140, "Logitech", "G203 Prodigy", 45),
    ("Mouse", 90, "Redragon", "Cobra M711", 60),
    ("Mouse", 320, "Razer", "DeathAdder V2", 20),
    ("Mouse", 75, "Multilaser", "Classic Box", 100),
    ("Mouse", 190, "Corsair", "Harpoon Pro", 25),

    # Teclados 
    ("Teclado", 280, "Razer", "Cynosa V2", 18),
    ("Teclado", 170, "Logitech", "K120", 35),
    ("Teclado", 220, "Redragon", "Kumara K552", 40),
    ("Teclado", 450, "Corsair", "K55 RGB", 12),

    # Monitores 
    ("Monitor", 950, "LG", "24MK430H", 22),
    ("Monitor", 1300, "Samsung", "T350 27\"", 15),
    ("Monitor", 850, "AOC", "24B1XHS", 30),
    ("Monitor", 1600, "Dell", "P2422H", 10),

    # Headsets 
    ("Headset", 320, "HyperX", "Cloud Stinger 2", 28),
    ("Headset", 195, "JBL", "Quantum 100", 40),
    ("Headset", 150, "Redragon", "Scylla H901", 50),
    ("Headset", 600, "SteelSeries", "Arctis Nova 1", 8),

    # Celulares
    ("Celular", 2300, "Samsung", "Galaxy A55", 14),
    ("Celular", 1900, "Motorola", "Moto G84", 20),
    ("Celular", 4800, "Apple", "iPhone 13", 9),
    ("Celular", 1600, "Xiaomi", "Redmi Note 13", 35),
    ("Celular", 2900, "Realme", "12 Pro Plus", 15),

    # Carregadores 
    ("Carregador", 85, "Anker", "PowerPort 20W", 80),
    ("Carregador", 65, "Baseus", "Super Si 20W", 95),
    ("Carregador", 120, "Samsung", "Super Fast 25W", 40),
    ("Carregador", 150, "Apple", "USB-C 20W", 30),

    # HDs Externos 
    ("HD Externo", 420, "Seagate", "Expansion 1TB", 25),
    ("HD Externo", 460, "WD Elements", "Portable 1TB", 20),
    ("HD Externo", 390, "Toshiba", "Canvio Basics", 15),

    # Caixas de Som 
    ("Caixa de Som", 380, "JBL", "Go 4", 30),
    ("Caixa de Som", 130, "Xiaomi", "Pocket Speaker", 45),
    ("Caixa de Som", 250, "Edifier", "X100B", 18),

    # Webcams 
    ("Webcam", 220, "Redragon", "Fobos GW600", 35),
    ("Webcam", 480, "Logitech", "C920s Pro", 22),
    ("Webcam", 180, "Intelbras", "CAM-720p", 40)
]

for item in dados:
    inserir_item(*item)
