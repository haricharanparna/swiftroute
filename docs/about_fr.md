#### Fonctionnement
1. **Adresses → points sur la carte** avec OpenStreetMap — tapez-les, dictez-les 🎙️ ou utilisez votre position 📍.
2. **Vraies routes :** distance et temps de trajet sans trafic entre chaque paire d'arrêts (OSRM sur OpenStreetMap).
3. **Vrai trafic :** 2,66 millions de mesures de vitesse sur 1 046 tronçons de Chicago (Chicago Traffic Tracker, avril 2026). Chaque tronçon est comparé à sa propre vitesse fluide : on obtient le ralentissement pour chaque heure de la semaine.
4. **Optimiseur :** Google OR-Tools résout le problème de tournées avec la capacité des camions et les créneaux des clients, en minimisant le coût réel (carburant + salaires). Chaque trajet est ralenti selon l'heure.
5. **Vérification honnête :** chaque tournée — la nôtre et celle de la méthode simple — est rejouée heure par heure avec le vrai trafic. Tous les chiffres viennent de ce rejeu.
6. **Référence :** la même journée planifiée avec « aller à l'arrêt le plus proche », comme beaucoup de petites flottes.

#### Hypothèses
5 min par livraison · 0,60 $/km · 25 $/heure par chauffeur · 0,25 kg de CO₂/km · service de 8 heures.

#### Accessibilité
Focus clavier visible · descriptions de la carte pour lecteurs d'écran · texte plus grand · contraste élevé · couleurs adaptées au daltonisme (Okabe-Ito) · réduction des animations · résumé lu à voix haute · anglais, espagnol, français.
