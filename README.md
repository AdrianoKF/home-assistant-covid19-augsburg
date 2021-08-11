# Home Assistant Augsburg COVID-19 Tracker Integration

## Adding to your dashboard

You can add an overview of the current infection and vaccination numbers to your dashboard
using the [multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row) card:

```yaml
type: entities
entities:
  - type: custom:multiple-entity-row
    entity: sensor.coronavirus_augsburg
    entities:
      - attribute: total_cases
        name: Cases
      - attribute: num_dead
        name: Deaths
      - attribute: num_recovered
        name: Recovered
      - attribute: num_infected
        name: Infected
    show_state: false
    icon: mdi:biohazard
    name: COVID-19
    secondary_info:
      attribute: incidence
      unit: cases/100k
  - type: custom:multiple-entity-row
    entity: sensor.covid_19_vaccinations_augsburg
    entities:
      - attribute: ratio_vaccinated_once
        name: Once
        format: precision1
        unit: '%'
      - attribute: ratio_vaccinated_full
        name: Fully
        format: precision1
        unit: '%'
      - attribute: ratio_vaccinated_total
        name: Total
        format: precision1
        unit: '%'
    show_state: false
    icon: mdi:needle
    name: COVID-19 Vaccinations
    secondary_info:
      attribute: date
      format: date
```
