"""All on-screen text in English, Spanish and French.  t("key") returns the text in the chosen language."""

LANGS = {"English": "en", "Español": "es", "Français": "fr"}
SPEECH_CODE = {"en": "en-US", "es": "es-ES", "fr": "fr-FR"}

S = {
    "tagline": {"en": "Traffic-aware delivery planning · capacity + time slots",
                "es": "Planificación de entregas según el tráfico · capacidad + franjas horarias",
                "fr": "Planification des livraisons selon le trafic · capacité + créneaux"},
    "pill_traffic": {"en": "Chicago traffic 2026", "es": "Tráfico de Chicago 2026", "fr": "Trafic de Chicago 2026"},
    "pill_roads": {"en": "OpenStreetMap roads", "es": "Calles de OpenStreetMap", "fr": "Routes OpenStreetMap"},
    "pill_opt": {"en": "OR-Tools optimizer", "es": "Optimizador OR-Tools", "fr": "Optimiseur OR-Tools"},
    # tabs
    "tab_plan": {"en": "Live plan", "es": "Plan en vivo", "fr": "Plan en direct"},
    "tab_replay": {"en": "▶ Replay the day", "es": "▶ Repetir el día", "fr": "▶ Rejouer la journée"},
    "tab_driver": {"en": "Driver directions", "es": "Indicaciones", "fr": "Itinéraire chauffeur"},
    "tab_whatif": {"en": "What if?", "es": "¿Y si…?", "fr": "Et si… ?"},
    "tab_traffic": {"en": "Traffic data", "es": "Datos de tráfico", "fr": "Données de trafic"},
    "tab_about": {"en": "How it works", "es": "Cómo funciona", "fr": "Fonctionnement"},
    # sidebar
    "language": {"en": "Language", "es": "Idioma", "fr": "Langue"},
    "theme": {"en": "Appearance", "es": "Apariencia", "fr": "Apparence"},
    "dark": {"en": "Dark", "es": "Oscuro", "fr": "Sombre"},
    "light": {"en": "Light", "es": "Claro", "fr": "Clair"},
    "intro_tag": {"en": "Your everyday delivery co-pilot", "es": "Tu copiloto de reparto de cada día",
                  "fr": "Votre copilote de livraison au quotidien"},
    "intro_load": {"en": "Loading real roads and Chicago traffic…", "es": "Cargando calles reales y tráfico de Chicago…",
                   "fr": "Chargement des routes et du trafic de Chicago…"},
    "shift": {"en": "Shift", "es": "Turno", "fr": "Service"},
    "day": {"en": "Day", "es": "Día", "fr": "Jour"},
    "start_hour": {"en": "Start hour", "es": "Hora de inicio", "fr": "Heure de début"},
    "drivers_work": {"en": "Drivers work {a}:00 – {b}:00", "es": "Los conductores trabajan de {a}:00 a {b}:00",
                     "fr": "Les chauffeurs travaillent de {a}h à {b}h"},
    "fleet": {"en": "Fleet", "es": "Flota", "fr": "Flotte"},
    "trucks": {"en": "Trucks", "es": "Camiones", "fr": "Camions"},
    "capacity": {"en": "Packages per truck", "es": "Paquetes por camión", "fr": "Colis par camion"},
    "van_cost": {"en": "Cost per van used ($/day)", "es": "Coste por furgoneta usada ($/día)",
                 "fr": "Coût par camion utilisé ($/jour)"},
    "van_cost_help": {"en": "Rental, insurance and the driver's minimum shift. Higher = fewer, longer routes.",
                      "es": "Alquiler, seguro y turno mínimo del conductor. Más alto = menos rutas, más largas.",
                      "fr": "Location, assurance et service minimum du chauffeur. Plus élevé = moins de trajets, plus longs."},
    "chaos": {"en": "Chaos mode", "es": "Modo caos", "fr": "Mode chaos"},
    "jam": {"en": "Traffic jam (% slower)", "es": "Atasco (% más lento)", "fr": "Embouteillage (% plus lent)"},
    "breakdown": {"en": "A truck breaks down", "es": "Un camión se avería", "fr": "Un camion tombe en panne"},
    "urgent": {"en": "Urgent order (3 packages, 12–14h)", "es": "Pedido urgente (3 paquetes, 12–14h)",
               "fr": "Commande urgente (3 colis, 12h–14h)"},
    "map": {"en": "Map", "es": "Mapa", "fr": "Carte"},
    "show_naive": {"en": "Show simple method's routes", "es": "Ver rutas del método simple",
                   "fr": "Voir les trajets de la méthode simple"},
    "access": {"en": "Accessibility", "es": "Accesibilidad", "fr": "Accessibilité"},
    "big_text": {"en": "Larger text", "es": "Texto más grande", "fr": "Texte plus grand"},
    "contrast": {"en": "High contrast", "es": "Alto contraste", "fr": "Contraste élevé"},
    "cb_colors": {"en": "Colour-blind-safe colours", "es": "Colores aptos para daltonismo",
                  "fr": "Couleurs adaptées au daltonisme"},
    "calm": {"en": "Reduce motion", "es": "Reducir movimiento", "fr": "Réduire les animations"},
    # deliveries input
    "sample": {"en": "Sample day · Chicago · 40 stops", "es": "Día de ejemplo · Chicago · 40 paradas",
               "fr": "Journée exemple · Chicago · 40 arrêts"},
    "own": {"en": "My own addresses", "es": "Mis direcciones", "fr": "Mes adresses"},
    "depot_addr": {"en": "Depot address", "es": "Dirección del almacén", "fr": "Adresse du dépôt"},
    "use_location": {"en": "📍 Use my location", "es": "📍 Usar mi ubicación", "fr": "📍 Ma position"},
    "located": {"en": "Location found", "es": "Ubicación encontrada", "fr": "Position trouvée"},
    "deliveries_help": {"en": "Deliveries — one per line:  address | packages | time slot",
                        "es": "Entregas — una por línea:  dirección | paquetes | franja horaria",
                        "fr": "Livraisons — une par ligne :  adresse | colis | créneau"},
    "voice": {"en": "🎙️ Speak an address", "es": "🎙️ Dictar una dirección", "fr": "🎙️ Dicter une adresse"},
    "voice_stop": {"en": "⏹ Stop", "es": "⏹ Parar", "fr": "⏹ Arrêter"},
    "heard": {"en": "Heard: “{x}” — added to the list", "es": "Escuché: «{x}» — añadido a la lista",
              "fr": "Entendu : « {x} » — ajouté à la liste"},
    "find": {"en": "Find addresses", "es": "Buscar direcciones", "fr": "Chercher les adresses"},
    "type_hint": {"en": "Type or speak your addresses, then press **Find addresses**.",
                  "es": "Escribe o dicta tus direcciones y pulsa **Buscar direcciones**.",
                  "fr": "Tapez ou dictez vos adresses puis appuyez sur **Chercher les adresses**."},
    "looking_up": {"en": "Looking up addresses…", "es": "Buscando direcciones…", "fr": "Recherche des adresses…"},
    "no_depot": {"en": "Couldn't find the depot address.", "es": "No se encontró el almacén.",
                 "fr": "Adresse du dépôt introuvable."},
    "skipped_addr": {"en": "Skipped (not found or bad format): {x}", "es": "Omitida (no encontrada o formato incorrecto): {x}",
                     "fr": "Ignorée (introuvable ou mal écrite) : {x}"},
    "optimizing": {"en": "Optimizing routes…", "es": "Optimizando rutas…", "fr": "Optimisation des trajets…"},
    # KPIs
    "saved": {"en": "Saved today vs simple routing", "es": "Ahorro hoy vs. ruta simple", "fr": "Économie du jour vs méthode simple"},
    "instead": {"en": "${a} instead of ${b} — fuel + driver pay", "es": "${a} en vez de ${b} — combustible + conductores",
                "fr": "{a} $ au lieu de {b} $ — carburant + salaires"},
    "on_time": {"en": "On time", "es": "A tiempo", "fr": "À l'heure"},
    "distance": {"en": "Distance", "es": "Distancia", "fr": "Distance"},
    "driver_hours": {"en": "Driver hours", "es": "Horas de conductor", "fr": "Heures chauffeur"},
    "delivered": {"en": "Delivered", "es": "Entregados", "fr": "Livrés"},
    "vs_simple": {"en": "vs simple", "es": "vs. simple", "fr": "vs simple"},
    "same": {"en": "same as simple method", "es": "igual que el método simple", "fr": "comme la méthode simple"},
    "fleet_panel": {"en": "Fleet · {n} trucks", "es": "Flota · {n} camiones", "fr": "Flotte · {n} camions"},
    "stops": {"en": "stops", "es": "paradas", "fr": "arrêts"},
    "pkgs": {"en": "pkgs", "es": "paq.", "fr": "colis"},
    "truck": {"en": "Truck", "es": "Camión", "fr": "Camion"},
    "missed": {"en": "<b>{n} deliveries can't make their time slot</b> with {t} trucks (red dots). Add a truck or bigger trucks to fix it.",
               "es": "<b>{n} entregas no llegan a su franja horaria</b> con {t} camiones (puntos rojos). Añade un camión o camiones más grandes.",
               "fr": "<b>{n} livraisons ne tiennent pas leur créneau</b> avec {t} camions (points rouges). Ajoutez un camion ou des camions plus grands."},
    "plan_caption": {"en": "SwiftRoute plan", "es": "Plan de SwiftRoute", "fr": "Plan SwiftRoute"},
    "naive_caption": {"en": "Simple “nearest stop next” routes", "es": "Rutas simples «parada más cercana»",
                      "fr": "Trajets simples « arrêt le plus proche »"},
    "speed_caption": {"en": "road speed this shift {p} of free-flow", "es": "velocidad en este turno {p} del flujo libre",
                      "fr": "vitesse pendant ce service {p} du trafic fluide"},
    "fit": {"en": "⌂ Show all routes", "es": "⌂ Ver todas las rutas", "fr": "⌂ Voir tous les trajets"},
    "fit_help": {"en": "Zoom the map back out to fit every route", "es": "Vuelve a encuadrar todas las rutas",
                 "fr": "Recadrer la carte sur tous les trajets"},
    "read_aloud": {"en": "🔊 Read summary aloud", "es": "🔊 Leer resumen en voz alta", "fr": "🔊 Lire le résumé"},
    "summary": {"en": "SwiftRoute plan for {d}. {t} trucks deliver {del} packages stops. {o} percent on time. Cost {c} dollars, saving {s} dollars, {p} percent, compared with simple routing.",
                "es": "Plan de SwiftRoute para el {d}. {t} camiones hacen {del} entregas. {o} por ciento a tiempo. Coste {c} dólares, un ahorro de {s} dólares, {p} por ciento, frente a la ruta simple.",
                "fr": "Plan SwiftRoute pour {d}. {t} camions font {del} livraisons. {o} pour cent à l'heure. Coût {c} dollars, soit {s} dollars d'économie, {p} pour cent, par rapport à la méthode simple."},
    "schedules": {"en": "Driver schedules", "es": "Horarios de conductores", "fr": "Horaires des chauffeurs"},
    "download_plan": {"en": "Download all schedules (CSV)", "es": "Descargar horarios (CSV)", "fr": "Télécharger les horaires (CSV)"},
    "col_stop": {"en": "Stop", "es": "Parada", "fr": "Arrêt"},
    "col_arrives": {"en": "Arrives", "es": "Llega", "fr": "Arrivée"},
    "col_slot": {"en": "Time slot", "es": "Franja", "fr": "Créneau"},
    "col_status": {"en": "Status", "es": "Estado", "fr": "Statut"},
    "col_pk": {"en": "Packages", "es": "Paquetes", "fr": "Colis"},
    "ontime_s": {"en": "On time", "es": "A tiempo", "fr": "À l'heure"},
    "late_s": {"en": "Late", "es": "Tarde", "fr": "En retard"},
    "depot": {"en": "Depot", "es": "Almacén", "fr": "Dépôt"},
    "map_alt": {"en": "Map of {n} delivery routes in Chicago. Full stop list is in the Driver schedules table below.",
                "es": "Mapa de {n} rutas de entrega en Chicago. La lista completa está en la tabla de horarios.",
                "fr": "Carte de {n} trajets de livraison à Chicago. La liste complète est dans le tableau des horaires."},
    # replay
    "replay_title": {"en": "Watch the whole day in 30 seconds", "es": "Mira el día entero en 30 segundos",
                     "fr": "Toute la journée en 30 secondes"},
    "replay_help": {"en": "Every truck drives its real street route at the speed real April-2026 Chicago traffic allows. Stops turn green when delivered.",
                    "es": "Cada camión recorre su ruta real a la velocidad que permite el tráfico real de Chicago (abril 2026). Las paradas se ponen verdes al entregarse.",
                    "fr": "Chaque camion suit son vrai trajet à la vitesse permise par le trafic réel de Chicago (avril 2026). Les arrêts deviennent verts une fois livrés."},
    "play": {"en": "Play", "es": "Reproducir", "fr": "Lecture"},
    "pause": {"en": "Pause", "es": "Pausa", "fr": "Pause"},
    "speed": {"en": "Speed", "es": "Velocidad", "fr": "Vitesse"},
    # driver directions
    "pick_truck": {"en": "Choose a driver", "es": "Elige un conductor", "fr": "Choisir un chauffeur"},
    "open_gmaps": {"en": "Open this route in Google Maps", "es": "Abrir la ruta en Google Maps", "fr": "Ouvrir dans Google Maps"},
    "gmaps_note": {"en": "Google Maps links hold up to 9 stops, so long routes are split into parts.",
                   "es": "Los enlaces de Google Maps admiten 9 paradas; las rutas largas se dividen.",
                   "fr": "Les liens Google Maps acceptent 9 arrêts ; les longs trajets sont découpés."},
    "part": {"en": "Part", "es": "Parte", "fr": "Partie"},
    "stop_n": {"en": "Stop {n}", "es": "Parada {n}", "fr": "Arrêt {n}"},
    "arrive_at": {"en": "arrive {t}", "es": "llegada {t}", "fr": "arrivée {t}"},
    "offline_dir": {"en": "Turn-by-turn directions need an internet connection.",
                    "es": "Las indicaciones necesitan conexión a internet.",
                    "fr": "L'itinéraire détaillé nécessite une connexion internet."},
    # what-if / traffic / about
    "whatif_title": {"en": "What happens to cost and service when things change?",
                     "es": "¿Qué pasa con el coste y el servicio cuando algo cambia?",
                     "fr": "Que deviennent coût et service quand tout change ?"},
    "whatif_help": {"en": "Six scenarios on the sample Chicago day, each planned by SwiftRoute and by the simple method. ~1 minute.",
                    "es": "Seis escenarios del día de ejemplo, planificados con SwiftRoute y con el método simple. ~1 minuto.",
                    "fr": "Six scénarios sur la journée exemple, planifiés par SwiftRoute et par la méthode simple. ~1 minute."},
    "run_scen": {"en": "Run scenarios", "es": "Ejecutar escenarios", "fr": "Lancer les scénarios"},
    "download_scen": {"en": "Download scenarios (CSV)", "es": "Descargar escenarios (CSV)", "fr": "Télécharger les scénarios (CSV)"},
    "traffic_title": {"en": "When are Chicago's roads slow?", "es": "¿Cuándo van lentas las calles de Chicago?",
                      "fr": "Quand les rues de Chicago sont-elles lentes ?"},
    "traffic_cap": {"en": "Each road segment's speed as % of its own free-flow speed, averaged over all segments",
                    "es": "Velocidad de cada tramo como % de su velocidad en flujo libre, promediada en todos los tramos",
                    "fr": "Vitesse de chaque tronçon en % de sa vitesse fluide, moyenne sur tous les tronçons"},
    "readings": {"en": "Speed readings", "es": "Lecturas de velocidad", "fr": "Mesures de vitesse"},
    "segments": {"en": "Road segments", "es": "Tramos de calle", "fr": "Tronçons"},
    "period": {"en": "Period", "es": "Periodo", "fr": "Période"},
    "hour_of_day": {"en": "Hour of day", "es": "Hora del día", "fr": "Heure"},
    "traffic_note": {"en": "Blue = free-flowing · red = rush hour. Every drive is slowed by the value for the hour it happens in.",
                     "es": "Azul = fluido · rojo = hora punta. Cada trayecto se ralentiza según la hora en que ocurre.",
                     "fr": "Bleu = fluide · rouge = heure de pointe. Chaque trajet est ralenti selon l'heure."},
}

