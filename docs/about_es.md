#### Cómo funciona
1. **Direcciones → puntos del mapa** con OpenStreetMap — escríbelas, díctalas 🎙️ o usa tu ubicación 📍.
2. **Calles reales:** distancia y tiempo de conducción sin tráfico entre cada par de paradas (OSRM sobre OpenStreetMap).
3. **Tráfico real:** 2,66 millones de lecturas de velocidad de 1.046 tramos de Chicago (Chicago Traffic Tracker, abril 2026). Cada tramo se compara con su propia velocidad en flujo libre: así obtenemos la ralentización para cada hora de la semana.
4. **Optimizador:** Google OR-Tools resuelve el problema de rutas con capacidad de los camiones y franjas horarias, minimizando el coste real (combustible + conductores). Cada trayecto se ralentiza según la hora en que ocurre.
5. **Comprobación honesta:** cada ruta — la nuestra y la del método simple — se reproduce hora a hora con el tráfico real. Todas las cifras salen de esa reproducción.
6. **Comparación:** el mismo día planificado con «ir a la parada más cercana», como hacen muchas flotas pequeñas.

#### Supuestos
5 min por entrega · 0,60 $/km · 25 $/hora por conductor · 0,25 kg CO₂/km · turno de 8 horas.

#### Accesibilidad
Foco visible con teclado · descripciones del mapa para lectores de pantalla · texto grande · alto contraste · colores aptos para daltonismo (Okabe-Ito) · reducir movimiento · resumen en voz alta · inglés, español, francés.