DAYS = {"en": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "es": ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
        "fr": ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]}

SCENARIOS = {
    "Normal day (40 stops, 4 trucks, leave 9am)": {"es": "Día normal (40 paradas, 4 camiones)", "fr": "Journée normale (40 arrêts, 4 camions)"},
    "+1 truck": {"es": "+1 camión", "fr": "+1 camion"},
    "Traffic 30% worse": {"es": "Tráfico 30% peor", "fr": "Trafic 30 % pire"},
    "Bigger trucks (25 packages)": {"es": "Camiones más grandes (25 paquetes)", "fr": "Camions plus grands (25 colis)"},
    "Orders double (80 stops)": {"es": "Pedidos el doble (80 paradas)", "fr": "Commandes doublées (80 arrêts)"},
    "Orders double + 4 more trucks": {"es": "Pedidos el doble + 4 camiones", "fr": "Commandes doublées + 4 camions"},
}

# ---- turn-by-turn phrases
MOD = {"en": {"left": "left", "right": "right", "slight left": "slight left", "slight right": "slight right",
              "sharp left": "sharp left", "sharp right": "sharp right", "straight": "straight", "uturn": "U-turn"},
       "es": {"left": "a la izquierda", "right": "a la derecha", "slight left": "ligeramente a la izquierda",
              "slight right": "ligeramente a la derecha", "sharp left": "fuerte a la izquierda",
              "sharp right": "fuerte a la derecha", "straight": "recto", "uturn": "cambio de sentido"},
       "fr": {"left": "à gauche", "right": "à droite", "slight left": "légèrement à gauche",
              "slight right": "légèrement à droite", "sharp left": "franchement à gauche",
              "sharp right": "franchement à droite", "straight": "tout droit", "uturn": "demi-tour"}}
ICON = {"left": "↰", "right": "↱", "slight left": "↖", "slight right": "↗", "sharp left": "↰", "sharp right": "↱",
        "straight": "↑", "uturn": "↶"}


def step_text(step, lang):
    typ, mod, name = step["type"], step["modifier"], step["name"]
    m = MOD[lang].get(mod, mod)
    on = {"en": f" onto {name}", "es": f" hacia {name}", "fr": f" sur {name}"}[lang] if name else ""
    if typ == "depart":
        return {"en": f"Head out{on}", "es": f"Sal{on}", "fr": f"Partez{on}"}[lang]
    if typ == "arrive":
        return {"en": "Arrive at the stop", "es": "Llegas a la parada", "fr": "Vous êtes arrivé à l'arrêt"}[lang]
    if typ in ("roundabout", "rotary"):
        ex = step.get("exit") or 1
        return {"en": f"At the roundabout, take exit {ex}{on}", "es": f"En la rotonda, toma la salida {ex}{on}",
                "fr": f"Au rond-point, prenez la sortie {ex}{on}"}[lang]
    if mod == "straight" or typ in ("new name", "continue"):
        return {"en": f"Continue{on}", "es": f"Continúa{on}", "fr": f"Continuez{on}"}[lang]
    if typ in ("merge", "on ramp", "off ramp", "fork"):
        return {"en": f"Keep {m}{on}", "es": f"Mantente {m}{on}", "fr": f"Restez {m}{on}"}[lang]
    return {"en": f"Turn {m}{on}", "es": f"Gira {m}{on}", "fr": f"Tournez {m}{on}"}[lang]


class T:
    def __init__(self, lang):
        self.lang = lang

    def __call__(self, key, **kw):
        s = S[key].get(self.lang) or S[key]["en"]
        return s.format(**kw) if kw else s

    def scenario(self, name):
        return SCENARIOS.get(name, {}).get(self.lang, name)
